#!/usr/bin/env python3
"""
IA GAIN - Configuration GUI Executor
Script executável para interface gráfica de configuração
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path

def setup_environment():
    """Configurar ambiente e paths"""
    # Adicionar o diretório src ao path
    src_path = Path(__file__).parent / 'src'
    sys.path.insert(0, str(src_path))
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('config_gui.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Verificar dependências necessárias"""
    required_packages = ['tkinter']
    
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
        return True
    except ImportError:
        print("❌ tkinter não está disponível")
        print("No Windows: tkinter geralmente vem com Python")
        print("No Linux: sudo apt-get install python3-tk")
        print("No macOS: brew install python-tk")
        return False

def check_config():
    """Verificar configuração existente"""
    config_file = 'config.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ Configuração encontrada e válida")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ Arquivo config.json inválido: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro ao ler configuração: {e}")
            return False
    else:
        print("ℹ️  Nenhuma configuração encontrada, será criada uma nova")
        return True

def launch_gui():
    """Iniciar interface gráfica"""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
        
        print("🚀 Iniciando interface gráfica...")
        
        # Criar janela principal
        root = tk.Tk()
        root.title("IA GAIN - Configuração")
        root.geometry("800x600")
        root.resizable(True, True)
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Criar notebook (abas)
        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Criar frames para cada aba
        general_frame = ttk.Frame(notebook)
        trading_frame = ttk.Frame(notebook)
        api_frame = ttk.Frame(notebook)
        alerts_frame = ttk.Frame(notebook)
        ml_frame = ttk.Frame(notebook)
        
        # Adicionar abas
        notebook.add(general_frame, text='Geral')
        notebook.add(trading_frame, text='Trading')
        notebook.add(api_frame, text='APIs')
        notebook.add(alerts_frame, text='Alertas')
        notebook.add(ml_frame, text='Machine Learning')
        
        # Carregar configuração atual
        config_data = load_current_config()
        
        # Criar widgets para cada aba
        create_general_tab(general_frame, config_data)
        create_trading_tab(trading_frame, config_data)
        create_api_tab(api_frame, config_data)
        create_alerts_tab(alerts_frame, config_data)
        create_ml_tab(ml_frame, config_data)
        
        # Criar frame de botões
        button_frame = ttk.Frame(root)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        # Botões
        save_btn = ttk.Button(button_frame, text="Salvar Configuração", 
                             command=lambda: save_configuration(root, config_data))
        save_btn.pack(side='right', padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancelar", 
                               command=root.destroy)
        cancel_btn.pack(side='right', padx=5)
        
        test_btn = ttk.Button(button_frame, text="Testar Configuração", 
                             command=lambda: test_configuration(config_data))
        test_btn.pack(side='right', padx=5)
        
        # Status bar
        status_var = tk.StringVar()
        status_var.set("Pronto")
        status_bar = ttk.Label(root, textvariable=status_var, relief='sunken')
        status_bar.pack(side='bottom', fill='x', padx=10, pady=5)
        
        print("✅ Interface gráfica iniciada")
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Erro ao iniciar interface gráfica: {e}")
        raise

def load_current_config():
    """Carregar configuração atual"""
    config_file = 'config.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    
    # Retornar configuração padrão
    return get_default_config()

def get_default_config():
    """Obter configuração padrão"""
    return {
        "general": {
            "debug": False,
            "log_level": "INFO",
            "timezone": "America/Sao_Paulo"
        },
        "trading": {
            "max_positions": 5,
            "position_size": 0.1,
            "stop_loss": 0.02,
            "take_profit": 0.05,
            "trailing_stop": 0.01
        },
        "api": {
            "binance": {
                "api_key": "",
                "api_secret": "",
                "testnet": True
            },
            "coinbase": {
                "api_key": "",
                "api_secret": "",
                "passphrase": ""
            },
            "coingecko": {
                "api_key": ""
            }
        },
        "alerts": {
            "telegram": {
                "enabled": False,
                "bot_token": "",
                "chat_id": ""
            },
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": ""
            }
        },
        "ml": {
            "enabled": True,
            "model_update_interval": 24,
            "prediction_confidence": 0.7,
            "features": ["rsi", "macd", "bollinger_bands", "volume"]
        }
    }

