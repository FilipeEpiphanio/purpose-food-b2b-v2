import ccxt
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
from collections import defaultdict

@dataclass
class CryptoScore:
    symbol: str
    total_score: float
    technical_score: float
    fundamental_score: float
    social_score: float
    risk_score: float
    volume_score: float
    market_cap_score: float
    trend_score: float
    recommendation: str
    reasoning: List[str]

@dataclass
class CryptoMetrics:
    symbol: str
    market_cap: float
    volume_24h: float
    price_change_24h: float
    price_change_7d: float
    rsi: Optional[float] = None
    macd: Optional[float] = None
    bb_position: Optional[float] = None
    ema_9: Optional[float] = None
    ema_21: Optional[float] = None
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    volatility: Optional[float] = None
    social_sentiment: Optional[float] = None
    github_activity: Optional[int] = None
    developer_activity: Optional[int] = None

class CryptoSelector:
    def __init__(self, config_path: str = 'config.json'):
        self.config = self.load_config(config_path)
        self.logger = self.setup_logger()
        self.exchanges = {}
        self.crypto_cache = {}
        self.scoring_weights = self.get_scoring_weights()
        
    def load_config(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        return {
            "crypto_selector": {
                "min_market_cap": 100000000,  # $100M
                "min_volume_24h": 1000000,   # $1M
                "max_volatility": 0.15,      # 15%
                "min_liquidity_score": 0.6,
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
            "api": {
                "coinmarketcap": {
                    "api_key": "",
                    "base_url": "https://pro-api.coinmarketcap.com"
                },
                "coingecko": {
                    "api_key": "",
                    "base_url": "https://api.coingecko.com/api/v3"
                }
            }
        }
    
    def get_scoring_weights(self) -> Dict[str, float]:
        """Get scoring weights from config"""
        selector_config = self.config.get('crypto_selector', {})
        return {
            'technical': selector_config.get('technical_weight', 0.3),
            'fundamental': selector_config.get('fundamental_weight', 0.25),
            'social': selector_config.get('social_weight', 0.15),
            'risk': selector_config.get('risk_weight', 0.2),
            'volume': selector_config.get('volume_weight', 0.1)
        }
    
    def setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('CryptoSelector')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('iagain_selector.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def initialize_exchanges(self):
        """Initialize exchange connections for data collection"""
        try:
            # Initialize Binance for price data
            self.exchanges['binance'] = ccxt.binance({
                'enableRateLimit': True,
            })
            
            # Initialize CoinGecko for fundamental data
            self.exchanges['coingecko'] = ccxt.coinbasepro({
                'enableRateLimit': True,
            })
            
            for exchange in self.exchanges.values():
                await exchange.load_markets()
                
            self.logger.info("Exchanges initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize exchanges: {str(e)}")
    
    async def get_top_cryptocurrencies(self, limit: int = 100) -> List[Dict]:
        """Get top cryptocurrencies by market cap"""
        try:
            # Use Binance to get top trading pairs
            binance = self.exchanges.get('binance')
            if not binance:
                return []
            
            tickers = await binance.fetch_tickers()
            
            # Filter and sort by volume and market cap proxy
            crypto_data = []
            for symbol, ticker in tickers.items():
                if symbol.endswith('/USDT') and not symbol.startswith('USDT'):
                    base_symbol = symbol.replace('/USDT', '')
                    
                    # Skip excluded symbols
                    if base_symbol in self.config['crypto_selector']['excluded_symbols']:
                        continue
                    
                    # Calculate metrics
                    volume_24h = ticker.get('quoteVolume', 0)
                    price_change_24h = ticker.get('percentage', 0)
                    current_price = ticker.get('last', 0)
                    
                    # Estimate market cap (simplified)
                    # This is a rough estimate based on circulating supply proxy
                    estimated_market_cap = volume_24h * 7  # Rough estimate
                    
                    crypto_data.append({
                        'symbol': base_symbol,
                        'full_symbol': symbol,
                        'market_cap': estimated_market_cap,
                        'volume_24h': volume_24h,
                        'price_change_24h': price_change_24h,
                        'current_price': current_price,
                        'high_24h': ticker.get('high', 0),
                        'low_24h': ticker.get('low', 0)
                    })
            
            # Sort by market cap and volume
            crypto_data.sort(key=lambda x: (x['market_cap'], x['volume_24h']), reverse=True)
            
            # Filter by minimum requirements
            filtered_data = [
                crypto for crypto in crypto_data
                if crypto['market_cap'] >= self.config['crypto_selector']['min_market_cap'] and
                   crypto['volume_24h'] >= self.config['crypto_selector']['min_volume_24h']
            ]
            
            self.logger.info(f"Found {len(filtered_data)} cryptocurrencies meeting criteria")
            return filtered_data[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting top cryptocurrencies: {str(e)}")
            return []
    
    async def analyze_cryptocurrency(self, crypto_data: Dict) -> CryptoMetrics:
        """Analyze a single cryptocurrency"""
        try:
            symbol = crypto_data['symbol']
            full_symbol = crypto_data['full_symbol']
            
            # Get historical data for technical analysis
            historical_data = await self.get_historical_data(full_symbol)
            
            # Calculate technical indicators
            technical_metrics = self.calculate_technical_indicators(historical_data)
            
            # Calculate volatility
            volatility = self.calculate_volatility(historical_data)
            
            # Get support and resistance levels
            support, resistance = self.calculate_support_resistance(historical_data)
            
            # Get social and fundamental metrics (simplified)
            social_metrics = await self.get_social_metrics(symbol)
            fundamental_metrics = await self.get_fundamental_metrics(symbol)
            
            return CryptoMetrics(
                symbol=symbol,
                market_cap=crypto_data['market_cap'],
                volume_24h=crypto_data['volume_24h'],
                price_change_24h=crypto_data['price_change_24h'],
                price_change_7d=self.calculate_7d_change(historical_data),
                rsi=technical_metrics.get('rsi'),
                macd=technical_metrics.get('macd'),
                bb_position=technical_metrics.get('bb_position'),
                ema_9=technical_metrics.get('ema_9'),
                ema_21=technical_metrics.get('ema_21'),
                support_level=support,
                resistance_level=resistance,
                volatility=volatility,
                social_sentiment=social_metrics.get('sentiment'),
                github_activity=fundamental_metrics.get('github_activity'),
                developer_activity=fundamental_metrics.get('developer_activity')
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing {crypto_data['symbol']}: {str(e)}")
            return CryptoMetrics(
                symbol=crypto_data['symbol'],
                market_cap=crypto_data['market_cap'],
                volume_24h=crypto_data['volume_24h'],
                price_change_24h=crypto_data['price_change_24h'],
                price_change_7d=0
            )
    
    async def get_historical_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical price data"""
        try:
            binance = self.exchanges.get('binance')
            if not binance:
                return pd.DataFrame()
            
            # Fetch OHLCV data
            ohlcv = await binance.fetch_ohlcv(
                symbol, 
                timeframe='1d', 
                limit=days
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        if df.empty or len(df) < 14:
            return {}
        
        try:
            indicators = {}
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None
            
            # MACD
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            macd = ema_12 - ema_26
            macd_signal = macd.ewm(span=9).mean()
            indicators['macd'] = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else None
            indicators['macd_signal'] = macd_signal.iloc[-1] if not pd.isna(macd_signal.iloc[-1]) else None
            
            # Bollinger Bands
            bb_middle = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            bb_upper = bb_middle + (bb_std * 2)
            bb_lower = bb_middle - (bb_std * 2)
            
            current_price = df['close'].iloc[-1]
            bb_range = bb_upper.iloc[-1] - bb_lower.iloc[-1]
            bb_position = (current_price - bb_lower.iloc[-1]) / bb_range if bb_range > 0 else None
            indicators['bb_position'] = bb_position
            
            # EMAs
            indicators['ema_9'] = df['close'].ewm(span=9).mean().iloc[-1]
            indicators['ema_21'] = df['close'].ewm(span=21).mean().iloc[-1]
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating technical indicators: {str(e)}")
            return {}
    
    def calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate price volatility"""
        if df.empty or len(df) < 2:
            return 0.0
        
        try:
            returns = df['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(365)  # Annualized volatility
            return volatility
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {str(e)}")
            return 0.0
    
    def calculate_support_resistance(self, df: pd.DataFrame) -> Tuple[float, float]:
        """Calculate support and resistance levels"""
        if df.empty or len(df) < 5:
            return 0.0, 0.0
        
        try:
            # Simple method: recent min/max
            recent_data = df.tail(10)  # Last 10 days
            support = recent_data['low'].min()
            resistance = recent_data['high'].max()
            
            return support, resistance
            
        except Exception as e:
            self.logger.error(f"Error calculating support/resistance: {str(e)}")
            return 0.0, 0.0
    
    def calculate_7d_change(self, df: pd.DataFrame) -> float:
        """Calculate 7-day price change"""
        if df.empty or len(df) < 7:
            return 0.0
        
        try:
            current_price = df['close'].iloc[-1]
            price_7d_ago = df['close'].iloc[-8]
            change = (current_price - price_7d_ago) / price_7d_ago * 100
            return change
        except Exception as e:
            self.logger.error(f"Error calculating 7d change: {str(e)}")
            return 0.0
    
    async def get_social_metrics(self, symbol: str) -> Dict:
        """Get social media metrics (simplified)"""
        # This would normally integrate with social media APIs
        # For now, return mock data
        return {
            'sentiment': np.random.uniform(-1, 1),  # -1 to 1
            'twitter_mentions': np.random.randint(0, 1000),
            'reddit_mentions': np.random.randint(0, 500)
        }
    
    async def get_fundamental_metrics(self, symbol: str) -> Dict:
        """Get fundamental metrics (simplified)"""
        # This would normally integrate with fundamental data APIs
        # For now, return mock data
        return {
            'github_activity': np.random.randint(0, 100),
            'developer_activity': np.random.randint(0, 50),
            'partnerships': np.random.randint(0, 10),
            'ecosystem_growth': np.random.uniform(0, 1)
        }
    
    def calculate_crypto_score(self, metrics: CryptoMetrics) -> CryptoScore:
        """Calculate overall score for a cryptocurrency"""
        try:
            reasoning = []
            
            # Technical Score (0-10)
            technical_score = self.calculate_technical_score(metrics)
            
            # Fundamental Score (0-10)
            fundamental_score = self.calculate_fundamental_score(metrics)
            
            # Social Score (0-10)
            social_score = self.calculate_social_score(metrics)
            
            # Risk Score (0-10, higher is better)
            risk_score = self.calculate_risk_score(metrics)
            
            # Volume Score (0-10)
            volume_score = self.calculate_volume_score(metrics)
            
            # Market Cap Score (0-10)
            market_cap_score = self.calculate_market_cap_score(metrics)
            
            # Trend Score (0-10)
            trend_score = self.calculate_trend_score(metrics)
            
            # Weighted Total Score
            weights = self.scoring_weights
            total_score = (
                technical_score * weights['technical'] +
                fundamental_score * weights['fundamental'] +
                social_score * weights['social'] +
                risk_score * weights['risk'] +
                volume_score * weights['volume']
            )
            
            # Generate recommendation
            recommendation = self.generate_recommendation(total_score)
            
            # Generate reasoning
            reasoning = self.generate_reasoning(metrics, {
                'technical': technical_score,
                'fundamental': fundamental_score,
                'social': social_score,
                'risk': risk_score,
                'volume': volume_score,
                'trend': trend_score
            })
            
            return CryptoScore(
                symbol=metrics.symbol,
                total_score=total_score,
                technical_score=technical_score,
                fundamental_score=fundamental_score,
                social_score=social_score,
                risk_score=risk_score,
                volume_score=volume_score,
                market_cap_score=market_cap_score,
                trend_score=trend_score,
                recommendation=recommendation,
                reasoning=reasoning
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating score for {metrics.symbol}: {str(e)}")
            return CryptoScore(
                symbol=metrics.symbol,
                total_score=0.0,
                technical_score=0.0,
                fundamental_score=0.0,
                social_score=0.0,
                risk_score=0.0,
                volume_score=0.0,
                market_cap_score=0.0,
                trend_score=0.0,
                recommendation='HOLD',
                reasoning=[f"Error in analysis: {str(e)}"]
            )
    
    def calculate_technical_score(self, metrics: CryptoMetrics) -> float:
        """Calculate technical analysis score"""
        score = 5.0  # Base score
        
        # RSI (0-10)
        if metrics.rsi:
            if metrics.rsi < 30:
                score += 2  # Oversold - good buying opportunity
            elif metrics.rsi > 70:
                score -= 2  # Overbought - be careful
            elif 40 <= metrics.rsi <= 60:
                score += 1  # Neutral zone - stable
        
        # MACD
        if metrics.macd and metrics.macd > 0:
            score += 1
        
        # Bollinger Bands position
        if metrics.bb_position:
            if metrics.bb_position < 0.2:
                score += 1.5  # Near lower band - potential bounce
            elif metrics.bb_position > 0.8:
                score -= 1.5  # Near upper band - potential reversal
        
        # EMA crossover
        if metrics.ema_9 and metrics.ema_21:
            if metrics.ema_9 > metrics.ema_21:
                score += 1  # Bullish trend
            else:
                score -= 1  # Bearish trend
        
        return max(0, min(10, score))
    
    def calculate_fundamental_score(self, metrics: CryptoMetrics) -> float:
        """Calculate fundamental analysis score"""
        score = 5.0  # Base score
        
        # GitHub activity
        if metrics.github_activity and metrics.github_activity > 50:
            score += 2
        elif metrics.github_activity and metrics.github_activity > 20:
            score += 1
        
        # Developer activity
        if metrics.developer_activity and metrics.developer_activity > 30:
            score += 1.5
        elif metrics.developer_activity and metrics.developer_activity > 10:
            score += 0.5
        
        # Market cap stability (proxy for adoption)
        if metrics.market_cap > 1000000000:  # $1B+
            score += 2
        elif metrics.market_cap > 500000000:  # $500M+
            score += 1
        
        return max(0, min(10, score))
    
    def calculate_social_score(self, metrics: CryptoMetrics) -> float:
        """Calculate social sentiment score"""
        score = 5.0  # Base score
        
        if metrics.social_sentiment:
            if metrics.social_sentiment > 0.5:
                score += 2.5  # Very positive sentiment
            elif metrics.social_sentiment > 0:
                score += 1.5  # Positive sentiment
            elif metrics.social_sentiment < -0.5:
                score -= 2.5  # Very negative sentiment
            else:
                score -= 1.5  # Negative sentiment
        
        return max(0, min(10, score))
    
    def calculate_risk_score(self, metrics: CryptoMetrics) -> float:
        """Calculate risk score (higher is better)"""
        score = 5.0  # Base score
        
        # Volatility (lower is better for risk score)
        if metrics.volatility:
            if metrics.volatility < 0.05:  # < 5%
                score += 2.5
            elif metrics.volatility < 0.1:  # < 10%
                score += 1.5
            elif metrics.volatility > 0.2:  # > 20%
                score -= 2.5
            elif metrics.volatility > 0.15:  # > 15%
                score -= 1.5
        
        # Price stability (24h change)
        if abs(metrics.price_change_24h) < 5:
            score += 1
        elif abs(metrics.price_change_24h) > 15:
            score -= 1.5
        
        return max(0, min(10, score))
    
    def calculate_volume_score(self, metrics: CryptoMetrics) -> float:
        """Calculate volume score"""
        score = 5.0  # Base score
        
        if metrics.volume_24h > 100000000:  # $100M+
            score += 2.5
        elif metrics.volume_24h > 50000000:  # $50M+
            score += 1.5
        elif metrics.volume_24h > 10000000:  # $10M+
            score += 1
        elif metrics.volume_24h < 1000000:  # < $1M
            score -= 2.5
        
        return max(0, min(10, score))
    
    def calculate_market_cap_score(self, metrics: CryptoMetrics) -> float:
        """Calculate market cap score"""
        score = 5.0  # Base score
        
        if metrics.market_cap > 5000000000:  # $5B+
            score += 2.5
        elif metrics.market_cap > 1000000000:  # $1B+
            score += 2
        elif metrics.market_cap > 500000000:  # $500M+
            score += 1.5
        elif metrics.market_cap > 100000000:  # $100M+
            score += 1
        
        return max(0, min(10, score))
    
    def calculate_trend_score(self, metrics: CryptoMetrics) -> float:
        """Calculate trend score"""
        score = 5.0  # Base score
        
        # 24h trend
        if metrics.price_change_24h > 5:
            score += 1.5
        elif metrics.price_change_24h > 0:
            score += 0.5
        elif metrics.price_change_24h < -5:
            score -= 1.5
        else:
            score -= 0.5
        
        # 7d trend
        if metrics.price_change_7d > 10:
            score += 2
        elif metrics.price_change_7d > 0:
            score += 1
        elif metrics.price_change_7d < -10:
            score -= 2
        else:
            score -= 1
        
        return max(0, min(10, score))
    
    def generate_recommendation(self, total_score: float) -> str:
        """Generate recommendation based on total score"""
        if total_score >= 8.5:
            return 'STRONG_BUY'
        elif total_score >= 7.0:
            return 'BUY'
        elif total_score >= 5.5:
            return 'MODERATE_BUY'
        elif total_score >= 4.0:
            return 'HOLD'
        elif total_score >= 2.5:
            return 'MODERATE_SELL'
        else:
            return 'SELL'
    
    def generate_reasoning(self, metrics: CryptoMetrics, scores: Dict[str, float]) -> List[str]:
        """Generate reasoning for the score"""
        reasoning = []
        
        if scores['technical'] >= 7:
            reasoning.append("Strong technical indicators")
        elif scores['technical'] <= 3:
            reasoning.append("Weak technical indicators")
        
        if scores['fundamental'] >= 7:
            reasoning.append("Strong fundamentals")
        elif scores['fundamental'] <= 3:
            reasoning.append("Weak fundamentals")
        
        if scores['social'] >= 7:
            reasoning.append("Positive social sentiment")
        elif scores['social'] <= 3:
            reasoning.append("Negative social sentiment")
        
        if scores['risk'] >= 7:
            reasoning.append("Low risk profile")
        elif scores['risk'] <= 3:
            reasoning.append("High risk profile")
        
        if scores['trend'] >= 7:
            reasoning.append("Strong upward trend")
        elif scores['trend'] <= 3:
            reasoning.append("Downward trend")
        
        if not reasoning:
            reasoning.append("Mixed signals across metrics")
        
        return reasoning
    
    async def select_best_cryptocurrencies(self, limit: int = None) -> List[CryptoScore]:
        """Select the best cryptocurrencies based on comprehensive analysis"""
        if limit is None:
            limit = self.config['crypto_selector']['max_cryptos_to_select']
        
        self.logger.info("Starting cryptocurrency selection process...")
        
        # Get top cryptocurrencies
        top_cryptos = await self.get_top_cryptocurrencies(100)
        
        if not top_cryptos:
            self.logger.error("No cryptocurrencies found")
            return []
        
        self.logger.info(f"Analyzing {len(top_cryptos)} cryptocurrencies...")
        
        # Analyze each cryptocurrency
        crypto_scores = []
        for crypto_data in top_cryptos:
            try:
                # Analyze cryptocurrency
                metrics = await self.analyze_cryptocurrency(crypto_data)
                
                # Calculate score
                score = self.calculate_crypto_score(metrics)
                
                # Filter by minimum score
                if score.total_score >= self.config['crypto_selector']['min_total_score']:
                    crypto_scores.append(score)
                
            except Exception as e:
                self.logger.error(f"Error processing {crypto_data['symbol']}: {str(e)}")
                continue
        
        # Sort by total score
        crypto_scores.sort(key=lambda x: x.total_score, reverse=True)
        
        # Limit results
        selected_cryptos = crypto_scores[:limit]
        
        self.logger.info(f"Selected {len(selected_cryptos)} cryptocurrencies")
        
        # Log results
        for i, crypto in enumerate(selected_cryptos[:10], 1):
            self.logger.info(f"{i}. {crypto.symbol}: {crypto.total_score:.2f} - {crypto.recommendation}")
        
        return selected_cryptos
    
    def get_selected_symbols(self, crypto_scores: List[CryptoScore]) -> List[str]:
        """Extract symbols from selected cryptocurrencies"""
        return [f"{score.symbol}/USDT" for score in crypto_scores]
    
    async def close(self):
        """Close all connections"""
        for exchange in self.exchanges.values():
            await exchange.close()

async def main():
    """Test the crypto selector"""
    selector = CryptoSelector()
    await selector.initialize_exchanges()
    
    print("Crypto Selector initialized")
    
    # Select best cryptocurrencies
    selected_cryptos = await selector.select_best_cryptocurrencies(20)
    
    print(f"\nSelected {len(selected_cryptos)} cryptocurrencies:")
    for i, crypto in enumerate(selected_cryptos, 1):
        print(f"{i}. {crypto.symbol}: {crypto.total_score:.2f} - {crypto.recommendation}")
        print(f"   Reasoning: {', '.join(crypto.reasoning)}")
        print()
    
    # Get symbols for trading
    symbols = selector.get_selected_symbols(selected_cryptos)
    print(f"Trading symbols: {symbols}")
    
    await selector.close()

if __name__ == "__main__":
    asyncio.run(main())