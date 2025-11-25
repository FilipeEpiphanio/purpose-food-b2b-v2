#!/usr/bin/env python3
"""
IA GAIN - Forex Trading Module Runner
Sistema de trading automatizado para pares de moedas forex
"""

import asyncio
import sys
import os
from pathlib import Path
import json
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from src.config.config_manager import ConfigManager
from src.data.data_collector import DataCollector
from src.forex.forex_trading import ForexTrading
from src.forex.forex_analyzer import ForexAnalyzer
from src.trading.risk_manager import RiskManager
from src.utils.notification import NotificationManager
from src.utils.logger import setup_logger

class ForexTradingRunner:
    """Executor do módulo de trading forex"""
    
    def __init__(self, config_path: str = None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # Configurar logger
        self.logger = setup_logger(
            name="forex_trading",
            log_file="logs/forex_trading.log",
            level=self.config.get('logging', {}).get('level', 'INFO')
        )
        
        self.data_collector = None
        self.forex_trading = None
        self.analyzer = None
        self.risk_manager = None
        self.notification_manager = None
        self.exchanges = {}
        
        self.is_running = False
        self.trading_pairs = []
        self.analysis_interval = 300  # 5 minutos
        self.trade_check_interval = 60  # 1 minuto
        
    async def initialize(self):
        """Inicializar componentes"""
        try:
            self.logger.info("Inicializando módulo de trading forex...")
            
            # Inicializar coletor de dados
            self.data_collector = DataCollector(self.config)
            await self.data_collector.initialize()
            
            # Inicializar gerenciador de risco
            self.risk_manager = RiskManager(self.config)
            
            # Inicializar notificações
            self.notification_manager = NotificationManager(self.config)
            await self.notification_manager.initialize()
            
            # Obter exchanges configuradas
            self.exchanges = self.data_collector.exchanges
            
            # Configurar pares forex
            forex_config = self.config.get('forex', {})
            self.trading_pairs = forex_config.get('default_pairs', [
                'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF',
                'AUD/USD', 'USD/CAD', 'NZD/USD', 'EUR/GBP'
            ])
            
            # Inicializar sistema de trading forex
            self.forex_trading = ForexTrading(
                config=self.config,
                exchanges=self.exchanges,
                risk_manager=self.risk_manager,
                notification_manager=self.notification_manager
            )
            
            # Inicializar analisador
            self.analyzer = ForexAnalyzer(self.config.get('forex', {}))
            
            self.logger.info("Módulo de trading forex inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar módulo forex: {str(e)}")
            raise
    
    async def analyze_forex_pairs(self):
        """Analisar pares forex e identificar oportunidades"""
        try:
            self.logger.info("Iniciando análise de pares forex...")
            
            opportunities = []
            
            for symbol in self.trading_pairs:
                try:
                    self.logger.info(f"Analisando {symbol}...")
                    
                    # Coletar dados históricos
                    df = await self.data_collector.get_forex_data(symbol, '1h', limit=200)
                    
                    if df.empty or len(df) < 50:
                        self.logger.warning(f"Dados insuficientes para {symbol}")
                        continue
                    
                    # Realizar análise
                    analysis = await self.analyzer.analyze_forex_pair(symbol, df)
                    
                    # Verificar se é uma boa oportunidade
                    if analysis.signal in [ForexSignal.BUY, ForexSignal.STRONG_BUY, 
                                         ForexSignal.SELL, ForexSignal.STRONG_SELL]:
                        if analysis.confidence >= 0.5:  # Mínimo 50% confiança
                            opportunities.append({
                                'symbol': symbol,
                                'analysis': analysis,
                                'score': analysis.strength_score
                            })
                            
                            self.logger.info(f"Oportunidade encontrada em {symbol}: "
                                           f"{analysis.signal.value} (confiança: {analysis.confidence:.1%})")
                    
                except Exception as e:
                    self.logger.error(f"Erro ao analisar {symbol}: {str(e)}")
                    continue
            
            # Ordenar por score
            opportunities.sort(key=lambda x: x['score'], reverse=True)
            
            self.logger.info(f"Análise concluída. {len(opportunities)} oportunidades encontradas")
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Erro na análise de pares forex: {str(e)}")
            return []
    
    async def execute_trades(self, opportunities: list):
        """Executar trades baseado nas oportunidades"""
        try:
            self.logger.info(f"Executando trades para {len(opportunities)} oportunidades...")
            
            executed_trades = []
            
            for opportunity in opportunities:
                try:
                    symbol = opportunity['symbol']
                    analysis = opportunity['analysis']
                    
                    # Verificar limite de trades simultâneos
                    active_trades = self.forex_trading.get_active_trades()
                    if len(active_trades) >= self.config.get('forex', {}).get('max_simultaneous_trades', 5):
                        self.logger.warning(f"Limite de trades simultâneos atingido")
                        break
                    
                    # Verificar se já existe trade ativo para este par
                    existing_trade = any(trade.symbol == symbol for trade in active_trades)
                    if existing_trade:
                        self.logger.info(f"Trade ativo já existe para {symbol}")
                        continue
                    
                    # Executar trade
                    trade = await self.forex_trading.execute_trade(symbol, analysis)
                    
                    if trade:
                        executed_trades.append(trade)
                        self.logger.info(f"Trade executado com sucesso: {trade.id}")
                    
                    # Pequena pausa entre trades
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Erro ao executar trade para {opportunity['symbol']}: {str(e)}")
                    continue
            
            self.logger.info(f"Execução concluída. {len(executed_trades)} trades executados")
            
            return executed_trades
            
        except Exception as e:
            self.logger.error(f"Erro na execução de trades: {str(e)}")
            return []
    
    async def monitor_and_update(self):
        """Monitorar trades e atualizar sistema"""
        try:
            # Monitorar trades ativos
            await self.forex_trading.monitor_trades()
            
            # Obter estatísticas
            stats = self.forex_trading.get_statistics()
            active_trades = self.forex_trading.get_active_trades()
            
            self.logger.info(f"Status do sistema - Trades ativos: {len(active_trades)}, "
                           f"Total trades: {stats['total_trades']}, "
                           f"Win rate: {stats['win_rate']:.1%}, "
                           f"PnL total: ${stats['total_pnl']:.2f}")
            
            # Salvar estatísticas periodicamente
            if stats['total_trades'] > 0 and stats['total_trades'] % 10 == 0:
                await self.save_statistics(stats)
            
        except Exception as e:
            self.logger.error(f"Erro no monitoramento: {str(e)}")
    
    async def save_statistics(self, stats: dict):
        """Salvar estatísticas"""
        try:
            stats_file = "data/forex_statistics.json"
            
            # Adicionar timestamp
            stats_with_time = {
                'timestamp': datetime.now().isoformat(),
                'statistics': stats
            }
            
            # Salvar
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_with_time, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Estatísticas salvas com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar estatísticas: {str(e)}")
    
    async def run_trading_cycle(self):
        """Executar ciclo completo de trading"""
        try:
            self.logger.info("Iniciando ciclo de trading forex...")
            
            # 1. Analisar pares forex
            opportunities = await self.analyze_forex_pairs()
            
            # 2. Executar trades
            if opportunities:
                await self.execute_trades(opportunities)
            
            # 3. Monitorar trades existentes
            await self.monitor_and_update()
            
            self.logger.info("Ciclo de trading forex concluído")
            
        except Exception as e:
            self.logger.error(f"Erro no ciclo de trading: {str(e)}")
    
    async def start_trading(self):
        """Iniciar trading automatizado"""
        try:
            self.logger.info("Iniciando trading forex automatizado...")
            
            # Inicializar sistema
            await self.initialize()
            
            # Iniciar trading
            await self.forex_trading.start_trading()
            self.is_running = True
            
            # Loop principal
            while self.is_running:
                try:
                    # Executar ciclo de trading
                    await self.run_trading_cycle()
                    
                    # Aguardar próximo ciclo
                    self.logger.info(f"Aguardando {self.analysis_interval} segundos para próximo ciclo...")
                    await asyncio.sleep(self.analysis_interval)
                    
                except KeyboardInterrupt:
                    self.logger.info("Interrupção detectada. Parando trading...")
                    break
                except Exception as e:
                    self.logger.error(f"Erro no loop principal: {str(e)}")
                    await asyncio.sleep(60)  # Aguardar 1 minuto antes de tentar novamente
            
            # Parar trading
            await self.stop_trading()
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar trading: {str(e)}")
            raise
    
    async def stop_trading(self):
        """Parar trading"""
        try:
            self.logger.info("Parando trading forex...")
            
            self.is_running = False
            
            if self.forex_trading:
                await self.forex_trading.stop_trading()
            
            # Salvar estatísticas finais
            if self.forex_trading:
                stats = self.forex_trading.get_statistics()
                await self.save_statistics(stats)
            
            self.logger.info("Trading forex parado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao parar trading: {str(e)}")
    
    def get_status(self) -> dict:
        """Obter status do sistema"""
        try:
            status = {
                'is_running': self.is_running,
                'trading_pairs': self.trading_pairs,
                'active_trades': [],
                'statistics': {},
                'timestamp': datetime.now().isoformat()
            }
            
            if self.forex_trading:
                status['active_trades'] = [trade.to_dict() for trade in self.forex_trading.get_active_trades()]
                status['statistics'] = self.forex_trading.get_statistics()
            
            return status
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status: {str(e)}")
            return {'error': str(e)}

async def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='IA GAIN - Forex Trading Module')
    parser.add_argument('--config', '-c', help='Caminho do arquivo de configuração')
    parser.add_argument('--symbols', '-s', nargs='+', help='Símbolos forex para trading')
    parser.add_argument('--check', action='store_true', help='Verificar configuração e sair')
    parser.add_argument('--dry-run', action='store_true', help='Executar em modo simulação')
    parser.add_argument('--interval', '-i', type=int, default=300, help='Intervalo de análise em segundos')
    
    args = parser.parse_args()
    
    # Configurar logger
    setup_logger("forex_trading", "logs/forex_trading.log")
    
    # Criar runner
    runner = ForexTradingRunner(args.config)
    
    # Verificar configuração
    if args.check:
        logger.info("Verificando configuração...")
        try:
            await runner.initialize()
            logger.info("✅ Configuração válida")
            return
        except Exception as e:
            logger.error(f"❌ Erro na configuração: {str(e)}")
            return
    
    # Configurar símbolos se fornecidos
    if args.symbols:
        runner.trading_pairs = args.symbols
    
    # Configurar intervalo
    runner.analysis_interval = args.interval
    
    # Executar trading
    try:
        await runner.start_trading()
    except KeyboardInterrupt:
        logger.info("Interrupção pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        raise
    finally:
        await runner.stop_trading()

if __name__ == "__main__":
    asyncio.run(main())