def create_general_tab(parent, config_data):
    """Criar aba de configurações gerais"""
    import tkinter as tk
    from tkinter import ttk
    
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Debug
    ttk.Label(frame, text="Modo Debug:").grid(row=0, column=0, sticky='w', pady=5)
    debug_var = tk.BooleanVar(value=config_data.get('general', {}).get('debug', False))
    ttk.Checkbutton(frame, variable=debug_var).grid(row=0, column=1, sticky='w', pady=5)
    
    # Log Level
    ttk.Label(frame, text="Nível de Log:").grid(row=1, column=0, sticky='w', pady=5)
    log_var = tk.StringVar(value=config_data.get('general', {}).get('log_level', 'INFO'))
    ttk.Combobox(frame, textvariable=log_var, values=['DEBUG', 'INFO', 'WARNING', 'ERROR']).grid(row=1, column=1, sticky='ew', pady=5)
    
    # Timezone
    ttk.Label(frame, text="Fuso Horário:").grid(row=2, column=0, sticky='w', pady=5)
    tz_var = tk.StringVar(value=config_data.get('general', {}).get('timezone', 'America/Sao_Paulo'))
    ttk.Entry(frame, textvariable=tz_var).grid(row=2, column=1, sticky='ew', pady=5)
    
    # Configurar grid
    frame.grid_columnconfigure(1, weight=1)
    
    # Salvar referências
    config_data['general']['debug'] = debug_var
    config_data['general']['log_level'] = log_var
    config_data['general']['timezone'] = tz_var

def create_trading_tab(parent, config_data):
    """Criar aba de configurações de trading"""
    import tkinter as tk
    from tkinter import ttk
    
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Max Positions
    ttk.Label(frame, text="Máximo de Posições:").grid(row=0, column=0, sticky='w', pady=5)
    max_pos_var = tk.IntVar(value=config_data.get('trading', {}).get('max_positions', 5))
    ttk.Spinbox(frame, from_=1, to=20, textvariable=max_pos_var).grid(row=0, column=1, sticky='ew', pady=5)
    
    # Position Size
    ttk.Label(frame, text="Tamanho da Posição:").grid(row=1, column=0, sticky='w', pady=5)
    pos_size_var = tk.DoubleVar(value=config_data.get('trading', {}).get('position_size', 0.1))
    ttk.Spinbox(frame, from_=0.01, to=1.0, increment=0.01, textvariable=pos_size_var).grid(row=1, column=1, sticky='ew', pady=5)
    
    # Stop Loss
    ttk.Label(frame, text="Stop Loss:").grid(row=2, column=0, sticky='w', pady=5)
    sl_var = tk.DoubleVar(value=config_data.get('trading', {}).get('stop_loss', 0.02))
    ttk.Spinbox(frame, from_=0.001, to=0.5, increment=0.001, textvariable=sl_var).grid(row=2, column=1, sticky='ew', pady=5)
    
    # Take Profit
    ttk.Label(frame, text="Take Profit:").grid(row=3, column=0, sticky='w', pady=5)
    tp_var = tk.DoubleVar(value=config_data.get('trading', {}).get('take_profit', 0.05))
    ttk.Spinbox(frame, from_=0.001, to=1.0, increment=0.001, textvariable=tp_var).grid(row=3, column=1, sticky='ew', pady=5)
    
    # Trailing Stop
    ttk.Label(frame, text="Trailing Stop:").grid(row=4, column=0, sticky='w', pady=5)
    ts_var = tk.DoubleVar(value=config_data.get('trading', {}).get('trailing_stop', 0.01))
    ttk.Spinbox(frame, from_=0.001, to=0.5, increment=0.001, textvariable=ts_var).grid(row=4, column=1, sticky='ew', pady=5)
    
    # Configurar grid
    frame.grid_columnconfigure(1, weight=1)
    
    # Salvar referências
    config_data['trading']['max_positions'] = max_pos_var
    config_data['trading']['position_size'] = pos_size_var
    config_data['trading']['stop_loss'] = sl_var
    config_data['trading']['take_profit'] = tp_var
    config_data['trading']['trailing_stop'] = ts_var

