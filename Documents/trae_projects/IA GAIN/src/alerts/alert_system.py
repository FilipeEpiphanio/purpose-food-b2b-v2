import smtplib
import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os
from telegram import Bot
from telegram.error import TelegramError

@dataclass
class AlertMessage:
    """Mensagem de alerta"""
    level: str  # 'info', 'warning', 'error', 'critical'
    title: str
    message: str
    symbol: Optional[str] = None
    timestamp: datetime = None
    additional_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.additional_data is None:
            self.additional_data = {}

@dataclass
class AlertConfig:
    """Configuração de alertas"""
    email_enabled: bool = False
    email_address: str = ""
    email_password: str = ""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    
    discord_enabled: bool = False
    discord_webhook: str = ""
    
    alert_on_large_trades: bool = True
    alert_on_high_volatility: bool = True
    alert_on_significant_price_changes: bool = True
    alert_on_system_errors: bool = True
    
    # Limites para alertas
    large_trade_threshold: float = 1000  # USDT
    volatility_threshold: float = 0.05  # 5%
    price_change_threshold: float = 0.02  # 2%

class AlertSystem:
    """
    Sistema de alertas para o IA GAIN
    """
    
    def __init__(self, config: AlertConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Inicializar clientes
        self.telegram_bot = None
        if self.config.telegram_enabled and self.config.telegram_bot_token:
            try:
                self.telegram_bot = Bot(token=self.config.telegram_bot_token)
            except Exception as e:
                self.logger.error(f"Erro ao inicializar bot do Telegram: {str(e)}")
        
        # Histórico de alertas
        self.alert_history: List[AlertMessage] = []
        self.max_history_size = 1000
        
        # Arquivo de log de alertas
        self.alert_log_file = "alerts.log"
        
        # Limitador de taxa
        self.rate_limiter = RateLimiter()
        
        self.logger.info("Sistema de alertas inicializado")
    
    async def send_alert(self, alert: AlertMessage) -> bool:
        """Enviar alerta por todos os canais configurados"""
        try:
            # Verificar limitador de taxa
            if not self.rate_limiter.can_send(alert.level):
                self.logger.warning(f"Alerta ignorado devido a limite de taxa: {alert.title}")
                return False
            
            # Adicionar ao histórico
            self.add_to_history(alert)
            
            # Salvar no log
            self.save_alert_to_log(alert)
            
            # Enviar por diferentes canais
            tasks = []
            
            if self.config.email_enabled:
                tasks.append(self.send_email_alert(alert))
            
            if self.config.telegram_enabled and self.telegram_bot:
                tasks.append(self.send_telegram_alert(alert))
            
            if self.config.discord_enabled:
                tasks.append(self.send_discord_alert(alert))
            
            # Executar todas as tarefas
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success = any(result is True for result in results)
            else:
                success = False
            
            if success:
                self.logger.info(f"Alerta enviado com sucesso: {alert.title}")
            else:
                self.logger.warning(f"Falha ao enviar alerta: {alert.title}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar alerta: {str(e)}")
            return False
    
    async def send_email_alert(self, alert: AlertMessage) -> bool:
        """Enviar alerta por email"""
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"IA GAIN Alert - {alert.level.upper()}: {alert.title}"
            msg['From'] = self.config.email_address
            msg['To'] = self.config.email_address
            
            # Criar corpo da mensagem
            html_body = self.create_html_email_body(alert)
            text_body = self.create_text_email_body(alert)
            
            # Adicionar partes
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Enviar email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.email_address, self.config.email_password)
                server.send_message(msg)
            
            self.logger.info(f"Email enviado com sucesso: {alert.title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    async def send_telegram_alert(self, alert: AlertMessage) -> bool:
        """Enviar alerta pelo Telegram"""
        try:
            if not self.telegram_bot:
                return False
            
            message = self.create_telegram_message(alert)
            
            await self.telegram_bot.send_message(
                chat_id=self.config.telegram_chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            self.logger.info(f"Telegram enviado com sucesso: {alert.title}")
            return True
            
        except TelegramError as e:
            self.logger.error(f"Erro do Telegram: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao enviar Telegram: {str(e)}")
            return False
    
    async def send_discord_alert(self, alert: AlertMessage) -> bool:
        """Enviar alerta pelo Discord"""
        try:
            embed = self.create_discord_embed(alert)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.discord_webhook,
                    json=embed,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 204:
                        self.logger.info(f"Discord enviado com sucesso: {alert.title}")
                        return True
                    else:
                        self.logger.error(f"Erro ao enviar Discord: Status {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Erro ao enviar Discord: {str(e)}")
            return False
    
    def create_html_email_body(self, alert: AlertMessage) -> str:
        """Criar corpo HTML do email"""
        color_map = {
            'info': '#3498db',
            'warning': '#f39c12',
            'error': '#e74c3c',
            'critical': '#c0392b'
        }
        
        color = color_map.get(alert.level, '#95a5a6')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background-color: {color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .alert-title {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                .alert-level {{ font-size: 14px; opacity: 0.9; }}
                .message {{ margin: 20px 0; line-height: 1.6; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .timestamp {{ color: #666; font-size: 12px; text-align: center; margin-top: 20px; }}
                .symbol {{ background-color: {color}; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="alert-title">{alert.title}</div>
                    <div class="alert-level">{alert.level.upper()}</div>
                </div>
                <div class="content">
                    <div class="message">
                        <p>{alert.message}</p>
                    </div>
                    
                    {f'<div class="symbol">Símbolo: {alert.symbol}</div>' if alert.symbol else ''}
                    
                    {self.create_details_html(alert.additional_data) if alert.additional_data else ''}
                    
                    <div class="timestamp">
                        Enviado em: {alert.timestamp.strftime('%d/%m/%Y %H:%M:%S')}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def create_text_email_body(self, alert: AlertMessage) -> str:
        """Criar corpo de texto do email"""
        text = f"""
IA GAIN Alert - {alert.level.upper()}: {alert.title}

{alert.message}

"""
        
        if alert.symbol:
            text += f"Símbolo: {alert.symbol}\n"
        
        if alert.additional_data:
            text += "\nDetalhes:\n"
            for key, value in alert.additional_data.items():
                text += f"- {key}: {value}\n"
        
        text += f"\nEnviado em: {alert.timestamp.strftime('%d/%m/%Y %H:%M:%S')}"
        
        return text
    
    def create_telegram_message(self, alert: AlertMessage) -> str:
        """Criar mensagem do Telegram"""
        emoji_map = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨'
        }
        
        emoji = emoji_map.get(alert.level, '🔔')
        
        message = f"{emoji} <b>{alert.title}</b>\n\n"
        message += f"{alert.message}\n"
        
        if alert.symbol:
            message += f"\n📊 Símbolo: <code>{alert.symbol}</code>"
        
        if alert.additional_data:
            message += "\n\n<b>Detalhes:</b>"
            for key, value in alert.additional_data.items():
                message += f"\n• <b>{key}:</b> {value}"
        
        message += f"\n\n🕐 {alert.timestamp.strftime('%d/%m/%Y %H:%M:%S')}"
        
        return message
    
    def create_discord_embed(self, alert: AlertMessage) -> Dict:
        """Criar embed do Discord"""
        color_map = {
            'info': 3447003,      # Azul
            'warning': 16776960,  # Amarelo
            'error': 15158332,    # Vermelho
            'critical': 10038562  # Vermelho escuro
        }
        
        color = color_map.get(alert.level, 9807270)
        
        embed = {
            "embeds": [{
                "title": alert.title,
                "description": alert.message,
                "color": color,
                "timestamp": alert.timestamp.isoformat(),
                "fields": [],
                "footer": {
                    "text": "IA GAIN Alert System"
                }
            }]
        }
        
        # Adicionar campos
        if alert.symbol:
            embed["embeds"][0]["fields"].append({
                "name": "Símbolo",
                "value": alert.symbol,
                "inline": True
            })
        
        if alert.additional_data:
            for key, value in alert.additional_data.items():
                embed["embeds"][0]["fields"].append({
                    "name": key,
                    "value": str(value),
                    "inline": True
                })
        
        return embed
    
    def create_details_html(self, additional_data: Dict[str, Any]) -> str:
        """Criar HTML para detalhes adicionais"""
        if not additional_data:
            return ""
        
        html = '<div class="details">'
        html += '<h4>Detalhes:</h4>'
        html += '<ul>'
        
        for key, value in additional_data.items():
            html += f'<li><strong>{key}:</strong> {value}</li>'
        
        html += '</ul>'
        html += '</div>'
        
        return html
    
    def add_to_history(self, alert: AlertMessage):
        """Adicionar alerta ao histórico"""
        self.alert_history.append(alert)
        
        # Limitar tamanho do histórico
        if len(self.alert_history) > self.max_history_size:
            self.alert_history = self.alert_history[-self.max_history_size:]
    
    def save_alert_to_log(self, alert: AlertMessage):
        """Salvar alerta em arquivo de log"""
        try:
            log_entry = {
                'timestamp': alert.timestamp.isoformat(),
                'level': alert.level,
                'title': alert.title,
                'message': alert.message,
                'symbol': alert.symbol,
                'additional_data': alert.additional_data
            }
            
            with open(self.alert_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar alerta no log: {str(e)}")
    
    def get_alert_history(self, limit: int = 100, level: str = None, symbol: str = None) -> List[AlertMessage]:
        """Obter histórico de alertas"""
        filtered_history = self.alert_history
        
        if level:
            filtered_history = [alert for alert in filtered_history if alert.level == level]
        
        if symbol:
            filtered_history = [alert for alert in filtered_history if alert.symbol == symbol]
        
        return filtered_history[-limit:]
    
    def get_alert_statistics(self) -> Dict:
        """Obter estatísticas de alertas"""
        if not self.alert_history:
            return {}
        
        stats = {
            'total_alerts': len(self.alert_history),
            'alerts_by_level': {},
            'alerts_by_symbol': {},
            'alerts_last_24h': 0,
            'alerts_last_7d': 0,
            'alerts_last_30d': 0
        }
        
        now = datetime.now()
        
        for alert in self.alert_history:
            # Contar por nível
            if alert.level not in stats['alerts_by_level']:
                stats['alerts_by_level'][alert.level] = 0
            stats['alerts_by_level'][alert.level] += 1
            
            # Contar por símbolo
            if alert.symbol:
                if alert.symbol not in stats['alerts_by_symbol']:
                    stats['alerts_by_symbol'][alert.symbol] = 0
                stats['alerts_by_symbol'][alert.symbol] += 1
            
            # Contar por período
            time_diff = now - alert.timestamp
            if time_diff.total_seconds() <= 86400:  # 24 horas
                stats['alerts_last_24h'] += 1
            if time_diff.total_seconds() <= 604800:  # 7 dias
                stats['alerts_last_7d'] += 1
            if time_diff.total_seconds() <= 2592000:  # 30 dias
                stats['alerts_last_30d'] += 1
        
        return stats
    
    def clear_history(self):
        """Limpar histórico de alertas"""
        self.alert_history.clear()
        self.logger.info("Histórico de alertas limpo")
    
    def export_history(self, filename: str = None) -> str:
        """Exportar histórico de alertas"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"alert_history_{timestamp}.json"
        
        try:
            history_data = []
            for alert in self.alert_history:
                alert_dict = asdict(alert)
                alert_dict['timestamp'] = alert.timestamp.isoformat()
                history_data.append(alert_dict)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Histórico exportado para {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar histórico: {str(e)}")
            return None

class RateLimiter:
    """Limitador de taxa para alertas"""
    
    def __init__(self):
        self.alert_counts = {
            'info': {'last_reset': datetime.now(), 'count': 0},
            'warning': {'last_reset': datetime.now(), 'count': 0},
            'error': {'last_reset': datetime.now(), 'count': 0},
            'critical': {'last_reset': datetime.now(), 'count': 0}
        }
        
        # Limites por hora
        self.limits = {
            'info': 50,
            'warning': 30,
            'error': 20,
            'critical': 10
        }
        
        # Reset a cada hora
        self.reset_interval = timedelta(hours=1)
    
    def can_send(self, level: str) -> bool:
        """Verificar se pode enviar alerta"""
        if level not in self.alert_counts:
            return True
        
        now = datetime.now()
        level_data = self.alert_counts[level]
        
        # Resetar contador se necessário
        if now - level_data['last_reset'] >= self.reset_interval:
            level_data['count'] = 0
            level_data['last_reset'] = now
        
        # Verificar limite
        return level_data['count'] < self.limits[level]
    
    def increment_count(self, level: str):
        """Incrementar contador"""
        if level in self.alert_counts:
            self.alert_counts[level]['count'] += 1

# Funções auxiliares para criar alertas comuns
async def alert_large_trade(alert_system: AlertSystem, symbol: str, amount: float, price: float, side: str):
    """Alertar sobre trade grande"""
    alert = AlertMessage(
        level='info',
        title=f'Large Trade Executed - {symbol}',
        message=f'A large trade has been executed for {symbol}',
        symbol=symbol,
        additional_data={
            'Amount': f'{amount:.4f}',
            'Price': f'${price:.4f}',
            'Side': side.upper(),
            'Total Value': f'${amount * price:.2f}'
        }
    )
    
    await alert_system.send_alert(alert)

async def alert_high_volatility(alert_system: AlertSystem, symbol: str, volatility: float, period: str = "24h"):
    """Alertar sobre alta volatilidade"""
    alert = AlertMessage(
        level='warning',
        title=f'High Volatility Detected - {symbol}',
        message=f'High volatility detected for {symbol} in the last {period}',
        symbol=symbol,
        additional_data={
            'Volatility': f'{volatility:.2%}',
            'Period': period,
            'Risk Level': 'High' if volatility > 0.1 else 'Medium'
        }
    )
    
    await alert_system.send_alert(alert)

async def alert_price_change(alert_system: AlertSystem, symbol: str, change_percent: float, current_price: float):
    """Alertar sobre mudança significativa de preço"""
    level = 'error' if abs(change_percent) > 0.1 else 'warning' if abs(change_percent) > 0.05 else 'info'
    
    alert = AlertMessage(
        level=level,
        title=f'Significant Price Change - {symbol}',
        message=f'Price changed {change_percent:+.2%} for {symbol}',
        symbol=symbol,
        additional_data={
            'Change': f'{change_percent:+.2%}',
            'Current Price': f'${current_price:.4f}',
            'Direction': 'Up' if change_percent > 0 else 'Down'
        }
    )
    
    await alert_system.send_alert(alert)

async def alert_system_error(alert_system: AlertSystem, error_message: str, component: str = "System"):
    """Alertar sobre erro do sistema"""
    alert = AlertMessage(
        level='critical',
        title=f'System Error - {component}',
        message=f'A system error occurred in {component}',
        additional_data={
            'Error': error_message,
            'Component': component,
            'Action Required': 'Check system logs'
        }
    )
    
    await alert_system.send_alert(alert)

async def alert_trade_signal(alert_system: AlertSystem, symbol: str, signal: str, confidence: float, price: float, indicators: Dict):
    """Alertar sobre sinal de trade"""
    level = 'info' if confidence > 0.8 else 'warning'
    
    alert = AlertMessage(
        level=level,
        title=f'Trade Signal - {symbol}',
        message=f'New trade signal generated for {symbol}',
        symbol=symbol,
        additional_data={
            'Signal': signal.upper(),
            'Confidence': f'{confidence:.1%}',
            'Current Price': f'${price:.4f}',
            'RSI': f"{indicators.get('rsi', 'N/A'):.1f}" if indicators.get('rsi') else 'N/A',
            'MACD': indicators.get('macd_signal', 'N/A'),
            'Volume': f"{indicators.get('volume_ratio', 0):.1f}x" if indicators.get('volume_ratio') else 'N/A'
        }
    )
    
    await alert_system.send_alert(alert)

# Exemplo de uso
if __name__ == "__main__":
    # Configuração de exemplo
    config = AlertConfig(
        email_enabled=False,
        telegram_enabled=False,
        discord_enabled=False
    )
    
    # Criar sistema de alertas
    alert_system = AlertSystem(config)
    
    # Exemplo de alerta
    async def test_alert():
        await alert_system.send_alert(AlertMessage(
            level='info',
            title='Test Alert',
            message='This is a test alert from IA GAIN system',
            symbol='BTC/USDT'
        ))
    
    # Executar teste
    asyncio.run(test_alert())