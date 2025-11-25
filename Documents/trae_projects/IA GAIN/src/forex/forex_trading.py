"""
Sistema de Trading Automatizado para Forex
Execução de estratégias de trading em pares de moedas
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
import json
from loguru import logger

from .forex_analyzer import ForexAnalyzer, ForexAnalysis, ForexSignal
from ..trading.risk_manager import RiskManager
from ..utils.notification import NotificationManager

class TradeStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

@dataclass
class ForexTrade:
    """Representa uma operação forex"""
    id: str
    symbol: str
    order_type: OrderType
    side: str  # buy/sell
    entry_price: float
    volume: float  # em lotes
    stop_loss: float
    take_profit: float
    status: TradeStatus
    open_time: datetime
    close_time: Optional[datetime] = None
    close_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pips: Optional[float] = None
    commission: float = 0.0
    swap: float = 0.0
    comment: str = ""
    magic_number: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'order_type': self.order_type.value,
            'side': self.side,
            'entry_price': self.entry_price,
            'volume': self.volume,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'status': self.status.value,
            'open_time': self.open_time.isoformat(),
            'close_time': self.close_time.isoformat() if self.close_time else None,
            'close_price': self.close_price,
            'pnl': self.pnl,
            'pnl_pips': self.pnl_pips,
            'commission': self.commission,
            'swap': self.swap,
            'comment': self.comment,
            'magic_number': self.magic_number
        }

class ForexTrading:
    """Sistema de trading automatizado forex"""
    
    def __init__(self, config: Dict, exchanges: Dict, risk_manager: RiskManager, 
                 notification_manager: NotificationManager):
        self.config = config
        self.exchanges = exchanges
        self.risk_manager = risk_manager
        self.notification_manager = notification_manager
        self.analyzer = ForexAnalyzer(config.get('forex', {}))
        
        self.logger = logger.bind(component="ForexTrading")
        
        # Configurações
        self.max_spread = config.get('forex', {}).get('max_spread', 0.0005)
        self.max_slippage = config.get('forex', {}).get('max_slippage', 0.0002)
        self.min_volume = config.get('forex', {}).get('min_volume', 0.01)
        self.max_volume = config.get('forex', {}).get('max_volume', 1.0)
        self.use_trailing_stop = config.get('forex', {}).get('use_trailing_stop', True)
        self.trailing_stop_distance = config.get('forex', {}).get('trailing_stop_distance', 0.002)
        
        # Estado do sistema
        self.active_trades: Dict[str, ForexTrade] = {}
        self.trade_history: List[ForexTrade] = []
        self.is_running = False
        self.trade_counter = 0
        
        # Estatísticas
        self.stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'total_pips': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0
        }
    
    def calculate_lot_size(self, symbol: str, risk_amount: float, stop_loss_pips: float) -> float:
        """Calcular tamanho do lote baseado no risco"""
        try:
            # Obter informações do contrato
            contract_size = 100000  # Tamanho padrão do contrato forex (100k unidades)
            
            # Calcular valor do pip
            pip_value = self.analyzer.calculate_pip_value(symbol, 1.0)  # Valor para 1 lote
            
            # Calcular tamanho do lote
            risk_per_pip = risk_amount / stop_loss_pips
            lot_size = risk_per_pip / pip_value
            
            # Arredondar para o tamanho mínimo permitido
            lot_size = max(self.min_volume, min(lot_size, self.max_volume))
            lot_size = round(lot_size, 2)  # Arredondar para 2 casas decimais
            
            return lot_size
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular tamanho do lote para {symbol}: {str(e)}")
            return self.min_volume
    
    def check_trading_conditions(self, symbol: str, analysis: ForexAnalysis) -> Dict:
        """Verificar condições de trading"""
        try:
            conditions = {
                'can_trade': False,
                'reasons': [],
                'spread_ok': False,
                'volume_ok': False,
                'risk_ok': False,
                'time_ok': False
            }
            
            # Verificar spread
            exchange = self._get_exchange_for_symbol(symbol)
            if exchange:
                ticker = exchange.fetch_ticker(symbol)
                spread = ticker['ask'] - ticker['bid']
                spread_pips = self.analyzer.calculate_pips(symbol, spread)
                
                if spread_pips <= self.max_spread * 10000:
                    conditions['spread_ok'] = True
                else:
                    conditions['reasons'].append(f"Spread alto: {spread_pips:.1f} pips")
            
            # Verificar volume
            if self.min_volume <= analysis.confidence <= self.max_volume:
                conditions['volume_ok'] = True
            else:
                conditions['reasons'].append(f"Volume fora dos limites: {analysis.confidence}")
            
            # Verificar risco
            risk_check = self.risk_manager.check_trade_risk(symbol, analysis.entry_price, 
                                                           analysis.stop_loss_pips, analysis.take_profit_pips)
            if risk_check['allowed']:
                conditions['risk_ok'] = True
            else:
                conditions['reasons'].extend(risk_check['reasons'])
            
            # Verificar horário de trading (exemplo: evitar fim de semana)
            current_time = datetime.now()
            if current_time.weekday() < 5:  # Segunda a sexta
                conditions['time_ok'] = True
            else:
                conditions['reasons'].append("Fora do horário de trading")
            
            # Decisão final
            conditions['can_trade'] = (conditions['spread_ok'] and 
                                     conditions['volume_ok'] and 
                                     conditions['risk_ok'] and 
                                     conditions['time_ok'])
            
            return conditions
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar condições de trading para {symbol}: {str(e)}")
            return {'can_trade': False, 'reasons': [str(e)]}
    
    async def execute_trade(self, symbol: str, analysis: ForexAnalysis) -> Optional[ForexTrade]:
        """Executar operação forex"""
        try:
            # Verificar condições
            conditions = self.check_trading_conditions(symbol, analysis)
            if not conditions['can_trade']:
                self.logger.warning(f"Condições não atendidas para {symbol}: {conditions['reasons']}")
                return None
            
            # Obter exchange apropriada
            exchange = self._get_exchange_for_symbol(symbol)
            if not exchange:
                self.logger.error(f"Exchange não encontrada para {symbol}")
                return None
            
            # Calcular parâmetros da ordem
            current_price = analysis.entry_price
            volume = analysis.confidence  # Usar confiança como volume inicial
            
            # Calcular tamanho real do lote baseado no risco
            risk_amount = self.risk_manager.get_max_risk_per_trade()
            lot_size = self.calculate_lot_size(symbol, risk_amount, analysis.stop_loss_pips)
            
            # Ajustar preços para o lado correto do mercado
            if analysis.signal in [ForexSignal.BUY, ForexSignal.STRONG_BUY]:
                side = "buy"
                entry_price = current_price
                stop_loss = current_price - (analysis.stop_loss_pips / 10000)
                take_profit = current_price + (analysis.take_profit_pips / 10000)
            else:
                side = "sell"
                entry_price = current_price
                stop_loss = current_price + (analysis.stop_loss_pips / 10000)
                take_profit = current_price - (analysis.take_profit_pips / 10000)
            
            # Criar ordem
            order = await self._create_order(
                exchange=exchange,
                symbol=symbol,
                side=side,
                order_type=OrderType.MARKET,
                volume=lot_size,
                price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            if order:
                # Criar objeto trade
                trade = ForexTrade(
                    id=f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    symbol=symbol,
                    order_type=OrderType.MARKET,
                    side=side,
                    entry_price=entry_price,
                    volume=lot_size,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    status=TradeStatus.OPEN,
                    open_time=datetime.now(),
                    magic_number=analysis.confidence * 1000
                )
                
                # Adicionar à lista de trades ativos
                self.active_trades[trade.id] = trade
                
                # Atualizar estatísticas
                self.stats['total_trades'] += 1
                
                # Notificar
                await self._notify_trade_opened(trade, analysis)
                
                self.logger.info(f"Trade executado: {trade.id} - {symbol} {side} @ {entry_price:.5f}")
                
                return trade
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao executar trade para {symbol}: {str(e)}")
            return None
    
    async def monitor_trades(self):
        """Monitorar trades abertos"""
        try:
            closed_trades = []
            
            for trade_id, trade in self.active_trades.items():
                try:
                    # Obter preço atual
                    exchange = self._get_exchange_for_symbol(trade.symbol)
                    if not exchange:
                        continue
                    
                    ticker = exchange.fetch_ticker(trade.symbol)
                    current_price = ticker['last']
                    
                    # Verificar se deve fechar
                    should_close = False
                    close_reason = ""
                    
                    # Verificar stop loss
                    if trade.side == "buy" and current_price <= trade.stop_loss:
                        should_close = True
                        close_reason = "Stop Loss"
                    elif trade.side == "sell" and current_price >= trade.stop_loss:
                        should_close = True
                        close_reason = "Stop Loss"
                    
                    # Verificar take profit
                    if trade.side == "buy" and current_price >= trade.take_profit:
                        should_close = True
                        close_reason = "Take Profit"
                    elif trade.side == "sell" and current_price <= trade.take_profit:
                        should_close = True
                        close_reason = "Take Profit"
                    
                    # Verificar trailing stop
                    if self.use_trailing_stop:
                        new_stop = await self._update_trailing_stop(trade, current_price)
                        if new_stop:
                            trade.stop_loss = new_stop
                    
                    # Fechar trade se necessário
                    if should_close:
                        await self.close_trade(trade, current_price, close_reason)
                        closed_trades.append(trade)
                    
                    # Atualizar PnL em tempo real
                    trade.pnl = self.calculate_pnl(trade, current_price)
                    trade.pnl_pips = self.analyzer.calculate_pips(trade.symbol, trade.pnl / trade.volume)
                    
                except Exception as e:
                    self.logger.error(f"Erro ao monitorar trade {trade_id}: {str(e)}")
            
            # Remover trades fechados
            for trade in closed_trades:
                if trade.id in self.active_trades:
                    del self.active_trades[trade.id]
                    self.trade_history.append(trade)
            
        except Exception as e:
            self.logger.error(f"Erro ao monitorar trades: {str(e)}")
    
    async def close_trade(self, trade: ForexTrade, close_price: float, reason: str = "Manual"):
        """Fechar uma operação"""
        try:
            # Calcular PnL final
            pnl = self.calculate_pnl(trade, close_price)
            pnl_pips = self.analyzer.calculate_pips(trade.symbol, pnl / trade.volume)
            
            # Atualizar trade
            trade.close_price = close_price
            trade.close_time = datetime.now()
            trade.status = TradeStatus.CLOSED
            trade.pnl = pnl
            trade.pnl_pips = pnl_pips
            trade.comment = f"Closed: {reason}"
            
            # Atualizar estatísticas
            if pnl > 0:
                self.stats['winning_trades'] += 1
                self.stats['avg_win'] = (self.stats['avg_win'] * (self.stats['winning_trades'] - 1) + pnl) / self.stats['winning_trades']
            else:
                self.stats['losing_trades'] += 1
                self.stats['avg_loss'] = (self.stats['avg_loss'] * (self.stats['losing_trades'] - 1) + abs(pnl)) / self.stats['losing_trades']
            
            self.stats['total_pnl'] += pnl
            self.stats['total_pips'] += pnl_pips
            self.stats['win_rate'] = self.stats['winning_trades'] / max(1, self.stats['total_trades'])
            
            # Calcular profit factor
            if self.stats['avg_loss'] > 0:
                self.stats['profit_factor'] = self.stats['avg_win'] / self.stats['avg_loss']
            
            # Notificar
            await self._notify_trade_closed(trade, reason)
            
            self.logger.info(f"Trade fechado: {trade.id} - {trade.symbol} @ {close_price:.5f} - PnL: ${pnl:.2f} ({pnl_pips:.1f} pips)")
            
        except Exception as e:
            self.logger.error(f"Erro ao fechar trade {trade.id}: {str(e)}")
    
    def calculate_pnl(self, trade: ForexTrade, current_price: float) -> float:
        """Calcular PnL de uma operação"""
        try:
            price_diff = current_price - trade.entry_price
            
            if trade.side == "sell":
                price_diff = -price_diff
            
            # PnL em moeda base (USD para pares XXX/USD)
            pnl = price_diff * trade.volume * 100000  # Multiplicar por tamanho do contrato
            
            return pnl
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular PnL: {str(e)}")
            return 0.0
    
    async def _create_order(self, exchange, symbol: str, side: str, order_type: OrderType,
                           volume: float, price: float, stop_loss: float, take_profit: float) -> Optional[Dict]:
        """Criar ordem na exchange"""
        try:
            order_params = {
                'symbol': symbol,
                'side': side,
                'type': order_type.value,
                'amount': volume,
                'price': price,
                'params': {
                    'stopLoss': stop_loss,
                    'takeProfit': take_profit
                }
            }
            
            order = exchange.create_order(**order_params)
            return order
            
        except Exception as e:
            self.logger.error(f"Erro ao criar ordem: {str(e)}")
            return None
    
    async def _update_trailing_stop(self, trade: ForexTrade, current_price: float) -> Optional[float]:
        """Atualizar trailing stop"""
        try:
            if trade.side == "buy":
                # Para compra, ajustar stop loss para cima
                new_stop = current_price - self.trailing_stop_distance
                if new_stop > trade.stop_loss:
                    return new_stop
            else:
                # Para venda, ajustar stop loss para baixo
                new_stop = current_price + self.trailing_stop_distance
                if new_stop < trade.stop_loss:
                    return new_stop
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar trailing stop: {str(e)}")
            return None
    
    def _get_exchange_for_symbol(self, symbol: str) -> Optional:
        """Obter exchange apropriada para o símbolo"""
        try:
            # Para forex, usar OANDA ou FXCM
            if 'USD' in symbol or 'EUR' in symbol or 'GBP' in symbol:
                if 'oanda' in self.exchanges:
                    return self.exchanges['oanda']
                elif 'fxcm' in self.exchanges:
                    return self.exchanges['fxcm']
            
            # Fallback para Binance
            return self.exchanges.get('binance')
            
        except Exception as e:
            self.logger.error(f"Erro ao obter exchange para {symbol}: {str(e)}")
            return None
    
    async def _notify_trade_opened(self, trade: ForexTrade, analysis: ForexAnalysis):
        """Notificar abertura de trade"""
        try:
            message = f"""