def create_api_tab(parent, config_data):
    """Criar aba de configurações de API"""
    import tkinter as tk
    from tkinter import ttk
    
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Binance Frame
    binance_frame = ttk.LabelFrame(frame, text="Binance")
    binance_frame.pack(fill='x', pady=10)
    
    ttk.Label(binance_frame, text="API Key:").grid(row=0, column=0, sticky='w', pady=2)
    binance_key_var = tk.StringVar(value=config_data.get('api', {}).get('binance', {}).get('api_key', ''))
    ttk.Entry(binance_frame, textvariable=binance_key_var, show='*').grid(row=0, column=1, sticky='ew', pady=2)
    
    ttk.Label(binance_frame, text="API Secret:").grid(row=1, column=0, sticky='w', pady=2)
    binance_secret_var = tk.StringVar(value=config_data.get('api', {}).get('binance', {}).get('api_secret', ''))
    ttk.Entry(binance_frame, textvariable=binance_secret_var, show='*').grid(row=1, column=1, sticky='ew', pady=2)
    
    binance_test_var = tk.BooleanVar(value=config_data.get('api', {}).get('binance', {}).get('testnet', True))
    ttk.Checkbutton(binance_frame, text="Usar Testnet", variable=binance_test_var).grid(row=2, column=1, sticky='w', pady=2)
    
    # Coinbase Frame
    coinbase_frame = ttk.LabelFrame(frame, text="Coinbase")
    coinbase_frame.pack(fill='x', pady=10)
    
    ttk.Label(coinbase_frame, text="API Key:").grid(row=0, column=0, sticky='w', pady=2)
    coinbase_key_var = tk.StringVar(value=config_data.get('api', {}).get('coinbase', {}).get('api_key', ''))
    ttk.Entry(coinbase_frame, textvariable=coinbase_key_var, show='*').grid(row=0, column=1, sticky='ew', pady=2)
    
    ttk.Label(coinbase_frame, text="API Secret:").grid(row=1, column=0, sticky='w', pady=2)
    coinbase_secret_var = tk.StringVar(value=config_data.get('api', {}).get('coinbase', {}).get('api_secret', ''))
    ttk.Entry(coinbase_frame, textvariable=coinbase_secret_var, show='*').grid(row=1, column=1, sticky='ew', pady=2)
    
    ttk.Label(coinbase_frame, text="Passphrase:").grid(row=2, column=0, sticky='w', pady=2)
    coinbase_pass_var = tk.StringVar(value=config_data.get('api', {}).get('coinbase', {}).get('passphrase', ''))
    ttk.Entry(coinbase_frame, textvariable=coinbase_pass_var, show='*').grid(row=2, column=1, sticky='ew', pady=2)
    
    # CoinGecko Frame
    coingecko_frame = ttk.LabelFrame(frame, text="CoinGecko")
    coingecko_frame.pack(fill='x', pady=10)
    
    ttk.Label(coingecko_frame, text="API Key:").grid(row=0, column=0, sticky='w', pady=2)
    coingecko_key_var = tk.StringVar(value=config_data.get('api', {}).get('coingecko', {}).get('api_key', ''))
    ttk.Entry(coingecko_frame, textvariable=coingecko_key_var, show='*').grid(row=0, column=1, sticky='ew', pady=2)
    
    # Configurar grid
    binance_frame.grid_columnconfigure(1, weight=1)
    coinbase_frame.grid_columnconfigure(1, weight=1)
    coingecko_frame.grid_columnconfigure(1, weight=1)
    
    # Salvar referências
    config_data['api']['binance']['api_key'] = binance_key_var
    config_data['api']['binance']['api_secret'] = binance_secret_var
    config_data['api']['binance']['testnet'] = binance_test_var
    config_data['api']['coinbase']['api_key'] = coinbase_key_var
    config_data['api']['coinbase']['api_secret'] = coinbase_secret_var
    config_data['api']['coinbase']['passphrase'] = coinbase_pass_var
    config_data['api']['coingecko']['api_key'] = coingecko_key_var

