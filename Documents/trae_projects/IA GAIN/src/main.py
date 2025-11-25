#!/usr/bin/env python3
"""
IA GAIN - Sistema de Trading com Inteligência Artificial
Ponto de entrada principal do sistema
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
import json
import signal
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent))

from data.data_collector import DataCollector, MarketData
from trading.automated_trading import AutomatedTrading
from analysis.crypto_selector import CryptoSelector
from ml.ml_model import MLModel
from alerts.alert_system import AlertSystem, AlertConfig
from risk.risk_manager import RiskManager
from analysis.momentum_analyzer import AdvancedMomentumAnalyzer
from analysis.combined_analyzer import CombinedAnalyzer
from exchange.metatrader5_integration import MetaTrader5Integration, TradeSignal, OrderType
from utils.utils import LoggerConfig

class IAGain:
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = self.load_config()
        self.logger = LoggerConfig.setup_logging('IAGain', self.load_log_level(), 'iagain.log')
        self.running = False
        self.components = {}
        
        # Inicializar componentes
        self.data_collector = None
        self.trading_system = None
        self.crypto_selector = None
        self.ml_model = None
        self.alert_system = None
        self.risk_manager = None
        self.momentum_analyzer = None
        self.combined_analyzer = None
        self.mt5 = None
        
        self.logger.info("IA GAIN System initialized")
    
    def load_config(self) -> dict:
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Configuration file {self.config_path} not found")
            return self.create_default_config()
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing configuration file: {e}")
            return self.create_default_config()
    
    def create_default_config(self) -> dict:
        default_config = {
            "system": {
                "mode": "live",  # live, paper, backtest
                "update_interval": 300,  # seconds
                "max_concurrent_trades": 5,
                "enable_notifications": True,
                "enable_risk_management": True
            },
            "trading": {
                "max_position_size": 0.1,
                "stop_loss": 0.02,
                "take_profit": 0.05,
                "max_daily_trades": 10,
                "min_volume_threshold": 1000000,
                "trading_hours": "24/7",
                "exchanges": ["binance", "coinbase", "kraken"]
            },
            "risk": {
                "max_portfolio_risk": 0.05,
                "max_single_trade_risk": 0.02,
                "risk_reward_ratio": 2.0,
                "use_trailing_stop": True,
                "trailing_stop_distance": 0.03,
                "max_drawdown": 0.1
            },
            "mt5": {
                "login": 0,
                "password": "",
                "server": "",
                "path": ""
            },
            "technical": {
                "rsi_period": 14,
                "rsi_overbought": 70,
                "rsi_oversold": 30,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "bb_period": 20,
                "bb_std": 2,
                "ema_periods": [9, 21, 50, 200]
            },
            "fundamental": {
                "min_market_cap": 100000000,
                "min_liquidity": 50000000,
                "max_supply_centralization": 0.3,
                "min_development_activity": 0.7,
                "sentiment_threshold": 0.6
            },
            "ml": {
                "model_type": "ensemble",
                "prediction_horizon": 24,  # hours
                "retrain_interval": 168,  # hours
                "confidence_threshold": 0.7
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "to_addresses": []
                },
                "telegram": {
                    "enabled": False,
                    "bot_token": "",
                    "chat_id": ""
                },
                "webhook": {
                    "enabled": False,
                    "url": ""
                }
            },
            "logging": {
                "level": "INFO",
                "file": "iagain.log",
                "max_size": "10MB",
                "backup_count": 5
            }
        }
        
        # Salvar configuração padrão
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.logger.info("Default configuration created")
        return default_config

    def load_log_level(self) -> str:
        try:
            with open(self.config_path, 'r') as f:
                cfg = json.load(f)
                return cfg.get("logging", {}).get("level", "INFO")
        except Exception:
            return "INFO"
    
    async def initialize_components(self):
        self.logger.info("Initializing system components...")
        
        try:
            # Inicializar coletor de dados
            self.data_collector = DataCollector(self.config_path)
            await self.data_collector.initialize_exchanges()
            
            # Inicializar sistema de trading
            self.trading_system = AutomatedTrading(self.config_path)
            
            # Inicializar seletor de criptomoedas
            self.crypto_selector = CryptoSelector(self.config_path)
            await self.crypto_selector.initialize_exchanges()
            
            # Inicializar modelo de ML
            self.ml_model = MLModel(self.config.get("ml", {}))
            
            # Inicializar sistema de alertas
            notif_cfg = self.config.get("notifications", {})
            alert_cfg = AlertConfig(
                email_enabled=bool(notif_cfg.get("email", {}).get("enabled", False)),
                email_address=notif_cfg.get("email", {}).get("username", ""),
                email_password=notif_cfg.get("email", {}).get("password", ""),
                smtp_server=notif_cfg.get("email", {}).get("smtp_server", "smtp.gmail.com"),
                smtp_port=int(notif_cfg.get("email", {}).get("smtp_port", 587)),
                telegram_enabled=bool(notif_cfg.get("telegram", {}).get("enabled", False)),
                telegram_bot_token=notif_cfg.get("telegram", {}).get("bot_token", ""),
                telegram_chat_id=notif_cfg.get("telegram", {}).get("chat_id", ""),
            )
            self.alert_system = AlertSystem(alert_cfg)
            
            # Inicializar gerenciador de risco
            self.risk_manager = RiskManager(self.config)
            
            # Inicializar analisadores
            self.momentum_analyzer = AdvancedMomentumAnalyzer()
            self.combined_analyzer = CombinedAnalyzer({
                "technical": self.config.get("technical", {}),
                "fundamental": self.config.get("fundamental", {}),
                "weights": {"technical": 0.4, "fundamental": 0.3}
            })
            
            # Inicializar MT5 se configurado
            mt5_cfg = self.config.get("mt5", {})
            if int(mt5_cfg.get("login", 0)) > 0 and mt5_cfg.get("server"):
                self.mt5 = MetaTrader5Integration(mt5_cfg)
                self.mt5.connect()
            
            self.components = {
                'data_collector': self.data_collector,
                'trading_system': self.trading_system,
                'crypto_selector': self.crypto_selector,
                'ml_model': self.ml_model,
                'alert_system': self.alert_system,
                'risk_manager': self.risk_manager,
                'momentum_analyzer': self.momentum_analyzer,
                'combined_analyzer': self.combined_analyzer,
                'mt5': self.mt5
            }
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            raise
    
    async def start_trading_cycle(self):
        self.logger.info("Starting trading cycle...")
        
        try:
            # 1. Seleção de criptos
            self.logger.info("Selecting best cryptocurrencies...")
            selected_scores = await self.crypto_selector.select_best_cryptocurrencies(20)
            symbols = self.crypto_selector.get_selected_symbols(selected_scores)
            
            # 2. Coleta de dados para momentum e sinais
            self.logger.info("Fetching market data for momentum analysis...")
            market_frames: Dict[str, Dict[str, pd.Series]] = {}
            selected_market_data: List[MarketData] = []
            for sym in symbols[:15]:
                df = await self.data_collector.get_historical_data(sym, '1h', 200)
                if df is not None and not df.empty:
                    market_frames[sym] = {
                        'open': df['open'],
                        'high': df['high'],
                        'low': df['low'],
                        'close': df['close'],
                        'volume': df['volume'],
                    }
                    md = await self.data_collector.analyze_market_data(sym, df)
                    selected_market_data.append(md)
            
            # 3. Análise de momentum e top 10
            self.logger.info("Analyzing momentum and building Top 10 list...")
            momentum_signals = []
            for sym, data in market_frames.items():
                sig = self.momentum_analyzer.analyze_momentum(data, sym, '1h')
                momentum_signals.append(sig)
            momentum_signals.sort(key=lambda s: (s.confidence, s.strength), reverse=True)
            top10 = momentum_signals[:10]
            for i, s in enumerate(top10, 1):
                self.logger.info(f"Top {i}: {s.symbol} {s.signal_type} strength={s.strength:.3f} conf={s.confidence:.3f}")
            
            # 4. Avaliação combinada por ativo
            self.logger.info("Combining technical/fundamental signals...")
            combined_scores: Dict[str, float] = {}
            for md in selected_market_data:
                try:
                    df = await self.data_collector.get_historical_data(md.symbol, '1h', 200)
                    score_out = self.combined_analyzer.analyze(df, md.symbol)
                    ml_pred = None
                    try:
                        ml_pred = self.ml_model.predict(df, md.symbol)
                    except Exception:
                        ml_pred = None
                    w_t = 0.4
                    w_m = 0.4
                    w_ml = 0.2
                    mom = next((s for s in momentum_signals if s.symbol == md.symbol), None)
                    mom_score = mom.indicators.get('composite_momentum', 0.0) if mom else 0.0
                    ml_score = float(ml_pred.confidence) * np.sign(float(ml_pred.prediction)) if ml_pred else 0.0
                    combined_scores[md.symbol] = float(score_out['score'] * w_t + mom_score * w_m + ml_score * w_ml)
                except Exception:
                    combined_scores[md.symbol] = 0.0
            
            # 5. Avaliar riscos
            if self.config['system']['enable_risk_management']:
                self.logger.info("Evaluating risks...")
                # Placeholder de avaliação agregada
                portfolio_risk = 0.0
                if portfolio_risk > self.config['risk']['max_portfolio_risk']:
                    self.logger.warning("Portfolio risk too high, skipping trades")
                    return
            
            # 6. Executar trades em cripto
            self.logger.info("Executing crypto trades...")
            await self.trading_system.execute_trades(selected_market_data)
            
            # 7. Executar trades em forex via MT5
            if self.mt5:
                self.logger.info("Evaluating forex pairs for MT5...")
                forex_pairs = [
                    'EUR/USD','GBP/USD','USD/JPY','USD/CHF','AUD/USD','USD/CAD','NZD/USD',
                    'EUR/GBP','EUR/JPY','GBP/JPY','AUD/JPY','CAD/JPY','EUR/CHF','GBP/CHF'
                ]
                for pair in forex_pairs:
                    df_fx = await self.data_collector.get_forex_data(pair, 'H1', 200)
                    if df_fx is None or df_fx.empty:
                        continue
                    data_fx = {
                        'open': df_fx['open'],
                        'high': df_fx['high'],
                        'low': df_fx['low'],
                        'close': df_fx['close'],
                        'volume': df_fx.get('volume', pd.Series([1.0] * len(df_fx)))
                    }
                    mom_sig = self.momentum_analyzer.analyze_momentum(data_fx, pair.replace('/', ''), 'H1')
                    if mom_sig.signal_type in ('bullish', 'bearish') and mom_sig.confidence >= 0.6:
                        price = float(df_fx['close'].iloc[-1])
                        sl = mom_sig.stop_loss if mom_sig.stop_loss else (price * (0.998 if mom_sig.signal_type == 'bullish' else 1.002))
                        tp = mom_sig.price_target if mom_sig.price_target else (price * (1.004 if mom_sig.signal_type == 'bullish' else 0.996))
                        lot = self.mt5.calculate_lot_size(pair.replace('/', ''), self.config['risk']['max_single_trade_risk'] * 100, 20)
                        order_type = OrderType.BUY if mom_sig.signal_type == 'bullish' else OrderType.SELL
                        ts = TradeSignal(symbol=pair.replace('/', ''), order_type=order_type, volume=lot, price=price, sl=sl, tp=tp)
                        self.mt5.send_order(ts)
            
            # 8. Enviar notificações
            if self.config['system']['enable_notifications']:
                # Placeholder de alerta simples
                pass
            
            self.logger.info("Trading cycle completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}")
            
    
    async def run(self):
        self.logger.info("IA GAIN System starting...")
        self.running = True
        
        # Inicializar componentes
        await self.initialize_components()
        
        # Enviar notificação de inicialização
        if self.config['system']['enable_notifications']:
            pass
        
        try:
            while self.running:
                await self.start_trading_cycle()
                
                # Aguardar próximo ciclo
                update_interval = self.config['system']['update_interval']
                self.logger.info(f"Waiting {update_interval} seconds for next cycle...")
                await asyncio.sleep(update_interval)
                
        except KeyboardInterrupt:
            self.logger.info("System shutdown requested by user")
        except Exception as e:
            self.logger.error(f"Fatal error in main loop: {e}")
            await self.notification_system.send_error_notification(f"Fatal error: {str(e)}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        self.logger.info("Shutting down IA GAIN System...")
        self.running = False
        
        # Fechar todos os componentes
        for component_name, component in self.components.items():
            try:
                if hasattr(component, 'close'):
                    await component.close()
                    self.logger.info(f"Closed {component_name}")
            except Exception as e:
                self.logger.error(f"Error closing {component_name}: {e}")
        
        # Enviar notificação de desligamento
        if self.config['system']['enable_notifications']:
            pass
        
        self.logger.info("IA GAIN System shutdown complete")
    
    def signal_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.shutdown())
    
    def print_system_status(self):
        print("\n" + "="*50)
        print("IA GAIN - Sistema de Trading com Inteligência Artificial")
        print("="*50)
        print(f"Status: {'Running' if self.running else 'Stopped'}")
        print(f"Mode: {self.config['system']['mode']}")
        print(f"Update Interval: {self.config['system']['update_interval']} seconds")
        print(f"Max Concurrent Trades: {self.config['system']['max_concurrent_trades']}")
        print(f"Risk Management: {'Enabled' if self.config['system']['enable_risk_management'] else 'Disabled'}")
        print(f"Notifications: {'Enabled' if self.config['system']['enable_notifications'] else 'Disabled'}")
        print("="*50)
        print("\nPress Ctrl+C to stop the system\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='IA GAIN - Sistema de Trading com Inteligência Artificial')
    parser.add_argument('--config', '-c', default='config.json', help='Path to configuration file')
    parser.add_argument('--mode', '-m', choices=['live', 'paper', 'backtest'], help='Trading mode')
    parser.add_argument('--daemon', '-d', action='store_true', help='Run as daemon')
    parser.add_argument('--status', '-s', action='store_true', help='Show system status')
    
    args = parser.parse_args()
    
    # Criar sistema
    system = IAGain(args.config)
    
    if args.status:
        system.print_system_status()
        return
    
    if args.mode:
        system.config['system']['mode'] = args.mode
    
    # Configurar handlers de sinal
    signal.signal(signal.SIGINT, system.signal_handler)
    signal.signal(signal.SIGTERM, system.signal_handler)
    
    # Executar sistema
    try:
        system.print_system_status()
        asyncio.run(system.run())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