🟢 **NOVA OPERAÇÃO FOREX ABERTA**

📊 **Par:** {trade.symbol}
🎯 **Sinal:** {analysis.signal.value.upper()}
📈 **Lado:** {trade.side.upper()}
💰 **Preço Entrada:** {trade.entry_price:.5f}
📏 **Volume:** {trade.volume:.2f} lotes
🛑 **Stop Loss:** {trade.stop_loss:.5f} ({analysis.stop_loss_pips:.1f} pips)
🎯 **Take Profit:** {trade.take_profit:.5f} ({analysis.take_profit_pips:.1f} pips)
⚖️ **R:R:** {analysis.risk_reward_ratio:.2f}
🎯 **Confiança:** {analysis.confidence:.1%}
            """
            
            await self.notification_manager.send_notification(message, 'trade_opened')
            
        except Exception as e:
            self.logger.error(f"Erro ao notificar abertura de trade: {str(e)}")
    
    async def _notify_trade_closed(self, trade: ForexTrade, reason: str):
        """Notificar fechamento de trade"""
        try:
            message = f"""
🔴 **OPERAÇÃO FOREX FECHADA**

📊 **Par:** {trade.symbol}
📈 **Lado:** {trade.side.upper()}
💰 **Preço Entrada:** {trade.entry_price:.5f}
💰 **Preço Saída:** {trade.close_price:.5f}
💵 **PnL:** ${trade.pnl:.2f} ({trade.pnl_pips:.1f} pips)
📅 **Duração:** {trade.close_time - trade.open_time}
📝 **Motivo:** {reason}
            """
            
            await self.notification_manager.send_notification(message, 'trade_closed')
            
        except Exception as e:
            self.logger.error(f"Erro ao notificar fechamento de trade: {str(e)}")
    
    def get_active_trades(self) -> List[ForexTrade]:
        """Obter trades ativos"""
        return list(self.active_trades.values())
    
    def get_trade_history(self, limit: int = 100) -> List[ForexTrade]:
        """Obter histórico de trades"""
        return self.trade_history[-limit:]
    
    def get_statistics(self) -> Dict:
        """Obter estatísticas de trading"""
        return self.stats.copy()
    
    async def start_trading(self):
        """Iniciar sistema de trading"""
        self.is_running = True
        self.logger.info("Sistema de trading forex iniciado")
        
        # Notificar início
        await self.notification_manager.send_notification("🚀 **SISTEMA FOREX INICIADO**", 'system_status')
    
    async def stop_trading(self):
        """Parar sistema de trading"""
        self.is_running = False
        self.logger.info("Sistema de trading forex parado")
        
        # Notificar parada
        await self.notification_manager.send_notification("⏹️ **SISTEMA FOREX PARADO**", 'system_status')
    
    def is_trading_active(self) -> bool:
        """Verificar se o trading está ativo"""
        return self.is_running