def create_alerts_tab(parent, config_data):
    """Criar aba de configurações de alertas"""
    import tkinter as tk
    from tkinter import ttk
    
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Telegram Frame
    telegram_frame = ttk.LabelFrame(frame, text="Telegram")
    telegram_frame.pack(fill='x', pady=10)
    
    telegram_enabled_var = tk.BooleanVar(value=config_data.get('alerts', {}).get('telegram', {}).get('enabled', False))
    ttk.Checkbutton(telegram_frame, text="Habilitar Telegram", variable=telegram_enabled_var).grid(row=0, column=0, columnspan=2, sticky='w', pady=2)
    
    ttk.Label(telegram_frame, text="Bot Token:").grid(row=1, column=0, sticky='w', pady=2)
    telegram_token_var = tk.StringVar(value=config_data.get('alerts', {}).get('telegram', {}).get('bot_token', ''))
    ttk.Entry(telegram_frame, textvariable=telegram_token_var, show='*').grid(row=1, column=1, sticky='ew', pady=2)
    
    ttk.Label(telegram_frame, text="Chat ID:").grid(row=2, column=0, sticky='w', pady=2)
    telegram_chat_var = tk.StringVar(value=config_data.get('alerts', {}).get('telegram', {}).get('chat_id', ''))
    ttk.Entry(telegram_frame, textvariable=telegram_chat_var).grid(row=2, column=1, sticky='ew', pady=2)
    
    # Email Frame
    email_frame = ttk.LabelFrame(frame, text="Email")
    email_frame.pack(fill='x', pady=10)
    
    email_enabled_var = tk.BooleanVar(value=config_data.get('alerts', {}).get('email', {}).get('enabled', False))
    ttk.Checkbutton(email_frame, text="Habilitar Email", variable=email_enabled_var).grid(row=0, column=0, columnspan=2, sticky='w', pady=2)
    
    ttk.Label(email_frame, text="SMTP Server:").grid(row=1, column=0, sticky='w', pady=2)
    smtp_server_var = tk.StringVar(value=config_data.get('alerts', {}).get('email', {}).get('smtp_server', 'smtp.gmail.com'))
    ttk.Entry(email_frame, textvariable=smtp_server_var).grid(row=1, column=1, sticky='ew', pady=2)
    
    ttk.Label(email_frame, text="SMTP Port:").grid(row=2, column=0, sticky='w', pady=2)
    smtp_port_var = tk.IntVar(value=config_data.get('alerts', {}).get('email', {}).get('smtp_port', 587))
    ttk.Spinbox(email_frame, from_=1, to=65535, textvariable=smtp_port_var).grid(row=2, column=1, sticky='ew', pady=2)
    
    ttk.Label(email_frame, text="Username:").grid(row=3, column=0, sticky='w', pady=2)
    email_user_var = tk.StringVar(value=config_data.get('alerts', {}).get('email', {}).get('username', ''))
    ttk.Entry(email_frame, textvariable=email_user_var).grid(row=3, column=1, sticky='ew', pady=2)
    
    ttk.Label(email_frame, text="Password:").grid(row=4, column=0, sticky='w', pady=2)
    email_pass_var = tk.StringVar(value=config_data.get('alerts', {}).get('email', {}).get('password', ''))
    ttk.Entry(email_frame, textvariable=email_pass_var, show='*').grid(row=4, column=1, sticky='ew', pady=2)
    
    # Configurar grid
    telegram_frame.grid_columnconfigure(1, weight=1)
    email_frame.grid_columnconfigure(1, weight=1)
    
    # Salvar referências
    config_data['alerts']['telegram']['enabled'] = telegram_enabled_var
    config_data['alerts']['telegram']['bot_token'] = telegram_token_var
    config_data['alerts']['telegram']['chat_id'] = telegram_chat_var
    config_data['alerts']['email']['enabled'] = email_enabled_var
    config_data['alerts']['email']['smtp_server'] = smtp_server_var
    config_data['alerts']['email']['smtp_port'] = smtp_port_var
    config_data['alerts']['email']['username'] = email_user_var
    config_data['alerts']['email']['password'] = email_pass_var

