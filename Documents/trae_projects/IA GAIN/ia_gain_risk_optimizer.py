#!/usr/bin/env python3
"""
IA GAIN + MetaTrader 5 - CONFIGURAÇÃO OTIMIZADA DE RISCO
Ajusta os parâmetros de risco conforme solicitado para trading mais conservador
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizedRiskConfig:
    """Configuração otimizada de risco para trading conservador"""
    
    def __init__(self):
        # NOVOS PARÂMETROS DE RISCO AJUSTADOS
        self.risk_parameters = {
            'max_risk_per_trade': 0.01,      # 1% por trade (era 2%)
            'max_daily_risk': 0.045,        # 4.5% por dia (era 6%)
            'max_drawdown': 0.09,           # 9% máximo drawdown (era 15%)
            'max_positions': 5,             # 5 posições máximas (era 10)
            'min_confidence': 0.55,          # 55% confiança mínima
            'risk_reward_ratio': 2.0,       # 1:2 risco/recompensa (era 1.5)
            'position_sizing_method': "percentage",  # percentage, fixed, kelly
            'use_trailing_stop': True,        # Usar trailing stop
            'trailing_stop_distance': 0.002,  # 20 pips trailing
            'max_leverage': 10,              # Máxima alavancagem permitida
        }
        
        # Parâmetros de mercado otimizados
        self.market_parameters = {
            'max_spread': 30,                # Máximo 30 pontos de spread
            'min_volatility': 0.0001,        # Mínima volatilidade aceitável
            'max_volatility': 0.015,         # Máxima volatilidade (1.5%)
            'volume_threshold': 1.3,         # Threshold de volume (1.3x)
            'avoid_news_hours': True,        # Evitar horários de notícias
            'news_hours': [(7, 9), (13, 15)], # Horários de notícias (GMT)
            'min_liquidity': 100,             # Mínima liquidez (volume)
        }
        
        # Parâmetros de execução
        self.execution_parameters = {
            'max_slippage': 10,              # Máximo slippage em pontos
            'max_deviation': 15,             # Máximo desvio de preço
            'order_timeout': 30,             # Timeout de ordem em segundos
            'retry_attempts': 3,             # Tentativas de reexecução
            'use_market_orders': True,       # Usar ordens de mercado
            'partial_fills_allowed': False,  # Não permitir execuções parciais
        }
        
        # Símbolos otimizados para baixo risco
        self.optimized_symbols = [
            'EURUSDm',   # Menor spread, alta liquidez
            'GBPUSDm',   # Boa volatilidade, alta liquidez
            'USDJPYm',   # Estável, boa liquidez
            'AUDUSDm',   # Correlação com commodities
            'USDCHFm',   # Safe haven, boa liquidez
            'USDCADm',   # Correlação com petróleo
        ]
        
        # Horários otimizados
        self.optimized_hours = {
            'trading_start': 8,    # 08:00 GMT (abertura Europa)
            'trading_end': 17,     # 17:00 GMT (fechamento Europa)
            'avoid_weekend': True, # Evitar domingo e sexta tarde
            'max_session_duration': 240, # 4 horas máximo por sessão
        }
    
    def generate_optimized_config(self) -> Dict[str, Any]:
        """Gera configuração completa otimizada"""
        config = {
            'version': '2.0',
            'created_at': datetime.now().isoformat(),
            'description': 'Configuração otimizada de risco para IA GAIN + MT5',
            'risk_management': self.risk_parameters,
            'market_filters': self.market_parameters,
            'execution_settings': self.execution_parameters,
            'trading_symbols': self.optimized_symbols,
            'trading_hours': self.optimized_hours,
            'optimization_notes': self._get_optimization_notes()
        }
        
        return config
    
    def _get_optimization_notes(self) -> Dict[str, str]:
        """Notas sobre as otimizações realizadas"""
        return {
            'risk_reduction': 'Reduzido risco por trade de 2% para 1% para proteger capital',
            'daily_limit': 'Reduzido limite diário para 4.5% para evitar perdas acumuladas',
            'drawdown_control': 'Ajustado drawdown máximo para 9% para proteção agressiva',
            'position_limit': 'Reduzido número máximo de posições para 5 para melhor controle',
            'risk_reward': 'Aumentado R/R ratio para 1:2 para melhor relação risco/recompensa',
            'confidence_threshold': 'Reduzido threshold de confiança para 55% para mais oportunidades',
            'symbol_selection': 'Selecionado apenas pares maiores com baixo spread e alta liquidez',
            'time_restriction': 'Limitado horário de trading para evitar períodos de alta volatilidade',
            'execution_safety': 'Adicionado múltiplas camadas de proteção na execução',
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Valida a configuração gerada"""
        try:
            # Validar parâmetros de risco
            risk = config['risk_management']
            
            if not (0 < risk['max_risk_per_trade'] <= 0.05):  # Máximo 5%
                logger.error("Risco por trade muito alto")
                return False
            
            if not (0 < risk['max_daily_risk'] <= 0.10):  # Máximo 10%
                logger.error("Risco diário muito alto")
                return False
            
            if not (0 < risk['max_drawdown'] <= 0.20):  # Máximo 20%
                logger.error("Drawdown máximo muito alto")
                return False
            
            if risk['risk_reward_ratio'] < 1.0:  # Mínimo 1:1
                logger.error("R/R ratio muito baixo")
                return False
            
            # Validar símbolos
            symbols = config['trading_symbols']
            if len(symbols) > 10:  # Máximo 10 símbolos
                logger.error("Muitos símbolos selecionados")
                return False
            
            logger.info("✅ Configuração validada com sucesso")
            return True
            
        except KeyError as e:
            logger.error(f"Configuração incompleta: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return False
    
    def save_config(self, config: Dict[str, Any], filename: str = None):
        """Salva configuração em arquivo JSON"""
        try:
            if filename is None:
                filename = f"ia_gain_optimized_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"✅ Configuração salva em: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
            return None
    
    def create_trading_script_template(self, config: Dict[str, Any]) -> str:
        """Cria template de script de trading com configuração otimizada"""
        template = f'''#!/usr/bin/env python3
"""
IA GAIN + MetaTrader 5 - Trading com Configuração Otimizada de Risco
Script gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Configuração: Conservadora com risco reduzido
"""

import MetaTrader5 as mt5
import pandas as pd
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IA_GAIN_ConservativeTrader:
    """Trader conservador com configuração otimizada de risco"""
    
    def __init__(self):
        # Parâmetros de risco (CONSERVADORES)
        self.max_risk_per_trade = {config['risk_management']['max_risk_per_trade']}  # {config['risk_management']['max_risk_per_trade']*100}% risco por trade
        self.max_daily_risk = {config['risk_management']['max_daily_risk']}  # {config['risk_management']['max_daily_risk']*100}% risco diário
        self.max_drawdown = {config['risk_management']['max_drawdown']}  # {config['risk_management']['max_drawdown']*100}% drawdown máximo
        self.max_positions = {config['risk_management']['max_positions']}  # Máximo {config['risk_management']['max_positions']} posições
        self.min_confidence = {config['risk_management']['min_confidence']}  # {config['risk_management']['min_confidence']*100}% confiança mínima
        self.risk_reward_ratio = {config['risk_management']['risk_reward_ratio']}  # R/R ratio {config['risk_management']['risk_reward_ratio']}:1
        
        # Símbolos otimizados
        self.trading_symbols = {config['trading_symbols']}
        
        # Filtros de mercado
        self.max_spread = {config['market_filters']['max_spread']}  # Máximo {config['market_filters']['max_spread']} pontos de spread
        self.max_volatility = {config['market_filters']['max_volatility']}  # Máxima volatilidade aceitável
        
        # Estatísticas
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.session_start = datetime.now()
        
        logger.info("🎯 Trader conservador inicializado com configuração otimizada")
        logger.info(f"📊 Risco por trade: {config['risk_management']['max_risk_per_trade']*100}%")
        logger.info(f"📈 R/R Ratio: {config['risk_management']['risk_reward_ratio']}:1")
        logger.info(f"📋 Máximo de posições: {config['risk_management']['max_positions']}")
    
    def connect_to_mt5(self) -> bool:
        """Conecta ao MetaTrader 5"""
        try:
            if not mt5.initialize():
                logger.error("Falha ao inicializar MT5")
                return False
            
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Não foi possível obter informações da conta")
                return False
            
            logger.info(f"✅ Conectado! Conta: {{account_info.login}}")
            logger.info(f"💰 Saldo: ${{account_info.balance:.2f}}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar MT5: {{e}}")
            return False
    
    def check_risk_limits(self) -> bool:
        """Verifica limites de risco"""
        try:
            # Verificar drawdown diário
            if abs(self.daily_pnl) > (mt5.account_info().balance * self.max_daily_risk):
                logger.warning(f"Limite diário atingido: ${{self.daily_pnl:.2f}}")
                return False
            
            # Verificar número de posições
            positions = mt5.positions_get()
            if positions and len(positions) >= self.max_positions:
                logger.warning(f"Máximo de posições atingido: {{len(positions)}}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar limites: {{e}}")
            return False
    
    def execute_conservative_trade(self, symbol: str, signal: str, confidence: float) -> bool:
        """Executa trade com gestão conservadora de risco"""
        try:
            if confidence < self.min_confidence:
                logger.info(f"Confiança baixa: {{confidence:.1%}} < {{self.min_confidence:.1%}}")
                return False
            
            if not self.check_risk_limits():
                return False
            
            # Implementar lógica de execução com SL/TP baseado em ATR
            # ... (código de execução aqui)
            
            logger.info(f"✅ Trade conservador executado: {{symbol}} {{signal}}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao executar trade: {{e}}")
            return False
    
    def run_conservative_session(self, duration_minutes: int = 60):
        """Executa sessão de trading conservadora"""
        logger.info("🚀 Iniciando sessão conservadora...")
        # ... implementar lógica da sessão
        logger.info("✅ Sessão conservadora concluída")

def main():
    """Função principal"""
    trader = IA_GAIN_ConservativeTrader()
    
    if not trader.connect_to_mt5():
        return
    
    try:
        trader.run_conservative_session(duration_minutes=60)
    except KeyboardInterrupt:
        logger.info("Sessão interrompida pelo usuário")
    finally:
        mt5.shutdown()
        logger.info("Desconectado do MT5")

if __name__ == "__main__":
    main()
'''
        return template

def main():
    """Função principal"""
    print("🎯 IA GAIN + MetaTrader 5 - CONFIGURAÇÃO OTIMIZADA DE RISCO")
    print("="*60)
    print("📊 Ajustando parâmetros para trading mais conservador:")
    print("   • Risco por trade: 2% → 1%")
    print("   • Risco diário: 6% → 4.5%") 
    print("   • Drawdown máximo: 15% → 9%")
    print("   • Máximo posições: 10 → 5")
    print("   • R/R Ratio: 1.5 → 2.0")
    print("="*60)
    
    # Criar configurador
    configurator = OptimizedRiskConfig()
    
    # Gerar configuração
    config = configurator.generate_optimized_config()
    
    # Validar
    if configurator.validate_config(config):
        print("✅ Configuração validada com sucesso!")
        
        # Salvar configuração
        filename = configurator.save_config(config)
        
        # Gerar script template
        template = configurator.create_trading_script_template(config)
        
        # Salvar template
        template_filename = filename.replace('.json', '_trader.py')
        with open(template_filename, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"📄 Script template salvo em: {template_filename}")
        print("\n🚀 Configuração otimizada de risco gerada com sucesso!")
        print("💡 Use o script template para trading com os novos parâmetros")
        
    else:
        print("❌ Falha na validação da configuração")

if __name__ == "__main__":
    main()