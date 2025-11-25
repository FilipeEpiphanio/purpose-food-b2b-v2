"""
Coletor de dados Forex para IA GAIN
Suporte a pares de moedas e indicadores específicos forex
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import ccxt
from loguru import logger

@dataclass
class ForexMarketData:
    """Dados de mercado forex"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    spread: float
    bid: float
    ask: float
    # Indicadores técnicos
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    # Indicadores forex específicos
    atr: Optional[float] = None
    adx: Optional[float] = None
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None

class ForexDataCollector:
    """Coletor de dados específico para Forex"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.exchanges = {}
        self.session = None
        self.logger = logger.bind(component="ForexDataCollector")
        
        # Configurações padrão
        self.default_pairs = [
            "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", 
            "AUD/USD", "USD/CAD", "NZD/USD"
        ]
        
        self.timeframes = {
            '1m': 60, '5m': 300, '15m': 900, '30m': 1800,
            '1h': 3600, '4h': 14400, '1d': 86400
        }
    
    async def initialize_exchanges(self):
        """Inicializar exchanges forex"""
        self.session = aiohttp.ClientSession()
        
        forex_exchanges = [
            {'name': 'oanda', 'id': 'oanda'},
            {'name': 'fxcm', 'id': 'fxcm'},
            {'name': 'forexcom', 'id': 'forexcom'}
        ]
        
        for exchange_config in forex_exchanges:
            try:
                # Configuração específica para OANDA
                if exchange_config['name'] == 'oanda':
                    exchange = ccxt.oanda({
                        'apiKey': self.config.get('oanda', {}).get('api_key', ''),
                        'password': self.config.get('oanda', {}).get('api_secret', ''),
                        'sandbox': self.config.get('oanda', {}).get('sandbox', True),
                        'enableRateLimit': True,
                    })
                else:
                    exchange = getattr(ccxt, exchange_config['id'])()
                
                await exchange.load_markets()
                self.exchanges[exchange_config['name']] = exchange
                self.logger.info(f"Exchange forex {exchange_config['name']} inicializada com sucesso")
                
            except Exception as e:
                self.logger.error(f"Falha ao inicializar {exchange_config['name']}: {str(e)}")
    
    def is_forex_pair(self, symbol: str) -> bool:
        """Verificar se é par forex válido"""
        major_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD']
        symbol_upper = symbol.upper()
        
        # Verificar formato XXX/YYY
        if '/' in symbol_upper:
            base, quote = symbol_upper.split('/')
            return base in major_currencies and quote in major_currencies
        
        return False
    
    async def get_historical_data(self, symbol: str, timeframe: str = '1h', 
                                  limit: int = 200, start_date: datetime = None) -> pd.DataFrame:
        """Obter dados históricos forex"""
        try:
            if not self.is_forex_pair(symbol):
                raise ValueError(f"Par {symbol} não é um par forex válido")
            
            # Selecionar exchange forex disponível
            exchange = None
            for exchange_name in ['oanda', 'fxcm', 'forexcom']:
                if exchange_name in self.exchanges:
                    exchange = self.exchanges[exchange_name]
                    break
            
            if not exchange:
                self.logger.error("Nenhuma exchange forex disponível")
                return pd.DataFrame()
            
            # Verificar se o par está disponível na exchange
            if symbol not in exchange.symbols:
                self.logger.warning(f"Par {symbol} não disponível na {exchange.name}")
                return pd.DataFrame()
            
            # Buscar dados OHLCV
            since = None
            if start_date:
                since = int(start_date.timestamp() * 1000)
            
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit, since=since)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Calcular spread e bid/ask estimados
            df['spread'] = (df['high'] - df['low']) * 0.1  # Estimativa 10% da amplitude
            df['bid'] = df['close'] - (df['spread'] / 2)
            df['ask'] = df['close'] + (df['spread'] / 2)
            
            self.logger.info(f"Dados históricos forex obtidos para {symbol}: {len(df)} candles")
            return df
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados históricos forex para {symbol}: {str(e)}")
            return pd.DataFrame()
    
    async def get_live_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """Obter cotações ao vivo forex"""
        quotes = {}
        
        try:
            # Usar primeira exchange forex disponível
            exchange = None
            for exchange_name in ['oanda', 'fxcm', 'forexcom']:
                if exchange_name in self.exchanges:
                    exchange = self.exchanges[exchange_name]
                    break
            
            if not exchange:
                self.logger.error("Nenhuma exchange forex disponível para cotações")
                return quotes
            
            for symbol in symbols:
                if self.is_forex_pair(symbol):
                    try:
                        ticker = await exchange.fetch_ticker(symbol)
                        quotes[symbol] = {
                            'bid': ticker.get('bid', 0),
                            'ask': ticker.get('ask', 0),
                            'spread': ticker.get('ask', 0) - ticker.get('bid', 0),
                            'timestamp': datetime.now(),
                            'volume': ticker.get('quoteVolume', 0)
                        }
                    except Exception as e:
                        self.logger.error(f"Erro ao obter cotação para {symbol}: {str(e)}")
                
                # Rate limiting
                await asyncio.sleep(0.1)
        
        except Exception as e:
            self.logger.error(f"Erro ao obter cotações forex: {str(e)}")
        
        return quotes
    
    # Indicadores técnicos específicos forex
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range - indicador chave para forex"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        
        return true_range.rolling(window=period).mean()
    
    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average Directional Index"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Stochastic Oscillator"""
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        
        k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=d_period).mean()
        
        return k, d
    
    async def analyze_forex_data(self, symbol: str, df: pd.DataFrame) -> ForexMarketData:
        """Analisar dados forex com indicadores específicos"""
        if df.empty:
            return ForexMarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                open=0, high=0, low=0, close=0, volume=0,
                spread=0, bid=0, ask=0
            )
        
        latest = df.iloc[-1]
        
        # Calcular indicadores técnicos
        rsi = self.calculate_rsi(df['close']).iloc[-1] if len(df) > 14 else None
        macd, macd_signal = self.calculate_macd(df['close'])
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(df['close'])
        
        # Indicadores forex específicos
        atr = self.calculate_atr(df).iloc[-1] if len(df) > 14 else None
        adx = self.calculate_adx(df).iloc[-1] if len(df) > 28 else None
        stoch_k, stoch_d = self.calculate_stochastic(df)
        
        forex_data = ForexMarketData(
            symbol=symbol,
            timestamp=pd.to_datetime(latest.name),
            open=float(latest['open']),
            high=float(latest['high']),
            low=float(latest['low']),
            close=float(latest['close']),
            volume=float(latest['volume']),
            spread=float(latest.get('spread', 0)),
            bid=float(latest.get('bid', latest['close'])),
            ask=float(latest.get('ask', latest['close'])),
            # Indicadores
            rsi=float(rsi) if rsi is not None and not pd.isna(rsi) else None,
            macd=float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
            macd_signal=float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else None,
            bb_upper=float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else None,
            bb_middle=float(bb_middle.iloc[-1]) if not pd.isna(bb_middle.iloc[-1]) else None,
            bb_lower=float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else None,
            atr=float(atr) if atr is not None and not pd.isna(atr) else None,
            adx=float(adx) if adx is not None and not pd.isna(adx) else None,
            stoch_k=float(stoch_k.iloc[-1]) if not pd.isna(stoch_k.iloc[-1]) else None,
            stoch_d=float(stoch_d.iloc[-1]) if not pd.isna(stoch_d.iloc[-1]) else None
        )
        
        return forex_data
    
    async def scan_forex_opportunities(self, symbols: List[str] = None) -> List[ForexMarketData]:
        """Escanear oportunidades no mercado forex"""
        self.logger.info("Iniciando escaneamento forex...")
        
        if symbols is None:
            symbols = self.default_pairs
        
        opportunities = []
        
        for symbol in symbols:
            try:
                if not self.is_forex_pair(symbol):
                    continue
                
                # Obter dados históricos
                df = await self.get_historical_data(symbol, '1h', 100)
                
                if not df.empty:
                    # Analisar dados forex
                    forex_data = await self.analyze_forex_data(symbol, df)
                    
                    # Filtros de qualidade
                    if (forex_data.spread is not None and 
                        forex_data.spread <= self.config.get('max_spread', 0.05) and
                        forex_data.volume > self.config.get('min_volume', 1000000)):
                        
                        opportunities.append(forex_data)
                        self.logger.info(f"Adicionado {symbol} à lista de oportunidades forex")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Erro ao processar {symbol}: {str(e)}")
                continue
        
        self.logger.info(f"Escaneamento forex concluído. Encontradas {len(opportunities)} oportunidades")
        return opportunities
    
    async def close(self):
        """Fechar conexões"""
        if self.session:
            await self.session.close()