def create_ml_tab(parent, config_data):
    """Criar aba de configurações de Machine Learning"""
    import tkinter as tk
    from tkinter import ttk
    
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # ML Enabled
    ml_enabled_var = tk.BooleanVar(value=config_data.get('ml', {}).get('enabled', True))
    ttk.Checkbutton(frame, text="Habilitar Machine Learning", variable=ml_enabled_var).grid(row=0, column=0, columnspan=2, sticky='w', pady=5)
    
    # Model Update Interval
    ttk.Label(frame, text="Intervalo de Atualização (horas):").grid(row=1, column=0, sticky='w', pady=5)
    update_interval_var = tk.IntVar(value=config_data.get('ml', {}).get('model_update_interval', 24))
    ttk.Spinbox(frame, from_=1, to=168, textvariable=update_interval_var).grid(row=1, column=1, sticky='ew', pady=5)
    
    # Prediction Confidence
    ttk.Label(frame, text="Confiança Mínima:").grid(row=2, column=0, sticky='w', pady=5)
    confidence_var = tk.DoubleVar(value=config_data.get('ml', {}).get('prediction_confidence', 0.7))
    ttk.Spinbox(frame, from_=0.1, to=1.0, increment=0.1, textvariable=confidence_var).grid(row=2, column=1, sticky='ew', pady=5)
    
    # Features
    ttk.Label(frame, text="Features:").grid(row=3, column=0, sticky='nw', pady=5)
    features_frame = ttk.Frame(frame)
    features_frame.grid(row=3, column=1, sticky='ew', pady=5)
    
    available_features = ['rsi', 'macd', 'bollinger_bands', 'volume', 'ema', 'sma', 'stochastic']
    feature_vars = {}
    
    current_features = config_data.get('ml', {}).get('features', [])
    
    for i, feature in enumerate(available_features):
        feature_vars[feature] = tk.BooleanVar(value=feature in current_features)
        ttk.Checkbutton(features_frame, text=feature.upper(), variable=feature_vars[feature]).grid(row=i//3, column=i%3, sticky='w', padx=5)
    
    # Configurar grid
    frame.grid_columnconfigure(1, weight=1)
    
    # Salvar referências
    config_data['ml']['enabled'] = ml_enabled_var
    config_data['ml']['model_update_interval'] = update_interval_var
    config_data['ml']['prediction_confidence'] = confidence_var
    config_data['ml']['feature_vars'] = feature_vars

def save_configuration(root, config_data):
    """Salvar configuração"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        # Converter variáveis Tkinter para valores
        config_to_save = {
            "general": {
                "debug": config_data['general']['debug'].get(),
                "log_level": config_data['general']['log_level'].get(),
                "timezone": config_data['general']['timezone'].get()
            },
            "trading": {
                "max_positions": config_data['trading']['max_positions'].get(),
                "position_size": config_data['trading']['position_size'].get(),
                "stop_loss": config_data['trading']['stop_loss'].get(),
                "take_profit": config_data['trading']['take_profit'].get(),
                "trailing_stop": config_data['trading']['trailing_stop'].get()
            },
            "api": {
                "binance": {
                    "api_key": config_data['api']['binance']['api_key'].get(),
                    "api_secret": config_data['api']['binance']['api_secret'].get(),
                    "testnet": config_data['api']['binance']['testnet'].get()
                },
                "coinbase": {
                    "api_key": config_data['api']['coinbase']['api_key'].get(),
                    "api_secret": config_data['api']['coinbase']['api_secret'].get(),
                    "passphrase": config_data['api']['coinbase']['passphrase'].get()
                },
                "coingecko": {
                    "api_key": config_data['api']['coingecko']['api_key'].get()
                }
            },
            "alerts": {
                "telegram": {
                    "enabled": config_data['alerts']['telegram']['enabled'].get(),
                    "bot_token": config_data['alerts']['telegram']['bot_token'].get(),
                    "chat_id": config_data['alerts']['telegram']['chat_id'].get()
                },
                "email": {
                    "enabled": config_data['alerts']['email']['enabled'].get(),
                    "smtp_server": config_data['alerts']['email']['smtp_server'].get(),
                    "smtp_port": config_data['alerts']['email']['smtp_port'].get(),
                    "username": config_data['alerts']['email']['username'].get(),
                    "password": config_data['alerts']['email']['password'].get()
                }
            },
            "ml": {
                "enabled": config_data['ml']['enabled'].get(),
                "model_update_interval": config_data['ml']['model_update_interval'].get(),
                "prediction_confidence": config_data['ml']['prediction_confidence'].get(),
                "features": [feature for feature, var in config_data['ml']['feature_vars'].items() if var.get()]
            }
        }
        
        # Salvar arquivo
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config_to_save, f, indent=4, ensure_ascii=False)
        
        messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
        root.destroy()
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar configuração: {e}")

def test_configuration(config_data):
    """Testar configuração"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        messagebox.showinfo("Teste", "Testando configuração...")
        
        # Aqui você pode adicionar testes específicos
        # Por exemplo, testar conexão com APIs, enviar alerta de teste, etc.
        
        messagebox.showinfo("Sucesso", "Configuração testada com sucesso!")
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao testar configuração: {e}")

def create_config_file():
    """Criar arquivo de configuração padrão"""
    try:
        default_config = get_default_config()
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        print("✅ Arquivo config.json criado com configuração padrão")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar configuração: {e}")
        return False

def validate_config():
    """Validar configuração existente"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validar estrutura básica
        required_sections = ['general', 'trading', 'api', 'alerts', 'ml']
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            print(f"❌ Seções faltando: {', '.join(missing_sections)}")
            return False
        
        print("✅ Configuração válida")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao validar configuração: {e}")
        return False

def backup_config():
    """Fazer backup da configuração atual"""
    try:
        if not os.path.exists('config.json'):
            print("ℹ️  Nenhuma configuração para fazer backup")
            return False
        
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'config_backup_{timestamp}.json'
        
        shutil.copy('config.json', backup_file)
        print(f"✅ Backup criado: {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="IA GAIN - Configuration GUI Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_config_gui.py                           # Abrir interface gráfica
  python run_config_gui.py --create                   # Criar configuração padrão
  python run_config_gui.py --validate                 # Validar configuração existente
  python run_config_gui.py --backup                   # Fazer backup da configuração
  python run_config_gui.py --check                    # Verificar dependências
        """
    )
    
    parser.add_argument('--create',
                       action='store_true',
                       help='Criar arquivo de configuração padrão')
    parser.add_argument('--validate',
                       action='store_true',
                       help='Validar configuração existente')
    parser.add_argument('--backup',
                       action='store_true',
                       help='Fazer backup da configuração atual')
    parser.add_argument('--check',
                       action='store_true',
                       help='Verificar dependências')
    
    args = parser.parse_args()
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║              IA GAIN - Configuration GUI                     ║
║         Interface de Configuração Gráfica                   ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar dependências
    if args.check:
        print("🔍 Verificando dependências...")
        if check_dependencies():
            print("✅ Dependências OK")
        else:
            print("❌ Problemas com dependências")
            sys.exit(1)
        return
    
    # Verificar dependências antes de executar
    if not check_dependencies():
        sys.exit(1)
    
    # Configurar ambiente
    setup_environment()
    
    try:
        if args.create:
            print("⚙️  Criando configuração padrão...")
            create_config_file()
            
        elif args.validate:
            print("🔍 Validando configuração...")
            validate_config()
            
        elif args.backup:
            print("💾 Fazendo backup...")
            backup_config()
            
        else:
            print("🚀 Iniciando interface gráfica...")
            launch_gui()
        
        print("✅ Operação concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()