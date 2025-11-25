import logging
import json
import os
import sys
import asyncio
import aiohttp
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal, ROUND_DOWN
import hashlib
import time
import requests
from pathlib import Path

class Utils:
    """
    Utilitários auxiliares para o IA GAIN
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def format_currency(value: float, currency: str = "USDT", decimals: int = 4) -> str:
        """Formatar valor monetário"""
        try:
            if value >= 1_000_000:
                return f"{value/1_000_000:.2f}M {currency}"
            elif value >= 1_000:
                return f"{value/1_000:.2f}K {currency}"
            else:
                return f"{value:.{decimals}f} {currency}"
        except (ValueError, TypeError):
            return f"0 {currency}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """Formatar porcentagem"""
        try:
            return f"{value:.{decimals}f}%"
        except (ValueError, TypeError):
            return "0.00%"
    
    @staticmethod
    def format_number(value: float, decimals: int = 2) -> str:
        """Formatar número"""
        try:
            if abs(value) >= 1_000_000:
                return f"{value/1_000_000:.{decimals}f}M"
            elif abs(value) >= 1_000:
                return f"{value/1_000:.{decimals}f}K"
            else:
                return f"{value:.{decimals}f}"
        except (ValueError, TypeError):
            return "0.00"
    
    @staticmethod
    def round_down(value: float, decimals: int = 8) -> float:
        """Arredondar para baixo"""
        try:
            decimal_value = Decimal(str(value))
            return float(decimal_value.quantize(Decimal(f'0.{"0"*decimals}'), rounding=ROUND_DOWN))
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """Converter para float de forma segura"""
        try:
            return float(value)
        except (ValueError, TypeError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """Converter para int de forma segura"""
        try:
            return int(value)
        except (ValueError, TypeError, TypeError):
            return default
    
    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Divisão segura"""
        try:
            if denominator == 0 or np.isnan(denominator) or np.isinf(denominator):
                return default
            return numerator / denominator
        except (ZeroDivisionError, ValueError, TypeError):
            return default
    
    @staticmethod
    def calculate_roi(entry_price: float, current_price: float) -> float:
        """Calcular ROI (Return on Investment)"""
        try:
            return (current_price - entry_price) / entry_price * 100
        except (ZeroDivisionError, ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def calculate_position_size(balance: float, risk_percentage: float, stop_loss_percentage: float) -> float:
        """Calcular tamanho da posição baseado no risco"""
        try:
            risk_amount = balance * (risk_percentage / 100)
            position_size = risk_amount / (stop_loss_percentage / 100)
            return min(position_size, balance)  # Não exceder o saldo
        except (ZeroDivisionError, ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Validar símbolo de criptomoeda"""
        try:
            if not symbol or not isinstance(symbol, str):
                return False
            
            # Formato esperado: BTC/USDT, ETH/USDT, etc.
            parts = symbol.split('/')
            if len(parts) != 2:
                return False
            
            base, quote = parts
            if len(base) < 2 or len(quote) < 2:
                return False
            
            # Verificar se são caracteres válidos (letras e números)
            if not (base.isalnum() and quote.isalnum()):
                return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def get_timestamp_ms() -> int:
        """Obter timestamp em milissegundos"""
        return int(time.time() * 1000)
    
    @staticmethod
    def get_timestamp_s() -> int:
        """Obter timestamp em segundos"""
        return int(time.time())
    
    @staticmethod
    def ms_to_datetime(timestamp_ms: int) -> datetime:
        """Converter timestamp em milissegundos para datetime"""
        try:
            return datetime.fromtimestamp(timestamp_ms / 1000)
        except (ValueError, TypeError):
            return datetime.now()
    
    @staticmethod
    def datetime_to_ms(dt: datetime) -> int:
        """Converter datetime para timestamp em milissegundos"""
        try:
            return int(dt.timestamp() * 1000)
        except (ValueError, TypeError):
            return Utils.get_timestamp_ms()
    
    @staticmethod
    def time_ago(timestamp: Union[int, datetime]) -> str:
        """Converter timestamp para string "tempo atrás""""
        try:
            if isinstance(timestamp, int):
                if timestamp > 1e10:  # Milissegundos
                    timestamp = Utils.ms_to_datetime(timestamp)
                else:  # Segundos
                    timestamp = datetime.fromtimestamp(timestamp)
            
            now = datetime.now()
            diff = now - timestamp
            
            if diff.total_seconds() < 60:
                return f"{int(diff.total_seconds())}s ago"
            elif diff.total_seconds() < 3600:
                return f"{int(diff.total_seconds() / 60)}m ago"
            elif diff.total_seconds() < 86400:
                return f"{int(diff.total_seconds() / 3600)}h ago"
            else:
                return f"{int(diff.total_seconds() / 86400)}d ago"
                
        except Exception:
            return "Unknown"
    
    @staticmethod
    def generate_id(prefix: str = "") -> str:
        """Gerar ID único"""
        timestamp = str(int(time.time() * 1000))
        random_part = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"{prefix}{timestamp}_{random_part}" if prefix else f"{timestamp}_{random_part}"
    
    @staticmethod
    def save_to_file(data: Any, filename: str, format: str = "json") -> bool:
        """Salvar dados em arquivo"""
        try:
            if format.lower() == "json":
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format.lower() == "csv":
                if isinstance(data, pd.DataFrame):
                    data.to_csv(filename, index=False)
                else:
                    pd.DataFrame(data).to_csv(filename, index=False)
            else:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(str(data))
            
            return True
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao salvar arquivo {filename}: {str(e)}")
            return False
    
    @staticmethod
    def load_from_file(filename: str, format: str = "json") -> Any:
        """Carregar dados de arquivo"""
        try:
            if not os.path.exists(filename):
                return None
            
            if format.lower() == "json":
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif format.lower() == "csv":
                return pd.read_csv(filename)
            else:
                with open(filename, 'r', encoding='utf-8') as f:
                    return f.read()
                    
        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao carregar arquivo {filename}: {str(e)}")
            return None
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Garantir que diretório existe"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao criar diretório {path}: {str(e)}")
            return False
    
    @staticmethod
    def get_file_size(filename: str) -> int:
        """Obter tamanho do arquivo em bytes"""
        try:
            return os.path.getsize(filename)
        except (OSError, FileNotFoundError):
            return 0
    
    @staticmethod
    def delete_file(filename: str) -> bool:
        """Deletar arquivo"""
        try:
            if os.path.exists(filename):
                os.remove(filename)
                return True
            return False
        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao deletar arquivo {filename}: {str(e)}")
            return False
    
    @staticmethod
    def list_files(directory: str, extension: str = None) -> List[str]:
        """Listar arquivos em diretório"""
        try:
            files = []
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    if extension is None or file.endswith(extension):
                        files.append(file_path)
            return files
        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao listar arquivos em {directory}: {str(e)}")
            return []
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Obter informações do sistema"""
        try:
            import psutil
            
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'python_version': sys.version,
                'platform': sys.platform,
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            return {
                'cpu_percent': 'N/A',
                'memory_percent': 'N/A',
                'disk_usage': 'N/A',
                'python_version': sys.version,
                'platform': sys.platform,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao obter informações do sistema: {str(e)}")
            return {}
    
    @staticmethod
    def check_internet_connection(timeout: int = 5) -> bool:
        """Verificar conexão com internet"""
        try:
            response = requests.get('https://www.google.com', timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False
    
    @staticmethod
    def retry_function(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        """Executar função com retry"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                wait_time = delay * (backoff ** attempt)
                logging.getLogger(__name__).warning(f"Tentativa {attempt + 1} falhou: {str(e)}. Tentando novamente em {wait_time}s...")
                time.sleep(wait_time)
        
        return None
    
    @staticmethod
    def calculate_moving_average(data: List[float], window: int) -> List[float]:
        """Calcular média móvel"""
        try:
            if len(data) < window:
                return []
            
            ma = []
            for i in range(window - 1, len(data)):
                ma.append(sum(data[i - window + 1:i + 1]) / window)
            
            return ma
        except Exception:
            return []
    
    @staticmethod
    def calculate_standard_deviation(data: List[float]) -> float:
        """Calcular desvio padrão"""
        try:
            if len(data) < 2:
                return 0.0
            
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
            return variance ** 0.5
        except Exception:
            return 0.0
    
    @staticmethod
    def normalize_data(data: List[float]) -> List[float]:
        """Normalizar dados (min-max normalization)"""
        try:
            if not data or len(data) < 2:
                return data
            
            min_val = min(data)
            max_val = max(data)
            
            if min_val == max_val:
                return [0.0] * len(data)
            
            return [(x - min_val) / (max_val - min_val) for x in data]
            
        except Exception:
            return data
    
    @staticmethod
    def calculate_correlation(x: List[float], y: List[float]) -> float:
        """Calcular correlação de Pearson"""
        try:
            if len(x) != len(y) or len(x) < 2:
                return 0.0
            
            mean_x = sum(x) / len(x)
            mean_y = sum(y) / len(y)
            
            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
            denominator = (sum((x[i] - mean_x) ** 2 for i in range(len(x))) * 
                          sum((y[i] - mean_y) ** 2 for i in range(len(y)))) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except Exception:
            return 0.0

# Configuração de logging
class LoggerConfig:
    """Configuração de logging"""
    
    @staticmethod
    def setup_logging(
        name: str = "ia_gain",
        level: str = "INFO",
        log_file: str = None,
        format_string: str = None
    ):
        """Configurar logging"""
        
        if format_string is None:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # Configurar nível
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # Configurar handlers
        handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(format_string)
        console_handler.setFormatter(console_formatter)
        handlers.append(console_handler)
        
        # File handler (se especificado)
        if log_file:
            Utils.ensure_directory(os.path.dirname(log_file))
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(format_string)
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)
        
        # Configurar logger
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        
        # Limpar handlers existentes
        logger.handlers.clear()
        
        # Adicionar handlers
        for handler in handlers:
            logger.addHandler(handler)
        
        return logger

# Classe para gerenciar configurações
class ConfigManager:
    """Gerenciador de configurações"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self) -> bool:
        """Carregar configuração"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                return True
            else:
                self.config = self.get_default_config()
                return self.save_config()
        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao carregar configuração: {str(e)}")
            self.config = self.get_default_config()
            return False
    
    def save_config(self) -> bool:
        """Salvar configuração"""
        try:
            Utils.ensure_directory(os.path.dirname(self.config_file))
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao salvar configuração: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obter valor da configuração"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Definir valor na configuração"""
        try:
            keys = key.split('.')
            config = self.config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
            return self.save_config()
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao definir configuração: {str(e)}")
            return False
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Obter configuração padrão"""
        return {
            "trading": {
                "enabled": True,
                "max_positions": 5,
                "risk_per_trade": 2.0,
                "min_balance": 100.0
            },
            "risk_management": {
                "stop_loss": 5.0,
                "take_profit": 10.0,
                "max_drawdown": 20.0
            },
            "technical_analysis": {
                "rsi_period": 14,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "bollinger_period": 20,
                "bollinger_std": 2
            },
            "alerts": {
                "enabled": True,
                "email_enabled": False,
                "telegram_enabled": False,
                "discord_enabled": False
            },
            "system": {
                "log_level": "INFO",
                "data_retention_days": 30,
                "backup_enabled": True
            }
        }

# Exemplo de uso
if __name__ == "__main__":
    # Testar utilitários
    utils = Utils()
    
    print("Testando utilitários:")
    print(f"Format currency: {utils.format_currency(1234.5678)}")
    print(f"Format percentage: {utils.format_percentage(12.345)}")
    print(f"Calculate ROI: {utils.calculate_roi(100, 120)}%")
    print(f"Validate symbol: {utils.validate_symbol('BTC/USDT')}")
    print(f"Time ago: {utils.time_ago(datetime.now() - timedelta(minutes=30))}")
    
    # Testar config manager
    config_manager = ConfigManager("test_config.json")
    print(f"Config: {config_manager.get('trading.enabled')}")
    
    # Testar logging
    logger = LoggerConfig.setup_logging("test", "DEBUG")
    logger.info("Logger configurado com sucesso!")