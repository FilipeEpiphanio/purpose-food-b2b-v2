import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time
import json
from typing import Dict, List, Optional, Tuple
import asyncio
import aiohttp
from dataclasses import dataclass

@dataclass
class MarketData:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: float
    weighted_avg_price: float
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    ema_9: Optional[float] = None
    ema_21: Optional[float] = None
    ema_50: Optional[float] = None
    ema_200: Optional[float] = None

class DataCollector:
    def __init__(self, config_path: str = 'config.json'):
        self.config = self.load_config(config_path)
        self.exchanges = {}
        self.logger = self.setup_logger()
        self.session = None
        
    def load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        return {
            "trading": {
                "max_position_size": 0.1,
                "stop_loss": 0.02,
                "take_profit": 0.05,
                "max_daily_trades": 10,
                "min_volume_threshold": 1000000
            },
            "risk": {
                "max_portfolio_risk": 0.05,
                "max_single_trade_risk": 0.02,
                "risk_reward_ratio": 2.0,
                "use_trailing_stop": True,
                "trailing_stop_distance": 0.03
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
            }
        }
    
    def setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('DataCollector')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('iagain.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def initialize_exchanges(self):
        self.session = aiohttp.ClientSession()
        
        exchanges_config = [
            {'name': 'binance', 'id': 'binance'},
            {'name': 'coinbase', 'id': 'coinbasepro'},
            {'name': 'kraken', 'id': 'kraken'},
            {'name': 'bybit', 'id': 'bybit'},
            {'name': 'oanda', 'id': 'oanda'},
            {'name': 'fxcm', 'id': 'fxcm'}
        ]
        
        for exchange_config in exchanges_config:
            try:
                exchange = getattr(ccxt, exchange_config['id'])()
                await exchange.load_markets()
                self.exchanges[exchange_config['name']] = exchange
                self.logger.info(f"Exchange {exchange_config['name']} initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize {exchange_config['name']}: {str(e)}")
    
    def is_forex_pair(self, symbol: str) -> bool:
        """Verificar se é par forex"""
        forex_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD',
                      'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/JPY', 'CAD/JPY', 'EUR/CHF', 'GBP/CHF']
        return symbol.upper() in forex_pairs or any(pair in symbol.upper() for pair in ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD'])
    
    async def get_top_cryptocurrencies(self, limit: int = 50) -> List[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://api.coingecko.com/api/v3/coins/markets',
                    params={
                        'vs_currency': 'usd',
                        'order': 'market_cap_desc',
                        'per_page': limit,
                        'page': 1,
                        'sparkline': 'false'
                    }
                ) as response:
                    data = await response.json()
                    return data
        except Exception as e:
            self.logger.error(f"Error fetching top cryptocurrencies: {str(e)}")
            return []
    
    async def get_fundamental_data(self, coin_id: str) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://api.coingecko.com/api/v3/coins/{coin_id}') as response:
                    data = await response.json()
                    return {
                        'market_cap': data.get('market_data', {}).get('market_cap', {}).get('usd', 0),
                        'total_volume': data.get('market_data', {}).get('total_volume', {}).get('usd', 0),
                        'circulating_supply': data.get('market_data', {}).get('circulating_supply', 0),
                        'total_supply': data.get('market_data', {}).get('total_supply', 0),
                        'developer_activity': data.get('developer_score', 0),
                        'community_score': data.get('community_score', 0),
                        'liquidity_score': data.get('liquidity_score', 0),
                        'public_interest_score': data.get('public_interest_score', 0)
                    }
        except Exception as e:
            self.logger.error(f"Error fetching fundamental data for {coin_id}: {str(e)}")
            return {}
    
    async def get_forex_data(self, symbol: str, timeframe: str = '1h', limit: int = 200) -> pd.DataFrame:
        """Buscar dados específicos para forex"""
        try:
            # Determinar exchange apropriada para forex
            if 'oanda' in self.exchanges:
                exchange = self.exchanges['oanda']
            elif 'fxcm' in self.exchanges:
                exchange = self.exchanges['fxcm']
            else:
                self.logger.error("Nenhuma exchange forex disponível")
                return pd.DataFrame()
            
            # Buscar dados OHLCV
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            self.logger.info(f"Dados forex obtidos para {symbol}: {len(df)} candles")
            return df
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados forex para {symbol}: {str(e)}")
            return pd.DataFrame()
    
    async def get_historical_data(self, symbol: str, timeframe: str = '1h', limit: int = 200) -> pd.DataFrame:
        """Buscar dados históricos (cripto ou forex)"""
        try:
            # Determinar exchange apropriada baseado no tipo de ativo
            if self.is_forex_pair(symbol):
                return await self.get_forex_data(symbol, timeframe, limit)
            else:
                # Usar Binance para criptomoedas
                if 'binance' in self.exchanges:
                    exchange = self.exchanges['binance']
                else:
                    self.logger.error("Binance exchange não disponível")
                    return pd.DataFrame()
                
                # Buscar dados OHLCV
                ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                self.logger.info(f"Dados históricos obtidos para {symbol}: {len(df)} candles")
                return df
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar dados históricos para {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
    
    def calculate_emas(self, prices: pd.Series, periods: List[int]) -> Dict[str, pd.Series]:
        emas = {}
        for period in periods:
            emas[f'ema_{period}'] = prices.ewm(span=period).mean()
        return emas
    
    async def analyze_market_data(self, symbol: str, df: pd.DataFrame) -> MarketData:
        if df.empty:
            return MarketData(symbol=symbol, timestamp=datetime.now(), **{col: 0 for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume', 'weighted_avg_price']})
        
        latest = df.iloc[-1]
        
        # Calculate technical indicators
        rsi = self.calculate_rsi(df['close'], self.config['technical']['rsi_period']).iloc[-1]
        macd, macd_signal = self.calculate_macd(df['close'])
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(df['close'])
        emas = self.calculate_emas(df['close'], self.config['technical']['ema_periods'])
        
        market_data = MarketData(
            symbol=symbol,
            timestamp=pd.to_datetime(latest.name),
            open=float(latest['open']),
            high=float(latest['high']),
            low=float(latest['low']),
            close=float(latest['close']),
            volume=float(latest['volume']),
            quote_volume=float(latest['volume']) * float(latest['close']),
            weighted_avg_price=float(latest['close']),
            rsi=float(rsi) if not pd.isna(rsi) else None,
            macd=float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
            macd_signal=float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else None,
            bb_upper=float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else None,
            bb_middle=float(bb_middle.iloc[-1]) if not pd.isna(bb_middle.iloc[-1]) else None,
            bb_lower=float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else None,
            ema_9=float(emas['ema_9'].iloc[-1]) if not pd.isna(emas['ema_9'].iloc[-1]) else None,
            ema_21=float(emas['ema_21'].iloc[-1]) if not pd.isna(emas['ema_21'].iloc[-1]) else None,
            ema_50=float(emas['ema_50'].iloc[-1]) if not pd.isna(emas['ema_50'].iloc[-1]) else None,
            ema_200=float(emas['ema_200'].iloc[-1]) if not pd.isna(emas['ema_200'].iloc[-1]) else None
        )
        
        return market_data
    
    async def scan_market_opportunities(self) -> List[MarketData]:
        self.logger.info("Starting market scan...")
        
        # Get top cryptocurrencies
        top_cryptos = await self.get_top_cryptocurrencies(50)
        opportunities = []
        
        for crypto in top_cryptos:
            try:
                symbol = f"{crypto['symbol'].upper()}/USDT"
                coin_id = crypto['id']
                
                # Get historical data
                df = await self.get_historical_data(symbol, '1h', 200)
                
                if not df.empty:
                    # Analyze market data
                    market_data = await self.analyze_market_data(symbol, df)
                    
                    # Get fundamental data
                    fundamental_data = await self.get_fundamental_data(coin_id)
                    
                    # Filter by minimum volume threshold
                    if market_data.volume >= self.config['trading']['min_volume_threshold']:
                        opportunities.append(market_data)
                        self.logger.info(f"Added {symbol} to opportunities list")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error processing {crypto['symbol']}: {str(e)}")
                continue
        
        self.logger.info(f"Market scan completed. Found {len(opportunities)} opportunities")
        return opportunities
    
    def save_market_data(self, data: List[MarketData], filename: str = None):
        if filename is None:
            filename = f"market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert MarketData objects to dictionaries
        data_dict = []
        for item in data:
            item_dict = item.__dict__.copy()
            item_dict['timestamp'] = item_dict['timestamp'].isoformat()
            data_dict.append(item_dict)
        
        with open(filename, 'w') as f:
            json.dump(data_dict, f, indent=2)
        
        self.logger.info(f"Market data saved to {filename}")
    
    async def close(self):
        if self.session:
            await self.session.close()
        
        for exchange in self.exchanges.values():
            await exchange.close()

async def main():
    collector = DataCollector()
    
    try:
        await collector.initialize_exchanges()
        opportunities = await collector.scan_market_opportunities()
        collector.save_market_data(opportunities)
        
        print(f"Found {len(opportunities)} trading opportunities")
        for opp in opportunities[:5]:  # Show top 5
            print(f"{opp.symbol}: RSI={opp.rsi:.2f}, MACD={opp.macd:.4f}, Volume={opp.volume:,.0f}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await collector.close()

if __name__ == "__main__":
    asyncio.run(main())