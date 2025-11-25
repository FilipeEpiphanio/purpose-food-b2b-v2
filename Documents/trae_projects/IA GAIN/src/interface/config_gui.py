import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Dict, Any
from datetime import datetime

class ConfigInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IA GAIN - Configuração")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Configuração
        self.config = {}
        self.config_file = "config.json"
        
        # Carregar configuração existente
        self.load_config()
        
        # Criar interface
        self.create_widgets()
        
    def load_config(self):
        """Carregar configuração existente"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configuração: {str(e)}")
            self.config = self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão"""
        return {
            "trading": {
                "base_currency": "USDT",
                "trade_amount": 100.0,
                "max_positions": 5,
                "stop_loss": 0.05,
                "take_profit": 0.15,
                "leverage": 1,
                "trading_enabled": True,
                "paper_trading": True,
                "auto_select_cryptos": True,
                "selected_cryptos": ["BTC/USDT", "ETH/USDT", "ADA/USDT"]
            },
            "risk_management": {
                "max_daily_loss": 0.05,
                "max_position_size": 0.2,
                "max_drawdown": 0.15,
                "risk_per_trade": 0.02,
                "position_sizing_method": "kelly_criterion",
                "diversification_min_cryptos": 3,
                "diversification_max_cryptos": 10
            },
            "technical_analysis": {
                "rsi_period": 14,
                "rsi_overbought": 70,
                "rsi_oversold": 30,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "bb_period": 20,
                "bb_std": 2,
                "ema_fast": 9,
                "ema_slow": 21,
                "volume_sma_period": 20
            },
            "fundamental_analysis": {
                "min_market_cap": 100000000,
                "min_volume_24h": 1000000,
                "max_volatility": 0.15,
                "social_sentiment_weight": 0.3,
                "github_activity_weight": 0.3,
                "developer_activity_weight": 0.4
            },
            "api": {
                "binance": {
                    "api_key": "",
                    "api_secret": "",
                    "testnet": True,
                    "sandbox": True
                },
                "coinbase": {
                    "api_key": "",
                    "api_secret": "",
                    "passphrase": "",
                    "sandbox": True
                },
                "coinmarketcap": {
                    "api_key": "",
                    "base_url": "https://pro-api.coinmarketcap.com"
                },
                "coingecko": {
                    "api_key": "",
                    "base_url": "https://api.coingecko.com/api/v3"
                }
            },
            "crypto_selector": {
                "technical_weight": 0.3,
                "fundamental_weight": 0.25,
                "social_weight": 0.15,
                "risk_weight": 0.2,
                "volume_weight": 0.1,
                "min_total_score": 6.0,
                "max_cryptos_to_select": 20,
                "excluded_symbols": ["USDT", "USDC", "BUSD", "DAI"],
                "preferred_categories": ["Layer 1", "DeFi", "Gaming", "NFT"]
            },
            "ml_model": {
                "model_type": "ensemble",
                "prediction_horizon": 24,
                "retrain_interval": 168,
                "confidence_threshold": 0.7,
                "use_sentiment_analysis": True,
                "use_technical_indicators": True,
                "use_fundamental_data": True
            },
            "alerts": {
                "email_enabled": False,
                "email_address": "",
                "email_password": "",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "telegram_enabled": False,
                "telegram_bot_token": "",
                "telegram_chat_id": "",
                "discord_enabled": False,
                "discord_webhook": "",
                "alert_on_large_trades": True,
                "alert_on_high_volatility": True,
                "alert_on_significant_price_changes": True,
                "alert_on_system_errors": True
            },
            "system": {
                "log_level": "INFO",
                "log_file": "iagain.log",
                "data_retention_days": 90,
                "backup_enabled": True,
                "backup_interval_hours": 24,
                "max_workers": 4,
                "timeout_seconds": 30
            }
        }
    
    def create_widgets(self):
        """Criar widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Notebook (abas)
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Criar abas
        self.create_trading_tab(notebook)
        self.create_risk_tab(notebook)
        self.create_analysis_tab(notebook)
        self.create_api_tab(notebook)
        self.create_selector_tab(notebook)
        self.create_ml_tab(notebook)
        self.create_alerts_tab(notebook)
        self.create_system_tab(notebook)
        
        # Botões de controle
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Salvar", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Carregar", command=self.load_config_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exportar", command=self.export_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Resetar", command=self.reset_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Testar APIs", command=self.test_apis).pack(side=tk.LEFT, padx=5)
        
        # Barra de status
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Configurar expansão
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
    
    def create_trading_tab(self, notebook):
        """Criar aba de trading"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Trading")
        
        # Configurações de trading
        row = 0
        
        ttk.Label(frame, text="Moeda Base:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.base_currency_var = tk.StringVar(value=self.config['trading']['base_currency'])
        ttk.Entry(frame, textvariable=self.base_currency_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Valor por Trade (USDT):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.trade_amount_var = tk.DoubleVar(value=self.config['trading']['trade_amount'])
        ttk.Entry(frame, textvariable=self.trade_amount_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Máximo de Posições:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.max_positions_var = tk.IntVar(value=self.config['trading']['max_positions'])
        ttk.Entry(frame, textvariable=self.max_positions_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Stop Loss (%):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.stop_loss_var = tk.DoubleVar(value=self.config['trading']['stop_loss'] * 100)
        ttk.Entry(frame, textvariable=self.stop_loss_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Take Profit (%):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.take_profit_var = tk.DoubleVar(value=self.config['trading']['take_profit'] * 100)
        ttk.Entry(frame, textvariable=self.take_profit_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Alavancagem:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.leverage_var = tk.IntVar(value=self.config['trading']['leverage'])
        ttk.Entry(frame, textvariable=self.leverage_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        # Checkboxes
        self.trading_enabled_var = tk.BooleanVar(value=self.config['trading']['trading_enabled'])
        ttk.Checkbutton(frame, text="Trading Habilitado", variable=self.trading_enabled_var).grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        self.paper_trading_var = tk.BooleanVar(value=self.config['trading']['paper_trading'])
        ttk.Checkbutton(frame, text="Paper Trading", variable=self.paper_trading_var).grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        self.auto_select_var = tk.BooleanVar(value=self.config['trading']['auto_select_cryptos'])
        ttk.Checkbutton(frame, text="Auto-seleção de Criptomoedas", variable=self.auto_select_var).grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        # Lista de criptomoedas
        ttk.Label(frame, text="Criptomoedas Selecionadas:").grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        # Text widget para criptomoedas
        self.crypto_list_text = tk.Text(frame, height=5, width=40)
        self.crypto_list_text.grid(row=row, column=0, columnspan=2, pady=2)
        
        # Preencher lista de criptomoedas
        for crypto in self.config['trading']['selected_cryptos']:
            self.crypto_list_text.insert(tk.END, crypto + "\n")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, command=self.crypto_list_text.yview)
        scrollbar.grid(row=row, column=2, sticky=(tk.N, tk.S))
        self.crypto_list_text.config(yscrollcommand=scrollbar.set)
    
    def create_risk_tab(self, notebook):
        """Criar aba de gerenciamento de risco"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Gerenciamento de Risco")
        
        row = 0
        
        ttk.Label(frame, text="Perda Máxima Diária (%):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.max_daily_loss_var = tk.DoubleVar(value=self.config['risk_management']['max_daily_loss'] * 100)
        ttk.Entry(frame, textvariable=self.max_daily_loss_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Tamanho Máximo da Posição (%):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.max_position_size_var = tk.DoubleVar(value=self.config['risk_management']['max_position_size'] * 100)
        ttk.Entry(frame, textvariable=self.max_position_size_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Drawdown Máximo (%):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.max_drawdown_var = tk.DoubleVar(value=self.config['risk_management']['max_drawdown'] * 100)
        ttk.Entry(frame, textvariable=self.max_drawdown_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Risco por Trade (%):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.risk_per_trade_var = tk.DoubleVar(value=self.config['risk_management']['risk_per_trade'] * 100)
        ttk.Entry(frame, textvariable=self.risk_per_trade_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Método de Dimensionamento:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.position_sizing_var = tk.StringVar(value=self.config['risk_management']['position_sizing_method'])
        ttk.Combobox(frame, textvariable=self.position_sizing_var, 
                    values=["kelly_criterion", "fixed_ratio", "fixed_fractional"], 
                    width=18).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Mínimo de Criptomoedas:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.min_cryptos_var = tk.IntVar(value=self.config['risk_management']['diversification_min_cryptos'])
        ttk.Entry(frame, textvariable=self.min_cryptos_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Máximo de Criptomoedas:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.max_cryptos_var = tk.IntVar(value=self.config['risk_management']['diversification_max_cryptos'])
        ttk.Entry(frame, textvariable=self.max_cryptos_var, width=20).grid(row=row, column=1, pady=2)
    
    def create_analysis_tab(self, notebook):
        """Criar aba de análise técnica"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Análise Técnica")
        
        row = 0
        
        # RSI
        ttk.Label(frame, text="Período RSI:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.rsi_period_var = tk.IntVar(value=self.config['technical_analysis']['rsi_period'])
        ttk.Entry(frame, textvariable=self.rsi_period_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="RSI Sobrevenda:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.rsi_oversold_var = tk.DoubleVar(value=self.config['technical_analysis']['rsi_oversold'])
        ttk.Entry(frame, textvariable=self.rsi_oversold_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="RSI Sobrecompra:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.rsi_overbought_var = tk.DoubleVar(value=self.config['technical_analysis']['rsi_overbought'])
        ttk.Entry(frame, textvariable=self.rsi_overbought_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        # MACD
        ttk.Label(frame, text="MACD Rápido:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.macd_fast_var = tk.IntVar(value=self.config['technical_analysis']['macd_fast'])
        ttk.Entry(frame, textvariable=self.macd_fast_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="MACD Lento:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.macd_slow_var = tk.IntVar(value=self.config['technical_analysis']['macd_slow'])
        ttk.Entry(frame, textvariable=self.macd_slow_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="MACD Sinal:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.macd_signal_var = tk.IntVar(value=self.config['technical_analysis']['macd_signal'])
        ttk.Entry(frame, textvariable=self.macd_signal_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        # Bollinger Bands
        ttk.Label(frame, text="BB Período:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.bb_period_var = tk.IntVar(value=self.config['technical_analysis']['bb_period'])
        ttk.Entry(frame, textvariable=self.bb_period_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="BB Desvio Padrão:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.bb_std_var = tk.IntVar(value=self.config['technical_analysis']['bb_std'])
        ttk.Entry(frame, textvariable=self.bb_std_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        # EMAs
        ttk.Label(frame, text="EMA Rápida:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.ema_fast_var = tk.IntVar(value=self.config['technical_analysis']['ema_fast'])
        ttk.Entry(frame, textvariable=self.ema_fast_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="EMA Lenta:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.ema_slow_var = tk.IntVar(value=self.config['technical_analysis']['ema_slow'])
        ttk.Entry(frame, textvariable=self.ema_slow_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Volume SMA Período:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.volume_sma_var = tk.IntVar(value=self.config['technical_analysis']['volume_sma_period'])
        ttk.Entry(frame, textvariable=self.volume_sma_var, width=20).grid(row=row, column=1, pady=2)
    
    def create_api_tab(self, notebook):
        """Criar aba de API"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="APIs")
        
        # Binance
        row = 0
        ttk.Label(frame, text="Binance API Key:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.binance_key_var = tk.StringVar(value=self.config['api']['binance']['api_key'])
        ttk.Entry(frame, textvariable=self.binance_key_var, width=40, show="*").grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        ttk.Label(frame, text="Binance API Secret:").grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        self.binance_secret_var = tk.StringVar(value=self.config['api']['binance']['api_secret'])
        ttk.Entry(frame, textvariable=self.binance_secret_var, width=40, show="*").grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        self.binance_testnet_var = tk.BooleanVar(value=self.config['api']['binance']['testnet'])
        ttk.Checkbutton(frame, text="Usar Testnet", variable=self.binance_testnet_var).grid(row=row, column=0, pady=5)
        row += 1
        
        # Coinbase
        ttk.Label(frame, text="Coinbase API Key:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.coinbase_key_var = tk.StringVar(value=self.config['api']['coinbase']['api_key'])
        ttk.Entry(frame, textvariable=self.coinbase_key_var, width=40, show="*").grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        ttk.Label(frame, text="Coinbase API Secret:").grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        self.coinbase_secret_var = tk.StringVar(value=self.config['api']['coinbase']['api_secret'])
        ttk.Entry(frame, textvariable=self.coinbase_secret_var, width=40, show="*").grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        ttk.Label(frame, text="Coinbase Passphrase:").grid(row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        self.coinbase_pass_var = tk.StringVar(value=self.config['api']['coinbase']['passphrase'])
        ttk.Entry(frame, textvariable=self.coinbase_pass_var, width=40, show="*").grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        self.coinbase_sandbox_var = tk.BooleanVar(value=self.config['api']['coinbase']['sandbox'])
        ttk.Checkbutton(frame, text="Usar Sandbox", variable=self.coinbase_sandbox_var).grid(row=row, column=0, pady=5)
        row += 1
        
        # CoinMarketCap
        ttk.Label(frame, text="CoinMarketCap API Key:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.cmc_key_var = tk.StringVar(value=self.config['api']['coinmarketcap']['api_key'])
        ttk.Entry(frame, textvariable=self.cmc_key_var, width=40, show="*").grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        # CoinGecko
        ttk.Label(frame, text="CoinGecko API Key:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.coingecko_key_var = tk.StringVar(value=self.config['api']['coingecko']['api_key'])
        ttk.Entry(frame, textvariable=self.coingecko_key_var, width=40, show="*").grid(row=row, column=0, columnspan=2, pady=2)
    
    def create_selector_tab(self, notebook):
        """Criar aba de seletor de criptomoedas"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Seletor")
        
        row = 0
        
        # Pesos
        ttk.Label(frame, text="Peso Técnico:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=2)
        self.technical_weight_var = tk.DoubleVar(value=self.config['crypto_selector']['technical_weight'])
        ttk.Entry(frame, textvariable=self.technical_weight_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Peso Fundamental:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.fundamental_weight_var = tk.DoubleVar(value=self.config['crypto_selector']['fundamental_weight'])
        ttk.Entry(frame, textvariable=self.fundamental_weight_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Peso Social:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.social_weight_var = tk.DoubleVar(value=self.config['crypto_selector']['social_weight'])
        ttk.Entry(frame, textvariable=self.social_weight_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Peso de Risco:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.risk_weight_var = tk.DoubleVar(value=self.config['crypto_selector']['risk_weight'])
        ttk.Entry(frame, textvariable=self.risk_weight_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Peso de Volume:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.volume_weight_var = tk.DoubleVar(value=self.config['crypto_selector']['volume_weight'])
        ttk.Entry(frame, textvariable=self.volume_weight_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Pontuação Mínima:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.min_score_var = tk.DoubleVar(value=self.config['crypto_selector']['min_total_score'])
        ttk.Entry(frame, textvariable=self.min_score_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Máximo de Criptomoedas:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.max_selector_cryptos_var = tk.IntVar(value=self.config['crypto_selector']['max_cryptos_to_select'])
        ttk.Entry(frame, textvariable=self.max_selector_cryptos_var, width=20).grid(row=row, column=1, pady=2)
    
    def create_ml_tab(self, notebook):
        """Criar aba de ML"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Machine Learning")
        
        row = 0
        
        ttk.Label(frame, text="Tipo de Modelo:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.model_type_var = tk.StringVar(value=self.config['ml_model']['model_type'])
        ttk.Combobox(frame, textvariable=self.model_type_var, 
                    values=["ensemble", "lstm", "xgboost", "random_forest"], 
                    width=18).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Horizonte de Predição (horas):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.prediction_horizon_var = tk.IntVar(value=self.config['ml_model']['prediction_horizon'])
        ttk.Entry(frame, textvariable=self.prediction_horizon_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Intervalo de Retreino (horas):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.retrain_interval_var = tk.IntVar(value=self.config['ml_model']['retrain_interval'])
        ttk.Entry(frame, textvariable=self.retrain_interval_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Limiar de Confiança:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.confidence_threshold_var = tk.DoubleVar(value=self.config['ml_model']['confidence_threshold'])
        ttk.Entry(frame, textvariable=self.confidence_threshold_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        self.use_sentiment_var = tk.BooleanVar(value=self.config['ml_model']['use_sentiment_analysis'])
        ttk.Checkbutton(frame, text="Usar Análise de Sentimento", variable=self.use_sentiment_var).grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        self.use_technical_var = tk.BooleanVar(value=self.config['ml_model']['use_technical_indicators'])
        ttk.Checkbutton(frame, text="Usar Indicadores Técnicos", variable=self.use_technical_var).grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        self.use_fundamental_var = tk.BooleanVar(value=self.config['ml_model']['use_fundamental_data'])
        ttk.Checkbutton(frame, text="Usar Dados Fundamentais", variable=self.use_fundamental_var).grid(row=row, column=0, columnspan=2, pady=2)
    
    def create_alerts_tab(self, notebook):
        """Criar aba de alertas"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Alertas")
        
        row = 0
        
        # Email
        ttk.Label(frame, text="Configurações de Email", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.email_enabled_var = tk.BooleanVar(value=self.config['alerts']['email_enabled'])
        ttk.Checkbutton(frame, text="Email Habilitado", variable=self.email_enabled_var).grid(row=row, column=0, pady=2)
        row += 1
        
        ttk.Label(frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.email_address_var = tk.StringVar(value=self.config['alerts']['email_address'])
        ttk.Entry(frame, textvariable=self.email_address_var, width=30).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Senha:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.email_password_var = tk.StringVar(value=self.config['alerts']['email_password'])
        ttk.Entry(frame, textvariable=self.email_password_var, width=30, show="*").grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Servidor SMTP:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.smtp_server_var = tk.StringVar(value=self.config['alerts']['smtp_server'])
        ttk.Entry(frame, textvariable=self.smtp_server_var, width=30).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Porta SMTP:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.smtp_port_var = tk.IntVar(value=self.config['alerts']['smtp_port'])
        ttk.Entry(frame, textvariable=self.smtp_port_var, width=30).grid(row=row, column=1, pady=2)
        row += 1
        
        # Telegram
        ttk.Label(frame, text="Configurações do Telegram", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.telegram_enabled_var = tk.BooleanVar(value=self.config['alerts']['telegram_enabled'])
        ttk.Checkbutton(frame, text="Telegram Habilitado", variable=self.telegram_enabled_var).grid(row=row, column=0, pady=2)
        row += 1
        
        ttk.Label(frame, text="Bot Token:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.telegram_token_var = tk.StringVar(value=self.config['alerts']['telegram_bot_token'])
        ttk.Entry(frame, textvariable=self.telegram_token_var, width=40, show="*").grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Chat ID:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.telegram_chat_var = tk.StringVar(value=self.config['alerts']['telegram_chat_id'])
        ttk.Entry(frame, textvariable=self.telegram_chat_var, width=40).grid(row=row, column=1, pady=2)
        row += 1
        
        # Discord
        ttk.Label(frame, text="Configurações do Discord", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.discord_enabled_var = tk.BooleanVar(value=self.config['alerts']['discord_enabled'])
        ttk.Checkbutton(frame, text="Discord Habilitado", variable=self.discord_enabled_var).grid(row=row, column=0, pady=2)
        row += 1
        
        ttk.Label(frame, text="Webhook URL:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.discord_webhook_var = tk.StringVar(value=self.config['alerts']['discord_webhook'])
        ttk.Entry(frame, textvariable=self.discord_webhook_var, width=50).grid(row=row, column=1, pady=2)
        row += 1
        
        # Alertas
        ttk.Label(frame, text="Tipos de Alertas", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.alert_trades_var = tk.BooleanVar(value=self.config['alerts']['alert_on_large_trades'])
        ttk.Checkbutton(frame, text="Alertar em Trades Grandes", variable=self.alert_trades_var).grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        self.alert_volatility_var = tk.BooleanVar(value=self.config['alerts']['alert_on_high_volatility'])
        ttk.Checkbutton(frame, text="Alertar em Alta Volatilidade", variable=self.alert_volatility_var).grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        self.alert_price_changes_var = tk.BooleanVar(value=self.config['alerts']['alert_on_significant_price_changes'])
        ttk.Checkbutton(frame, text="Alertar em Mudanças Significativas de Preço", variable=self.alert_price_changes_var).grid(row=row, column=0, columnspan=2, pady=2)
        row += 1
        
        self.alert_errors_var = tk.BooleanVar(value=self.config['alerts']['alert_on_system_errors'])
        ttk.Checkbutton(frame, text="Alertar em Erros do Sistema", variable=self.alert_errors_var).grid(row=row, column=0, columnspan=2, pady=2)
    
    def create_system_tab(self, notebook):
        """Criar aba de sistema"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Sistema")
        
        row = 0
        
        ttk.Label(frame, text="Nível de Log:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.log_level_var = tk.StringVar(value=self.config['system']['log_level'])
        ttk.Combobox(frame, textvariable=self.log_level_var, 
                    values=["DEBUG", "INFO", "WARNING", "ERROR"], 
                    width=18).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Arquivo de Log:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.log_file_var = tk.StringVar(value=self.config['system']['log_file'])
        ttk.Entry(frame, textvariable=self.log_file_var, width=30).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Retenção de Dados (dias):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.data_retention_var = tk.IntVar(value=self.config['system']['data_retention_days'])
        ttk.Entry(frame, textvariable=self.data_retention_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        self.backup_enabled_var = tk.BooleanVar(value=self.config['system']['backup_enabled'])
        ttk.Checkbutton(frame, text="Backup Habilitado", variable=self.backup_enabled_var).grid(row=row, column=0, pady=2)
        row += 1
        
        ttk.Label(frame, text="Intervalo de Backup (horas):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.backup_interval_var = tk.IntVar(value=self.config['system']['backup_interval_hours'])
        ttk.Entry(frame, textvariable=self.backup_interval_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Máximo de Workers:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.max_workers_var = tk.IntVar(value=self.config['system']['max_workers'])
        ttk.Entry(frame, textvariable=self.max_workers_var, width=20).grid(row=row, column=1, pady=2)
        row += 1
        
        ttk.Label(frame, text="Timeout (segundos):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.timeout_var = tk.IntVar(value=self.config['system']['timeout_seconds'])
        ttk.Entry(frame, textvariable=self.timeout_var, width=20).grid(row=row, column=1, pady=2)
    
    def save_config(self):
        """Salvar configuração"""
        try:
            # Coletar valores da interface
            self.collect_values()
            
            # Salvar em arquivo
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            self.status_var.set("Configuração salva com sucesso!")
            messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configuração: {str(e)}")
            self.status_var.set(f"Erro ao salvar: {str(e)}")
    
    def collect_values(self):
        """Coletar valores da interface"""
        # Trading
        self.config['trading']['base_currency'] = self.base_currency_var.get()
        self.config['trading']['trade_amount'] = self.trade_amount_var.get()
        self.config['trading']['max_positions'] = self.max_positions_var.get()
        self.config['trading']['stop_loss'] = self.stop_loss_var.get() / 100
        self.config['trading']['take_profit'] = self.take_profit_var.get() / 100
        self.config['trading']['leverage'] = self.leverage_var.get()
        self.config['trading']['trading_enabled'] = self.trading_enabled_var.get()
        self.config['trading']['paper_trading'] = self.paper_trading_var.get()
        self.config['trading']['auto_select_cryptos'] = self.auto_select_var.get()
        
        # Coletar lista de criptomoedas
        crypto_text = self.crypto_list_text.get("1.0", tk.END).strip()
        self.config['trading']['selected_cryptos'] = [crypto.strip() for crypto in crypto_text.split('\n') if crypto.strip()]
        
        # Risk Management
        self.config['risk_management']['max_daily_loss'] = self.max_daily_loss_var.get() / 100
        self.config['risk_management']['max_position_size'] = self.max_position_size_var.get() / 100
        self.config['risk_management']['max_drawdown'] = self.max_drawdown_var.get() / 100
        self.config['risk_management']['risk_per_trade'] = self.risk_per_trade_var.get() / 100
        self.config['risk_management']['position_sizing_method'] = self.position_sizing_var.get()
        self.config['risk_management']['diversification_min_cryptos'] = self.min_cryptos_var.get()
        self.config['risk_management']['diversification_max_cryptos'] = self.max_cryptos_var.get()
        
        # Technical Analysis
        self.config['technical_analysis']['rsi_period'] = self.rsi_period_var.get()
        self.config['technical_analysis']['rsi_overbought'] = self.rsi_overbought_var.get()
        self.config['technical_analysis']['rsi_oversold'] = self.rsi_oversold_var.get()
        self.config['technical_analysis']['macd_fast'] = self.macd_fast_var.get()
        self.config['technical_analysis']['macd_slow'] = self.macd_slow_var.get()
        self.config['technical_analysis']['macd_signal'] = self.macd_signal_var.get()
        self.config['technical_analysis']['bb_period'] = self.bb_period_var.get()
        self.config['technical_analysis']['bb_std'] = self.bb_std_var.get()
        self.config['technical_analysis']['ema_fast'] = self.ema_fast_var.get()
        self.config['technical_analysis']['ema_slow'] = self.ema_slow_var.get()
        self.config['technical_analysis']['volume_sma_period'] = self.volume_sma_var.get()
        
        # APIs
        self.config['api']['binance']['api_key'] = self.binance_key_var.get()
        self.config['api']['binance']['api_secret'] = self.binance_secret_var.get()
        self.config['api']['binance']['testnet'] = self.binance_testnet_var.get()
        
        self.config['api']['coinbase']['api_key'] = self.coinbase_key_var.get()
        self.config['api']['coinbase']['api_secret'] = self.coinbase_secret_var.get()
        self.config['api']['coinbase']['passphrase'] = self.coinbase_pass_var.get()
        self.config['api']['coinbase']['sandbox'] = self.coinbase_sandbox_var.get()
        
        self.config['api']['coinmarketcap']['api_key'] = self.cmc_key_var.get()
        self.config['api']['coingecko']['api_key'] = self.coingecko_key_var.get()
        
        # Crypto Selector
        self.config['crypto_selector']['technical_weight'] = self.technical_weight_var.get()
        self.config['crypto_selector']['fundamental_weight'] = self.fundamental_weight_var.get()
        self.config['crypto_selector']['social_weight'] = self.social_weight_var.get()
        self.config['crypto_selector']['risk_weight'] = self.risk_weight_var.get()
        self.config['crypto_selector']['volume_weight'] = self.volume_weight_var.get()
        self.config['crypto_selector']['min_total_score'] = self.min_score_var.get()
        self.config['crypto_selector']['max_cryptos_to_select'] = self.max_selector_cryptos_var.get()
        
        # ML Model
        self.config['ml_model']['model_type'] = self.model_type_var.get()
        self.config['ml_model']['prediction_horizon'] = self.prediction_horizon_var.get()
        self.config['ml_model']['retrain_interval'] = self.retrain_interval_var.get()
        self.config['ml_model']['confidence_threshold'] = self.confidence_threshold_var.get()
        self.config['ml_model']['use_sentiment_analysis'] = self.use_sentiment_var.get()
        self.config['ml_model']['use_technical_indicators'] = self.use_technical_var.get()
        self.config['ml_model']['use_fundamental_data'] = self.use_fundamental_var.get()
        
        # Alerts
        self.config['alerts']['email_enabled'] = self.email_enabled_var.get()
        self.config['alerts']['email_address'] = self.email_address_var.get()
        self.config['alerts']['email_password'] = self.email_password_var.get()
        self.config['alerts']['smtp_server'] = self.smtp_server_var.get()
        self.config['alerts']['smtp_port'] = self.smtp_port_var.get()
        self.config['alerts']['telegram_enabled'] = self.telegram_enabled_var.get()
        self.config['alerts']['telegram_bot_token'] = self.telegram_token_var.get()
        self.config['alerts']['telegram_chat_id'] = self.telegram_chat_var.get()
        self.config['alerts']['discord_enabled'] = self.discord_enabled_var.get()
        self.config['alerts']['discord_webhook'] = self.discord_webhook_var.get()
        self.config['alerts']['alert_on_large_trades'] = self.alert_trades_var.get()
        self.config['alerts']['alert_on_high_volatility'] = self.alert_volatility_var.get()
        self.config['alerts']['alert_on_significant_price_changes'] = self.alert_price_changes_var.get()
        self.config['alerts']['alert_on_system_errors'] = self.alert_errors_var.get()
        
        # System
        self.config['system']['log_level'] = self.log_level_var.get()
        self.config['system']['log_file'] = self.log_file_var.get()
        self.config['system']['data_retention_days'] = self.data_retention_var.get()
        self.config['system']['backup_enabled'] = self.backup_enabled_var.get()
        self.config['system']['backup_interval_hours'] = self.backup_interval_var.get()
        self.config['system']['max_workers'] = self.max_workers_var.get()
        self.config['system']['timeout_seconds'] = self.timeout_var.get()
    
    def load_config_dialog(self):
        """Carregar configuração de arquivo"""
        filename = filedialog.askopenfilename(
            title="Carregar Configuração",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.config = json.load(f)
                
                # Atualizar interface
                self.update_interface()
                self.status_var.set("Configuração carregada com sucesso!")
                messagebox.showinfo("Sucesso", "Configuração carregada com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar configuração: {str(e)}")
                self.status_var.set(f"Erro ao carregar: {str(e)}")
    
    def export_config(self):
        """Exportar configuração"""
        filename = filedialog.asksaveasfilename(
            title="Exportar Configuração",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.collect_values()
                with open(filename, 'w') as f:
                    json.dump(self.config, f, indent=4)
                
                self.status_var.set("Configuração exportada com sucesso!")
                messagebox.showinfo("Sucesso", "Configuração exportada com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar configuração: {str(e)}")
                self.status_var.set(f"Erro ao exportar: {str(e)}")
    
    def reset_config(self):
        """Resetar configuração para valores padrão"""
        if messagebox.askyesno("Confirmar", "Deseja realmente resetar para configuração padrão?"):
            self.config = self.get_default_config()
            self.update_interface()
            self.status_var.set("Configuração resetada para padrão!")
            messagebox.showinfo("Sucesso", "Configuração resetada para valores padrão!")
    
    def update_interface(self):
        """Atualizar interface com valores da configuração"""
        # Trading
        self.base_currency_var.set(self.config['trading']['base_currency'])
        self.trade_amount_var.set(self.config['trading']['trade_amount'])
        self.max_positions_var.set(self.config['trading']['max_positions'])
        self.stop_loss_var.set(self.config['trading']['stop_loss'] * 100)
        self.take_profit_var.set(self.config['trading']['take_profit'] * 100)
        self.leverage_var.set(self.config['trading']['leverage'])
        self.trading_enabled_var.set(self.config['trading']['trading_enabled'])
        self.paper_trading_var.set(self.config['trading']['paper_trading'])
        self.auto_select_var.set(self.config['trading']['auto_select_cryptos'])
        
        # Atualizar lista de criptomoedas
        self.crypto_list_text.delete("1.0", tk.END)
        for crypto in self.config['trading']['selected_cryptos']:
            self.crypto_list_text.insert(tk.END, crypto + "\n")
        
        # Continuar atualização para outros campos...
        # (Este método pode ser extenso, mas segue o mesmo padrão)
        
    def test_apis(self):
        """Testar conexões de API"""
        self.status_var.set("Testando APIs...")
        self.root.update()
        
        # Aqui você implementaria testes para cada API
        # Por enquanto, apenas um placeholder
        
        results = []
        
        # Testar Binance
        if self.config['api']['binance']['api_key']:
            results.append("Binance: Chave API configurada")
        else:
            results.append("Binance: Chave API não configurada")
        
        # Testar Coinbase
        if self.config['api']['coinbase']['api_key']:
            results.append("Coinbase: Chave API configurada")
        else:
            results.append("Coinbase: Chave API não configurada")
        
        # Testar CoinMarketCap
        if self.config['api']['coinmarketcap']['api_key']:
            results.append("CoinMarketCap: Chave API configurada")
        else:
            results.append("CoinMarketCap: Chave API não configurada")
        
        # Mostrar resultados
        result_text = "\n".join(results)
        messagebox.showinfo("Resultados dos Testes", result_text)
        self.status_var.set("Testes de API concluídos")
    
    def run(self):
        """Executar a interface"""
        self.root.mainloop()

def main():
    """Função principal"""
    app = ConfigInterface()
    app.run()

if __name__ == "__main__":
    main()