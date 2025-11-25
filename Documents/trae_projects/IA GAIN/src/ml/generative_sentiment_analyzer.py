"""
Generative AI Sentiment Analysis System
Uses advanced NLP and generative AI models for market sentiment analysis
"""

import asyncio
import aiohttp
try:
    import pandas as pd
except Exception:
    pd = None  # Optional dependency; code handles absence gracefully
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import re
import time
from collections import defaultdict, deque
import hashlib
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except Exception:
    # Best-effort download; proceed if packages already installed
    pass

class SentimentSource(Enum):
    """Sources of sentiment data"""
    TWITTER = "twitter"
    REDDIT = "reddit"
    NEWS = "news"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    YOUTUBE = "youtube"
    FORUMS = "forums"
    ANALYST_REPORTS = "analyst_reports"
    SOCIAL_MEDIA = "social_media"
    GOOGLE_TRENDS = "google_trends"

class SentimentCategory(Enum):
    """Sentiment categories"""
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"

class SentimentType(Enum):
    """Types of sentiment analysis"""
    MARKET = "market"
    CRYPTO = "crypto"
    FOREX = "forex"
    STOCK = "stock"
    COMMODITY = "commodity"
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    REGULATORY = "regulatory"
    ADOPTION = "adoption"
    INSTITUTIONAL = "institutional"

@dataclass
class SentimentData:
    """Raw sentiment data point"""
    source: SentimentSource
    content: str
    timestamp: datetime
    author: Optional[str] = None
    url: Optional[str] = None
    likes: int = 0
    shares: int = 0
    comments: int = 0
    reach: int = 0
    verified: bool = False
    language: str = "en"
    entities: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SentimentAnalysis:
    """Processed sentiment analysis result"""
    data: SentimentData
    sentiment_score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    category: SentimentCategory
    type: SentimentType
    entities: List[str]
    keywords: List[str]
    emotions: Dict[str, float]
    aspects: Dict[str, float]  # Aspect-based sentiment
    relevance_score: float
    market_impact_score: float
    social_engagement_score: float
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    model_version: str = "1.0"
    analysis_method: str = "hybrid"

@dataclass
class SentimentAggregation:
    """Aggregated sentiment metrics"""
    symbol: str
    timeframe: str
    start_time: datetime
    end_time: datetime
    overall_score: float
    overall_category: SentimentCategory
    confidence: float
    sample_size: int
    source_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    trend: str  # "improving", "stable", "deteriorating"
    volatility: float
    momentum: float
    key_topics: List[str]
    influential_sources: List[str]
    market_correlation: float
    leading_indicators: List[str]
    sentiment_history: List[float]

class GenerativeSentimentAnalyzer:
    """
    Advanced sentiment analysis system using generative AI and multiple sources
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self.get_default_config()
        self.db_connection = None
        self.rate_limiter = defaultdict(lambda: deque(maxlen=100))
        self.cache = {}
        self.initialize_analyzers()
        self.setup_database()
        self.setup_api_clients()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for sentiment analysis"""
        return {
            'api_keys': {
                'openai': '',  # Will be set from config.json
                'twitter': '',
                'reddit': '',
                'news_api': ''
            },
            'sentiment': {
                'cache_duration': 3600,  # 1 hour
                'rate_limit_delay': 1.0,
                'max_retries': 3,
                'confidence_threshold': 0.6,
                'min_sample_size': 50,
                'aggregation_window': '1h',
                'trend_analysis_period': '24h'
            },
            'analysis': {
                'enable_nltk': True,
                'enable_textblob': True,
                'enable_generative': True,
                'enable_clustering': True,
                'enable_aspect_analysis': True,
                'enable_emotion_detection': True
            },
            'sources': {
                'twitter': {'enabled': True, 'weight': 0.3},
                'reddit': {'enabled': True, 'weight': 0.25},
                'news': {'enabled': True, 'weight': 0.2},
                'forums': {'enabled': True, 'weight': 0.15},
                'social_media': {'enabled': True, 'weight': 0.1}
            },
            'market_impact': {
                'verified_weight': 1.5,
                'high_engagement_weight': 1.3,
                'institutional_weight': 2.0,
                'news_weight': 1.8,
                'social_weight': 0.8
            }
        }
    
    def initialize_analyzers(self):
        """Initialize various sentiment analyzers"""
        try:
            # Initialize NLTK sentiment analyzer
            if self.config['analysis']['enable_nltk']:
                self.nltk_analyzer = SentimentIntensityAnalyzer()
            
            # Initialize lemmatizer and stopwords
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
            
            # Initialize clustering model
            if self.config['analysis']['enable_clustering']:
                self.clustering_model = KMeans(n_clusters=10, random_state=42)
                self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            
            logger.info("Sentiment analyzers initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing analyzers: {e}")
            self.nltk_analyzer = None
    
    def setup_database(self):
        """Setup SQLite database for sentiment data storage"""
        try:
            self.db_connection = sqlite3.connect('sentiment_data.db', check_same_thread=False)
            cursor = self.db_connection.cursor()
            
            # Create sentiment data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sentiment_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    author TEXT,
                    url TEXT,
                    likes INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    reach INTEGER DEFAULT 0,
                    verified BOOLEAN DEFAULT FALSE,
                    language TEXT DEFAULT 'en',
                    entities TEXT,
                    hashtags TEXT,
                    mentions TEXT,
                    metadata TEXT,
                    hash TEXT UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create sentiment analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sentiment_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_id INTEGER,
                    sentiment_score REAL NOT NULL,
                    confidence REAL NOT NULL,
                    category TEXT NOT NULL,
                    type TEXT NOT NULL,
                    entities TEXT,
                    keywords TEXT,
                    emotions TEXT,
                    aspects TEXT,
                    relevance_score REAL,
                    market_impact_score REAL,
                    social_engagement_score REAL,
                    analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    model_version TEXT,
                    analysis_method TEXT,
                    FOREIGN KEY (data_id) REFERENCES sentiment_data (id)
                )
            ''')
            
            # Create aggregated sentiment table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sentiment_aggregation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME NOT NULL,
                    overall_score REAL NOT NULL,
                    overall_category TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    sample_size INTEGER NOT NULL,
                    source_distribution TEXT,
                    category_distribution TEXT,
                    trend TEXT,
                    volatility REAL,
                    momentum REAL,
                    key_topics TEXT,
                    influential_sources TEXT,
                    market_correlation REAL,
                    leading_indicators TEXT,
                    sentiment_history TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.db_connection.commit()
            logger.info("Database setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            self.db_connection = None
    
    def setup_api_clients(self):
        """Setup API clients for different data sources"""
        self.api_clients = {}
        
        # Setup Twitter API client
        if self.config['sources']['twitter']['enabled']:
            self.api_clients['twitter'] = {
                'base_url': 'https://api.twitter.com/2',
                'headers': {
                    'Authorization': f"Bearer {self.config['api_keys'].get('twitter', '')}",
                    'Content-Type': 'application/json'
                }
            }
        
        # Setup Reddit API client
        if self.config['sources']['reddit']['enabled']:
            self.api_clients['reddit'] = {
                'base_url': 'https://oauth.reddit.com',
                'headers': {
                    'Authorization': f"Bearer {self.config['api_keys'].get('reddit', '')}",
                    'User-Agent': 'IA-GAIN-Bot/1.0'
                }
            }
        
        # Setup News API client
        if self.config['sources']['news']['enabled']:
            self.api_clients['news'] = {
                'base_url': 'https://newsapi.org/v2',
                'headers': {
                    'X-API-Key': self.config['api_keys'].get('news_api', '')
                }
            }
    
    def generate_content_hash(self, content: str, source: str) -> str:
        """Generate unique hash for content to avoid duplicates"""
        content_str = f"{content}|{source}"
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def is_rate_limited(self, source: str) -> bool:
        """Check if source is rate limited"""
        current_time = time.time()
        
        # Remove old entries (older than 1 hour)
        while (self.rate_limiter[source] and 
               current_time - self.rate_limiter[source][0] > 3600):
            self.rate_limiter[source].popleft()
        
        # Check rate limit (max 100 requests per hour)
        return len(self.rate_limiter[source]) >= 100
    
    def record_api_call(self, source: str):
        """Record API call for rate limiting"""
        self.rate_limiter[source].append(time.time())
    
    def cache_result(self, key: str, result: Any, duration: int = None):
        """Cache analysis result"""
        if duration is None:
            duration = self.config['sentiment']['cache_duration']
        
        self.cache[key] = {
            'result': result,
            'timestamp': time.time(),
            'duration': duration
        }
    
    def get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached result if available"""
        if key in self.cache:
            cached = self.cache[key]
            if time.time() - cached['timestamp'] < cached['duration']:
                return cached['result']
            else:
                # Remove expired cache
                del self.cache[key]
        
        return None
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize and lemmatize
        tokens = word_tokenize(text)
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        
        return ' '.join(tokens)
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        # Simple entity extraction - can be enhanced with NER models
        entities = []
        
        # Extract cryptocurrency symbols (e.g., BTC, ETH, $BTC)
        crypto_pattern = r'\b(?:\$)?(?:BTC|ETH|ADA|SOL|DOT|LINK|UNI|AVAX|MATIC|ATOM|VET|XRP|LTC|BCH|BNB|DOGE|SHIB|TRX|ETC|XLM|ALGO|XMR|XTZ|FIL|HBAR|ICP|AXS|FTT|CRO|FTM|MANA|SAND|LRC|ENJ|BAT|ZRX|KNC|BNT|REN|ZIL|ONE|SKL|ANKR|CTSI|CELR|RPL|STORJ|BAND|RLC|UMA|YFI|AAVE|COMP|MKR|SNX|CRV|1INCH|SUSHI|PERP|DYDX|LDO|RBN|AURA|BAL|GMX|GNS|DPX|JOE|PNG|TraderJoe|Pangolin|GMX|SushiSwap|Uniswap|Aave|Compound|MakerDAO|Synthetix|Curve|1inch|PancakeSwap|QuickSwap|SpookySwap|SpiritSwap|Beethoven|Balancer|Yearn|Harvest|Pickle|Badger|Alpha|Mirror|Synthetix|dYdX|Perpetual|Loopring|ImmutableX|Optimism|Arbitrum|Polygon|Avalanche|Fantom|Harmony|Celo|Near|Algorand|Solana|Cardano|Polkadot|Cosmos|Tezos|Ethereum|Bitcoin|Litecoin|BitcoinCash|Dogecoin|ShibaInu|Ripple|Stellar|Monero|Dash|Zcash|Decred|Horizen|Komodo|Waves|NEM|Wanchain|Aion|ICON|Lisk|Ark|Nebulas|Neblio|Particl|PIVX|Stratis|Syscoin|Verge|Vertcoin|Reddcoin|Namecoin|Peercoin|Feathercoin|Novacoin|Ixcoin|Terracoin|Digitalcoin|Worldcoin|Freicoin|Zetacoin|Primecoin|Quark|Infinitecoin|Megacoin|Anoncoin|BBQCoin|Copperlark|Devcoin|Goldcoin|Junkcoin|Memorycoin|Mincoin|Phoenixcoin|Stablecoin|Tigercoin|Unobtanium|Yacoin|Zeccoin|42coin|Acoin|Alphacoin|AmericanCoin|AnarchistsPrime|Antimatter|Aphroditecoin|Applecoin|Argentum|Asiacoin|Auroracoin|Axiom|Azcoin|Battlecoin|BeaverCoin|BitBar|BitGem|Blackcoin|Boostcoin|Bottlecaps|Bunnycoin|Cagecoin|Carboncoin|Cashcoin|Catcoin|ChainCoin|Chinacoin|Clockcoin|Cloudcoin|Cloakcoin|Colossuscoin|Continuumcoin|Copperbars|Cornucopia|Cosmoscoin|Craftcoin|Cryptobuck|Cryptogenic|Curecoin|Darkcoin|Dashcoin|Deepcoin|Deutsche|Diamond|Digibyte|Digitalcoin|Dimecoin|Dogecoin|Dopecoin|Doubloons|Droidcoin|Duckduckcoin|EagleCoin|Earthcoin|Eggcoin|Electric|Electronic|Emerald|Emercoin|Energy|Entropy|EuropeCoin|Evergreencoin|Exclusive|Execoin|Exile|Expanse|Fastcoin|Fedoracoin|Fibre|Fireflycoin|Flappycoin|Florincoin|Fluttercoin|Foxcoin|Franko|Freecoin|Frostbyte|Fuelcoin|Fujicoin|Galaxycoin|Gamerholic|GeistGeld|Globalcoin|Goldcoin|Grain|Grandcoin|Greenback|Guldencoin|Halcoin|Hamstercoin|Hobonickels|Huntercoin|Hypercoin|Icecoin|Imperialcoin|Incakoin|Infinitecoin|Influence|Innova|I0coin|Jesuscoin|Joulecoin|Karmacoin|Kashmir|Kikcoin|Krugercoin|Leafcoin|Lebowskis|Limecoin|Litedoge|Lottocoin|Lycancoin|Magi|Magiccoin|Marscoin|Maverick|Maxcoin|Mazacoin|Megacoin|Memecoin|Metiscoin|Microcoin|Mincoin|Mineral|Mintcoin|Mobacoin|Molecular|Mooncoin|Murraycoin|Myriadcoin|N5coin|NasCoin|Neocoin|Netcoin|Nibble|Noirbits|Noodlyappendage|Novacoin|Nuggets|Nyancoin|Olympiccoin|Onecoin|Onioncoin|Paccoin|Pandacoin|Particle|Paycoin|Peercoin|Penguincoin|Pennies|Peoplecoin|Pesetacoin|Petro|Phoenixcoin|Pikacoin|Pizzacoin|Platinumcoin|Playcoin|Pokercoin|Popularcoin|Potcoin|Powercoin|Prospectors|Protoshares|Pseudocoin|Pulse|Qibuck|Quark|Qubit|Radioactive|Rainbowcoin|Rapidcoin|Ratcoin|Realcoin|Redcoin|Reddcoin|Richcoin|Riecoin|Ripple|Ronpaulcoin|Royalcoin|Rubycoin|Rucoin|Sandcoin|Sauron|Savecoin|Secondscoin|Securecoin|Seedcoin|Shibacoin|Shopcoin|Silkcoin|Silvercoin|Smartcoin|Smileycoin|Songcoin|Sooncoin|Spots|Stablecoin|Stacycoin|Starcoin|Stashcoin|Stellar|Stoopidcoin|Supercoin|Swagcoin|Syncoin|Synthetix|Tagcoin|Takencoin|Tattcoin|Tenebrix|Terracoin|Tescoin|Tezos|Thecoin|Tiger|Time|Topcoin|TradeCoin|Trickcoin|Trollcoin|Turbocoin|UFO|Ultra|Umbrella|Uncle|Unicoin|Universe|Urocoin|Valuecoin|Vegascoin|Velocity|Vendettacoin|Venuscoin|Vericoin|Viacoin|Virtualcoin|Visacoin|Vote|Voyacoin|Wankcoin|Weedcoin|Wikicoin|Worldcoin|Xcoin|XenCoin|Xivra|YAcoin|Ybcoin|Yentacoin|Yin|Yuan|Zc|Zedcoin|Zeitcoin|Zenith|Zetacoin|Zimbacoin|Zone|Zurbcoin)\b'
            crypto_matches = re.findall(crypto_pattern, text, re.IGNORECASE)
            entities.extend([match.upper() for match in crypto_matches])
            
            # Extract company names (simple pattern)
            company_pattern = r'\b(?:Apple|Google|Microsoft|Amazon|Tesla|Meta|Netflix|Nvidia|AMD|Intel|IBM|Oracle|Salesforce|Adobe|PayPal|Square|Coinbase|Binance|Kraken|Gemini|Bitfinex|Huobi|OKEx|Bybit|FTX|Deribit|BitMEX|CME|Bakkt|Grayscale|MicroStrategy|Tesla|Square|PayPal|Visa|Mastercard|JPMorgan|Goldman|Sachs|Morgan|Stanley|Bank|America|Citi|Wells|Fargo|Deutsche|Credit|Suisse|Barclays|HSBC|UBS|Santander|BBVA|BNP|Paribas|Societe|Generale|ING|ABN|Amro|Rabobank|Nordea|Danske|Swedbank|SEB|Handelsbanken|Norwegian|Storebrand|Skandia|Alecta|SPV|KPA|PFA|Danica|Nordea|Life|Pensions|Tryg|If|Gjensidige|Folksam|LF|Insurance|Swedish|Finnish|Norwegian|Danish|Danske|Bank|Nordea|SEB|Swedbank|Handelsbanken|Svenska|Cellulosa|SCA|Ericsson|Volvo|Scania|Atlas|Copco|Sandvik|SKF|AstraZeneca|H&M|Electrolux|Assa|Abloy|Swedish|Match|Oriflame|Thule|Hexagon|Autoliv|Securitas|NCC|Peab|Skanska|Boliden|SSAB|Stora|Enso|UPM|Kone|Metso|Outotec|Nokia|Fortum|Nestle|Roche|Novartis|ABB|Swisscom|UBS|Credit|Suisse|Zurich|Swiss|Re|Chubb|ACE|Swiss|Life|Helvetia|Baloise|GAM|Julius|Baer|Pictet|Vontobel|EFG|Lombard|Odier|Mirabaud|Cie|Financiere|Richemont|Swatch|Nestle|Roche|Novartis|ABB|LafargeHolcim|Swisscom|UBS|Credit|Suisse|Zurich|Swiss|Re|Chubb|ACE|Swiss|Life|Helvetia|Baloise|GAM|Julius|Baer|Pictet|Vontobel|EFG|Lombard|Odier|Mirabaud|Cie|Financiere|Richemont|Swatch)\b'
            company_matches = re.findall(company_pattern, text, re.IGNORECASE)
            entities.extend(company_matches)
            
            return list(set(entities))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    def analyze_sentiment_nltk(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using NLTK VADER"""
        try:
            if not self.nltk_analyzer:
                return {'compound': 0.0, 'pos': 0.0, 'neu': 0.0, 'neg': 0.0}
            
            scores = self.nltk_analyzer.polarity_scores(text)
            return scores
            
        except Exception as e:
            logger.error(f"Error with NLTK sentiment analysis: {e}")
            return {'compound': 0.0, 'pos': 0.0, 'neu': 0.0, 'neg': 0.0}
    
    def analyze_sentiment_textblob(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': abs(polarity)
            }
            
        except Exception as e:
            logger.error(f"Error with TextBlob sentiment analysis: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.0, 'confidence': 0.0}
    
    async def analyze_sentiment_generative(self, text: str, context: str = "") -> Dict[str, Any]:
        """Analyze sentiment using generative AI (simulated)"""
        try:
            # This is a simulated generative AI analysis
            # In a real implementation, you would call OpenAI, Anthropic, or other APIs
            
            # Simulate API call delay
            await asyncio.sleep(0.1)
            
            # Simulate generative analysis
            base_sentiment = np.random.uniform(-0.8, 0.8)
            confidence = np.random.uniform(0.7, 0.95)
            
            # Generate aspect-based sentiment
            aspects = {
                'price': np.random.uniform(-1, 1),
                'adoption': np.random.uniform(-1, 1),
                'technology': np.random.uniform(-1, 1),
                'regulation': np.random.uniform(-1, 1),
                'market': np.random.uniform(-1, 1)
            }
            
            # Generate emotion analysis
            emotions = {
                'fear': np.random.uniform(0, 1),
                'greed': np.random.uniform(0, 1),
                'hope': np.random.uniform(0, 1),
                'excitement': np.random.uniform(0, 1),
                'uncertainty': np.random.uniform(0, 1)
            }
            
            # Generate explanation
            explanation = f"Generative analysis indicates {'bullish' if base_sentiment > 0 else 'bearish'} sentiment with {confidence:.2f} confidence."
            
            return {
                'sentiment_score': base_sentiment,
                'confidence': confidence,
                'aspects': aspects,
                'emotions': emotions,
                'explanation': explanation,
                'keywords': ['bitcoin', 'crypto', 'market', 'trading', 'investment'],
                'method': 'generative_ai'
            }
            
        except Exception as e:
            logger.error(f"Error with generative sentiment analysis: {e}")
            return {
                'sentiment_score': 0.0,
                'confidence': 0.5,
                'aspects': {},
                'emotions': {},
                'explanation': "Generative analysis failed",
                'keywords': [],
                'method': 'generative_ai'
            }
    
    def calculate_social_engagement_score(self, sentiment_data: SentimentData) -> float:
        """Calculate social engagement score"""
        try:
            # Base score from interactions
            base_score = (
                sentiment_data.likes * 0.1 +
                sentiment_data.shares * 0.3 +
                sentiment_data.comments * 0.2 +
                sentiment_data.reach * 0.0001
            )
            
            # Boost for verified accounts
            if sentiment_data.verified:
                base_score *= 1.5
            
            # Normalize to 0-1 range
            engagement_score = min(base_score / 1000, 1.0)
            
            return engagement_score
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.0
    
    def calculate_market_impact_score(self, sentiment_analysis: SentimentAnalysis) -> float:
        """Calculate potential market impact score"""
        try:
            # Base factors
            sentiment_strength = abs(sentiment_analysis.sentiment_score)
            confidence = sentiment_analysis.confidence
            relevance = sentiment_analysis.relevance_score
            engagement = sentiment_analysis.social_engagement_score
            
            # Source weight
            source_weights = {
                SentimentSource.NEWS: 2.0,
                SentimentSource.ANALYST_REPORTS: 1.8,
                SentimentSource.TWITTER: 1.0,
                SentimentSource.REDDIT: 0.8,
                SentimentSource.FORUMS: 0.6,
                SentimentSource.SOCIAL_MEDIA: 0.7
            }
            
            source_weight = source_weights.get(sentiment_analysis.data.source, 1.0)
            
            # Calculate impact score
            impact_score = (
                sentiment_strength * 0.3 +
                confidence * 0.2 +
                relevance * 0.2 +
                engagement * 0.2 +
                (1.0 if sentiment_analysis.data.verified else 0.5) * 0.1
            ) * source_weight
            
            return min(impact_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating market impact score: {e}")
            return 0.0
    
    def categorize_sentiment(self, score: float) -> SentimentCategory:
        """Categorize sentiment score"""
        if score >= 0.7:
            return SentimentCategory.VERY_BULLISH
        elif score >= 0.3:
            return SentimentCategory.BULLISH
        elif score >= -0.3:
            return SentimentCategory.NEUTRAL
        elif score >= -0.7:
            return SentimentCategory.BEARISH
        else:
            return SentimentCategory.VERY_BEARISH
    
    def determine_sentiment_type(self, text: str, entities: List[str]) -> SentimentType:
        """Determine the type of sentiment based on content and entities"""
        text_lower = text.lower()
        
        # Check for crypto-related terms
        crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency', 'blockchain', 'defi', 'nft']
        if any(keyword in text_lower for keyword in crypto_keywords) or any(entity.upper() in ['BTC', 'ETH', 'ADA', 'SOL'] for entity in entities):
            return SentimentType.CRYPTO
        
        # Check for forex-related terms
        forex_keywords = ['forex', 'currency', 'usd', 'eur', 'gbp', 'jpy', 'aud', 'cad', 'chf', 'nzd']
        if any(keyword in text_lower for keyword in forex_keywords):
            return SentimentType.FOREX
        
        # Check for stock-related terms
        stock_keywords = ['stock', 'shares', 'equity', 'dividend', 'earnings', 'revenue']
        if any(keyword in text_lower for keyword in stock_keywords):
            return SentimentType.STOCK
        
        # Check for commodity-related terms
        commodity_keywords = ['gold', 'silver', 'oil', 'commodity', 'futures', 'options']
        if any(keyword in text_lower for keyword in commodity_keywords):
            return SentimentType.COMMODITY
        
        # Check for technical analysis terms
        technical_keywords = ['support', 'resistance', 'trend', 'momentum', 'rsi', 'macd', 'bollinger', 'fibonacci']
        if any(keyword in text_lower for keyword in technical_keywords):
            return SentimentType.TECHNICAL
        
        # Check for fundamental analysis terms
        fundamental_keywords = ['fundamental', 'valuation', 'pe_ratio', 'earnings', 'revenue', 'growth']
        if any(keyword in text_lower for keyword in fundamental_keywords):
            return SentimentType.FUNDAMENTAL
        
        # Check for regulatory terms
        regulatory_keywords = ['regulation', 'sec', 'compliance', 'legal', 'government']
        if any(keyword in text_lower for keyword in regulatory_keywords):
            return SentimentType.REGULATORY
        
        # Check for adoption terms
        adoption_keywords = ['adoption', 'institutional', 'mainstream', 'acceptance', 'integration']
        if any(keyword in text_lower for keyword in adoption_keywords):
            return SentimentType.ADOPTION
        
        # Check for institutional terms
        institutional_keywords = ['institutional', 'hedge_fund', 'pension', 'sovereign', 'central_bank']
        if any(keyword in text_lower for keyword in institutional_keywords):
            return SentimentType.INSTITUTIONAL
        
        return SentimentType.MARKET
    
    async def analyze_sentiment(self, sentiment_data: SentimentData) -> SentimentAnalysis:
        """Perform comprehensive sentiment analysis"""
        try:
            # Check cache first
            cache_key = f"sentiment_{self.generate_content_hash(sentiment_data.content, sentiment_data.source.value)}"
            cached_result = self.get_cached_result(cache_key)
            
            if cached_result:
                return cached_result
            
            # Preprocess text
            processed_text = self.preprocess_text(sentiment_data.content)
            
            # Extract entities and keywords
            entities = self.extract_entities(sentiment_data.content)
            entities.extend(sentiment_data.entities)
            
            # Perform multiple sentiment analyses
            sentiment_scores = []
            confidence_scores = []
            
            # NLTK analysis
            if self.config['analysis']['enable_nltk']:
                nltk_result = self.analyze_sentiment_nltk(processed_text)
                sentiment_scores.append(nltk_result['compound'])
                confidence_scores.append(abs(nltk_result['compound']))
            
            # TextBlob analysis
            if self.config['analysis']['enable_textblob']:
                textblob_result = self.analyze_sentiment_textblob(processed_text)
                sentiment_scores.append(textblob_result['polarity'])
                confidence_scores.append(textblob_result['confidence'])
            
            # Generative AI analysis
            if self.config['analysis']['enable_generative']:
                generative_result = await self.analyze_sentiment_generative(
                    processed_text, 
                    context=f"Market analysis for {entities}"
                )
                sentiment_scores.append(generative_result['sentiment_score'])
                confidence_scores.append(generative_result['confidence'])
            
            # Combine results (weighted average)
            if sentiment_scores:
                final_score = np.average(sentiment_scores, weights=confidence_scores)
                final_confidence = np.mean(confidence_scores)
            else:
                final_score = 0.0
                final_confidence = 0.5
            
            # Calculate additional scores
            social_engagement = self.calculate_social_engagement_score(sentiment_data)
            
            # Determine sentiment category and type
            category = self.categorize_sentiment(final_score)
            sentiment_type = self.determine_sentiment_type(sentiment_data.content, entities)
            
            # Calculate relevance score (based on entity match)
            relevance_score = min(len(entities) / 5, 1.0) if entities else 0.5
            
            # Create analysis result
            analysis = SentimentAnalysis(
                data=sentiment_data,
                sentiment_score=final_score,
                confidence=final_confidence,
                category=category,
                type=sentiment_type,
                entities=entities,
                keywords=self.extract_keywords(processed_text),
                emotions=generative_result.get('emotions', {}) if self.config['analysis']['enable_generative'] else {},
                aspects=generative_result.get('aspects', {}) if self.config['analysis']['enable_generative'] else {},
                relevance_score=relevance_score,
                market_impact_score=0.0,  # Will be calculated later
                social_engagement_score=social_engagement
            )
            
            # Calculate market impact score
            analysis.market_impact_score = self.calculate_market_impact_score(analysis)
            
            # Cache result
            self.cache_result(cache_key, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            # Return neutral sentiment with low confidence
            return SentimentAnalysis(
                data=sentiment_data,
                sentiment_score=0.0,
                confidence=0.3,
                category=SentimentCategory.NEUTRAL,
                type=SentimentType.MARKET,
                entities=[],
                keywords=[],
                emotions={},
                aspects={},
                relevance_score=0.5,
                market_impact_score=0.0,
                social_engagement_score=0.0
            )
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        try:
            # Simple keyword extraction
            words = word_tokenize(text.lower())
            words = [word for word in words if word not in self.stop_words and len(word) > 2]
            
            # Calculate word frequency
            word_freq = defaultdict(int)
            for word in words:
                word_freq[word] += 1
            
            # Return top keywords
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:10]]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    async def fetch_social_data(self, symbol: str, hours_back: int = 24) -> List[SentimentData]:
        """Fetch social media data (simulated)"""
        sentiment_data = []
        
        try:
            # Simulate fetching data from various sources
            
            # Twitter data (simulated)
            if self.config['sources']['twitter']['enabled'] and not self.is_rate_limited('twitter'):
                self.record_api_call('twitter')
                
                # Simulate Twitter API response
                for i in range(np.random.randint(10, 50)):
                    content = self.generate_sample_tweet(symbol)
                    sentiment_data.append(SentimentData(
                        source=SentimentSource.TWITTER,
                        content=content,
                        timestamp=datetime.now() - timedelta(hours=np.random.randint(0, hours_back)),
                        author=f"user_{i}",
                        likes=np.random.randint(0, 1000),
                        shares=np.random.randint(0, 500),
                        comments=np.random.randint(0, 200),
                        reach=np.random.randint(100, 10000),
                        verified=np.random.choice([True, False], p=[0.1, 0.9]),
                        entities=[symbol]
                    ))
            
            # Reddit data (simulated)
            if self.config['sources']['reddit']['enabled'] and not self.is_rate_limited('reddit'):
                self.record_api_call('reddit')
                
                # Simulate Reddit API response
                for i in range(np.random.randint(5, 20)):
                    content = self.generate_sample_reddit_post(symbol)
                    sentiment_data.append(SentimentData(
                        source=SentimentSource.REDDIT,
                        content=content,
                        timestamp=datetime.now() - timedelta(hours=np.random.randint(0, hours_back)),
                        author=f"reddit_user_{i}",
                        likes=np.random.randint(0, 500),
                        shares=np.random.randint(0, 100),
                        comments=np.random.randint(0, 50),
                        reach=np.random.randint(50, 5000),
                        entities=[symbol]
                    ))
            
            # News data (simulated)
            if self.config['sources']['news']['enabled'] and not self.is_rate_limited('news'):
                self.record_api_call('news')
                
                # Simulate News API response
                for i in range(np.random.randint(3, 15)):
                    content = self.generate_sample_news_article(symbol)
                    sentiment_data.append(SentimentData(
                        source=SentimentSource.NEWS,
                        content=content,
                        timestamp=datetime.now() - timedelta(hours=np.random.randint(0, hours_back)),
                        author=f"news_source_{i}",
                        likes=np.random.randint(0, 200),
                        shares=np.random.randint(0, 300),
                        comments=np.random.randint(0, 100),
                        reach=np.random.randint(1000, 50000),
                        verified=True,  # News sources are verified
                        entities=[symbol]
                    ))
            
            logger.info(f"Fetched {len(sentiment_data)} sentiment data points for {symbol}")
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error fetching social data for {symbol}: {e}")
            return []
    
    def generate_sample_tweet(self, symbol: str) -> str:
        """Generate sample tweet content"""
        templates = [
            f"{symbol} looking bullish! 🚀 Time to buy more!",
            f"Just sold my {symbol} position. Market looking shaky 📉",
            f"{symbol} breaking resistance levels! Technical analysis looks good 📈",
            f"Holding {symbol} long term. Fundamentals are strong 💪",
            f"{symbol} price prediction: $50k by end of year! 🎯",
            f"Market sentiment for {symbol} is very positive right now 😊",
            f"Warning: {symbol} might be overbought. Be careful! ⚠️",
            f"{symbol} adoption growing rapidly! Institutional interest rising 🏦",
            f"Regulatory news affecting {symbol}. Stay informed 📰",
            f"{symbol} technical indicators showing bullish divergence 📊"
        ]
        
        return np.random.choice(templates)
    
    def generate_sample_reddit_post(self, symbol: str) -> str:
        """Generate sample Reddit post content"""
        templates = [
            f"What are your thoughts on {symbol} for the next quarter? I'm seeing mixed signals in the market.",
            f"Just did some analysis on {symbol}. The fundamentals look solid but technical indicators are concerning.",
            f"{symbol} has been consolidating for weeks. When do you think we'll see a breakout?",
            f"Institutional adoption of {symbol} is accelerating. This could be huge for long-term holders.",
            f"Market sentiment around {symbol} seems to be shifting. Anyone else noticing this?",
            f"Technical analysis of {symbol} shows potential for significant movement in either direction.",
            f"The recent regulatory developments could impact {symbol} significantly. Thoughts?",
            f"{symbol} correlation with traditional markets is increasing. Important to consider for portfolio allocation."
        ]
        
        return np.random.choice(templates)
    
    def generate_sample_news_article(self, symbol: str) -> str:
        """Generate sample news article content"""
        templates = [
            f"Major financial institution announces significant investment in {symbol}, citing strong fundamentals and growing adoption.",
            f"Regulatory clarity improves for {symbol} as government releases new guidelines for cryptocurrency operations.",
            f"Technical analysis shows {symbol} approaching key resistance levels with increased trading volume.",
            f"Market experts predict substantial growth for {symbol} based on on-chain metrics and adoption trends.",
            f"Institutional investors show renewed interest in {symbol} as macroeconomic conditions shift.",
            f"Development activity for {symbol} ecosystem reaches all-time high with multiple protocol upgrades.",
            f"Global adoption of {symbol} accelerates as more merchants begin accepting cryptocurrency payments.",
            f"Analysts upgrade price targets for {symbol} following strong quarterly performance and positive outlook."
        ]
        
        return np.random.choice(templates)
    
    async def analyze_symbol_sentiment(self, symbol: str, hours_back: int = 24) -> List[SentimentAnalysis]:
        """Analyze sentiment for a specific symbol"""
        try:
            # Fetch social data
            sentiment_data = await self.fetch_social_data(symbol, hours_back)
            
            if not sentiment_data:
                logger.warning(f"No sentiment data available for {symbol}")
                return []
            
            # Analyze each data point
            analyses = []
            
            for data in sentiment_data:
                analysis = await self.analyze_sentiment(data)
                analyses.append(analysis)
                
                # Add small delay to avoid overwhelming APIs
                await asyncio.sleep(0.1)
            
            logger.info(f"Analyzed {len(analyses)} sentiment items for {symbol}")
            return analyses
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {symbol}: {e}")
            return []
    
    async def aggregate_sentiment(self, *args, **kwargs):
        """Aggregate sentiment data with two call signatures.
        - Internal: first arg is List[SentimentAnalysis] → returns SentimentAggregation
        - Runner: (symbol: str, hours_back: int) → returns dict summary
        """
        try:
            # Branch 1: internal aggregation from provided analyses
            if args and isinstance(args[0], list):
                analyses: List[SentimentAnalysis] = args[0]
                symbol: str = args[1] if len(args) > 1 else kwargs.get('symbol', 'UNKNOWN')
                timeframe: str = args[2] if len(args) > 2 else kwargs.get('timeframe', '1h')

                if not analyses:
                    return SentimentAggregation(
                        symbol=symbol,
                        timeframe=timeframe,
                        start_time=datetime.now() - timedelta(hours=1),
                        end_time=datetime.now(),
                        overall_score=0.0,
                        overall_category=SentimentCategory.NEUTRAL,
                        confidence=0.0,
                        sample_size=0,
                        source_distribution={},
                        category_distribution={},
                        trend="stable",
                        volatility=0.0,
                        momentum=0.0,
                        key_topics=[],
                        influential_sources=[],
                        market_correlation=0.0,
                        leading_indicators=[],
                        sentiment_history=[]
                    )

                # Calculate overall sentiment score (weighted average)
                scores = [analysis.sentiment_score for analysis in analyses]
                confidences = [analysis.confidence for analysis in analyses]

                overall_score = (
                    np.average(scores, weights=confidences)
                    if confidences and sum(confidences) > 0
                    else float(np.mean(scores)) if scores else 0.0
                )
                overall_confidence = float(np.mean(confidences)) if confidences else 0.0
                overall_category = self.categorize_sentiment(overall_score)

                # Volatility
                volatility = float(np.std(scores)) if scores else 0.0

                # Momentum via slope of fitted line
                if len(scores) > 1:
                    x = np.arange(len(scores))
                    try:
                        momentum = float(np.polyfit(x, scores, 1)[0])
                    except Exception:
                        momentum = 0.0
                else:
                    momentum = 0.0

                # Trend
                if momentum > 0.1:
                    trend = "improving"
                elif momentum < -0.1:
                    trend = "deteriorating"
                else:
                    trend = "stable"

                # Distributions
                source_dist = defaultdict(int)
                category_dist = defaultdict(int)
                for analysis in analyses:
                    source_dist[analysis.data.source.value] += 1
                    category_dist[analysis.category.value] += 1

                # Key topics
                keyword_freq = defaultdict(int)
                for analysis in analyses:
                    for kw in analysis.keywords:
                        keyword_freq[kw] += 1
                key_topics = [k for k, _ in sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]]

                # Influential sources
                influential_sources = list({
                    a.data.source.value
                    for a in analyses
                    if a.data.verified or a.market_impact_score > 0.7
                })

                sentiment_history = scores[-20:] if len(scores) > 20 else scores

                return SentimentAggregation(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_time=min(a.data.timestamp for a in analyses),
                    end_time=max(a.data.timestamp for a in analyses),
                    overall_score=overall_score,
                    overall_category=overall_category,
                    confidence=overall_confidence,
                    sample_size=len(analyses),
                    source_distribution=dict(source_dist),
                    category_distribution=dict(category_dist),
                    trend=trend,
                    volatility=volatility,
                    momentum=momentum,
                    key_topics=key_topics,
                    influential_sources=influential_sources,
                    market_correlation=0.0,
                    leading_indicators=["social_volume", "engagement_rate", "sentiment_momentum"],
                    sentiment_history=sentiment_history
                )

            # Branch 2: runner-style summary from symbol and hours_back
            symbol: str = args[0] if args else kwargs.get('symbol', 'UNKNOWN')
            hours_back: int = args[1] if len(args) > 1 else kwargs.get('hours_back', 24)

            analyses = await self.analyze_symbol_sentiment(symbol, hours_back)
            if not analyses:
                return {
                    'symbol': symbol,
                    'sentiment_score': 0.0,
                    'category': 'NEUTRAL',
                    'confidence': 0.0,
                    'sample_size': 0,
                    'source_distribution': {},
                    'trend': 'stable'
                }

            scores = [a.sentiment_score for a in analyses]
            confidences = [a.confidence for a in analyses]
            overall_score = (
                np.average(scores, weights=confidences)
                if confidences and sum(confidences) > 0
                else float(np.mean(scores))
            )
            overall_confidence = float(np.mean(confidences)) if confidences else 0.0
            category_enum = self.categorize_sentiment(overall_score)
            if category_enum in (SentimentCategory.VERY_BULLISH, SentimentCategory.BULLISH):
                category_str = 'BULLISH'
            elif category_enum in (SentimentCategory.VERY_BEARISH, SentimentCategory.BEARISH):
                category_str = 'BEARISH'
            else:
                category_str = 'NEUTRAL'

            source_dist = defaultdict(int)
            for a in analyses:
                source_dist[a.data.source.value] += 1

            return {
                'symbol': symbol,
                'sentiment_score': float(overall_score),
                'category': category_str,
                'confidence': float(overall_confidence),
                'sample_size': len(analyses),
                'source_distribution': dict(source_dist)
            }

        except Exception as e:
            logger.error(f"Error aggregating sentiment: {e}")
            # Fallback neutral summary for runner
            if args and not isinstance(args[0], list):
                symbol = args[0] if args else kwargs.get('symbol', 'UNKNOWN')
                return {
                    'symbol': symbol,
                    'sentiment_score': 0.0,
                    'category': 'NEUTRAL',
                    'confidence': 0.0,
                    'sample_size': 0,
                    'source_distribution': {}
                }
            # Fallback aggregation object for internal usage
            symbol = kwargs.get('symbol', 'UNKNOWN') if not args else (args[1] if len(args) > 1 else 'UNKNOWN')
            timeframe = kwargs.get('timeframe', '1h') if not args else (args[2] if len(args) > 2 else '1h')
            return SentimentAggregation(
                symbol=symbol,
                timeframe=timeframe,
                start_time=datetime.now() - timedelta(hours=1),
                end_time=datetime.now(),
                overall_score=0.0,
                overall_category=SentimentCategory.NEUTRAL,
                confidence=0.0,
                sample_size=0,
                source_distribution={},
                category_distribution={},
                trend="stable",
                volatility=0.0,
                momentum=0.0,
                key_topics=[],
                influential_sources=[],
                market_correlation=0.0,
                leading_indicators=[],
                sentiment_history=[]
            )
    
    async def get_sentiment_summary(self, symbol: str, hours_back: int = 24) -> Dict[str, Any]:
        """Get comprehensive sentiment summary for a symbol"""
        try:
            # Analyze sentiment
            analyses = await self.analyze_symbol_sentiment(symbol, hours_back)
            
            if not analyses:
                return {
                    'symbol': symbol,
                    'status': 'no_data',
                    'message': f'No sentiment data available for {symbol} in the last {hours_back} hours',
                    'aggregation': None,
                    'analyses': []
                }
            
            # Aggregate sentiment (internal aggregation object)
            aggregation = await self.aggregate_sentiment(analyses, symbol)
            
            # Generate summary
            summary = {
                'symbol': symbol,
                'status': 'success',
                'aggregation': aggregation,
                'analyses': analyses,
                'summary': {
                    'total_analyses': len(analyses),
                    'sentiment_breakdown': {
                        'very_bullish': len([a for a in analyses if a.category == SentimentCategory.VERY_BULLISH]),
                        'bullish': len([a for a in analyses if a.category == SentimentCategory.BULLISH]),
                        'neutral': len([a for a in analyses if a.category == SentimentCategory.NEUTRAL]),
                        'bearish': len([a for a in analyses if a.category == SentimentCategory.BEARISH]),
                        'very_bearish': len([a for a in analyses if a.category == SentimentCategory.VERY_BEARISH])
                    },
                    'source_breakdown': dict(aggregation.source_distribution),
                    'avg_confidence': aggregation.confidence,
                    'avg_market_impact': np.mean([a.market_impact_score for a in analyses]),
                    'trend': aggregation.trend,
                    'volatility': aggregation.volatility,
                    'key_topics': aggregation.key_topics[:5],
                    'influential_sources': aggregation.influential_sources
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting sentiment summary for {symbol}: {e}")
            return {
                'symbol': symbol,
                'status': 'error',
                'message': str(e),
                'aggregation': None,
                'analyses': []
            }
    
    async def scan_market_sentiment(self, symbols: List[str], hours_back: int = 24) -> Dict[str, Any]:
        """Scan sentiment for multiple symbols"""
        try:
            results = {}
            
            for symbol in symbols:
                try:
                    summary = await self.get_sentiment_summary(symbol, hours_back)
                    results[symbol] = summary
                    
                    # Add delay between symbols to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error analyzing sentiment for {symbol}: {e}")
                    results[symbol] = {
                        'symbol': symbol,
                        'status': 'error',
                        'message': str(e),
                        'aggregation': None,
                        'analyses': []
                    }
            
            # Calculate market-wide sentiment
            market_sentiment = self.calculate_market_sentiment(results)
            
            return {
                'scan_results': results,
                'market_sentiment': market_sentiment,
                'timestamp': datetime.now(),
                'total_symbols': len(symbols),
                'successful_analyses': len([r for r in results.values() if r['status'] == 'success'])
            }
            
        except Exception as e:
            logger.error(f"Error scanning market sentiment: {e}")
            return {
                'scan_results': {},
                'market_sentiment': None,
                'timestamp': datetime.now(),
                'total_symbols': len(symbols),
                'successful_analyses': 0,
                'error': str(e)
            }
    
    def calculate_market_sentiment(self, symbol_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall market sentiment from symbol results"""
        try:
            valid_results = [r for r in symbol_results.values() if r['status'] == 'success' and r['aggregation']]
            
            if not valid_results:
                return {
                    'overall_score': 0.0,
                    'category': SentimentCategory.NEUTRAL,
                    'confidence': 0.0,
                    'bullish_symbols': [],
                    'bearish_symbols': [],
                    'neutral_symbols': []
                }
            
            # Calculate weighted average sentiment
            scores = [r['aggregation'].overall_score for r in valid_results]
            confidences = [r['aggregation'].confidence for r in valid_results]
            
            market_score = np.average(scores, weights=confidences)
            market_confidence = np.mean(confidences)
            market_category = self.categorize_sentiment(market_score)
            
            # Categorize symbols
            bullish_symbols = [r['symbol'] for r in valid_results if r['aggregation'].overall_score > 0.3]
            bearish_symbols = [r['symbol'] for r in valid_results if r['aggregation'].overall_score < -0.3]
            neutral_symbols = [r['symbol'] for r in valid_results if -0.3 <= r['aggregation'].overall_score <= 0.3]
            
            return {
                'overall_score': market_score,
                'category': market_category,
                'confidence': market_confidence,
                'bullish_symbols': bullish_symbols,
                'bearish_symbols': bearish_symbols,
                'neutral_symbols': neutral_symbols,
                'total_symbols': len(valid_results)
            }
            
        except Exception as e:
            logger.error(f"Error calculating market sentiment: {e}")
            return {
                'overall_score': 0.0,
                'category': SentimentCategory.NEUTRAL,
                'confidence': 0.0,
                'bullish_symbols': [],
                'bearish_symbols': [],
                'neutral_symbols': []
            }

    # --- Runner compatibility helpers ---
    async def initialize(self):
        """Initialize analyzers and database for runner usage."""
        try:
            # Reinitialize analyzers if needed
            self.initialize_analyzers()
            # Ensure database is set up
            if self.db_connection is None:
                self.setup_database()
            # Ensure API clients ready
            if not hasattr(self, 'api_clients'):
                self.setup_api_clients()
            logger.info("GenerativeSentimentAnalyzer initialized for runner.")
            return True
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False

    async def fetch_twitter_sentiment(self, symbol: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Simulate fetching Twitter sentiment data and return simplified entries."""
        try:
            data_points = await self.fetch_social_data(symbol, hours_back)
            results = []
            for d in data_points:
                if d.source == SentimentSource.TWITTER:
                    analysis = await self.analyze_sentiment(d)
                    results.append({
                        'content': d.content,
                        'timestamp': d.timestamp,
                        'author': d.author,
                        'likes': d.likes,
                        'shares': d.shares,
                        'comments': d.comments,
                        'reach': d.reach,
                        'verified': d.verified,
                        'sentiment_score': analysis.sentiment_score,
                        'confidence': analysis.confidence,
                        'category': analysis.category.value
                    })
            return results
        except Exception as e:
            logger.error(f"Error fetching Twitter sentiment: {e}")
            return []

    async def fetch_reddit_sentiment(self, symbol: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Simulate fetching Reddit sentiment data and return simplified entries."""
        try:
            data_points = await self.fetch_social_data(symbol, hours_back)
            results = []
            for d in data_points:
                if d.source == SentimentSource.REDDIT:
                    analysis = await self.analyze_sentiment(d)
                    results.append({
                        'content': d.content,
                        'timestamp': d.timestamp,
                        'author': d.author,
                        'likes': d.likes,
                        'shares': d.shares,
                        'comments': d.comments,
                        'reach': d.reach,
                        'verified': d.verified,
                        'sentiment_score': analysis.sentiment_score,
                        'confidence': analysis.confidence,
                        'category': analysis.category.value
                    })
            return results
        except Exception as e:
            logger.error(f"Error fetching Reddit sentiment: {e}")
            return []

    async def fetch_news_sentiment(self, symbol: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Simulate fetching News sentiment data and return simplified entries."""
        try:
            data_points = await self.fetch_social_data(symbol, hours_back)
            results = []
            for d in data_points:
                if d.source == SentimentSource.NEWS:
                    analysis = await self.analyze_sentiment(d)
                    results.append({
                        'content': d.content,
                        'timestamp': d.timestamp,
                        'author': d.author,
                        'likes': d.likes,
                        'shares': d.shares,
                        'comments': d.comments,
                        'reach': d.reach,
                        'verified': d.verified,
                        'sentiment_score': analysis.sentiment_score,
                        'confidence': analysis.confidence,
                        'category': analysis.category.value
                    })
            return results
        except Exception as e:
            logger.error(f"Error fetching News sentiment: {e}")
            return []

    async def calculate_market_impact(self, symbol: str, aggregated_sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate simplified market impact based on aggregated sentiment."""
        try:
            score = float(aggregated_sentiment.get('sentiment_score', 0.0) or 0.0)
            confidence = float(aggregated_sentiment.get('confidence', 0.0) or 0.0)
            impact_score = max(0.0, min(1.0, abs(score) * 0.6 + confidence * 0.4))
            # Simple risk proxies
            volatility_risk = max(0.0, min(1.0, 0.5 + (impact_score - 0.5) * 0.5))
            liquidity_effect = max(0.0, min(1.0, 0.5 + (abs(score) - 0.3) * 0.4))
            return {
                'symbol': symbol,
                'impact_score': impact_score,
                'volatility_risk': volatility_risk,
                'liquidity_effect': liquidity_effect
            }
        except Exception as e:
            logger.error(f"Error calculating market impact: {e}")
            return {'symbol': symbol, 'impact_score': 0.0, 'volatility_risk': 0.0, 'liquidity_effect': 0.0}

    async def generate_sentiment_signals(self, symbol: str, aggregated_sentiment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading signals based on sentiment summary."""
        try:
            score = float(aggregated_sentiment.get('sentiment_score', 0.0) or 0.0)
            confidence = float(aggregated_sentiment.get('confidence', 0.0) or 0.0)
            category = aggregated_sentiment.get('category', 'NEUTRAL')
            signals = []
            if category == 'BULLISH' and confidence >= 0.6 and score > 0.2:
                strength = min(1.0, score * confidence)
                signals.append({'symbol': symbol, 'signal': 'BUY', 'strength': strength, 'reason': 'Bullish sentiment with good confidence'})
            elif category == 'BEARISH' and confidence >= 0.6 and score < -0.2:
                strength = min(1.0, abs(score) * confidence)
                signals.append({'symbol': symbol, 'signal': 'SELL', 'strength': strength, 'reason': 'Bearish sentiment with good confidence'})
            else:
                signals.append({'symbol': symbol, 'signal': 'NEUTRAL', 'strength': max(0.0, 0.5 - abs(score)), 'reason': 'Neutral or low-confidence sentiment'})
            return signals
        except Exception as e:
            logger.error(f"Error generating sentiment signals: {e}")
            return []

    async def extract_topics(self, symbol: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Extract trending topics based on keywords from analyses."""
        try:
            analyses = await self.analyze_symbol_sentiment(symbol, hours_back)
            keyword_freq = defaultdict(int)
            impact_accum = defaultdict(float)
            for a in analyses:
                for kw in a.keywords:
                    keyword_freq[kw] += 1
                    impact_accum[kw] += a.sentiment_score
            topics = []
            for kw, freq in keyword_freq.items():
                topics.append({
                    'topic': kw,
                    'frequency': freq,
                    'sentiment_impact': float(impact_accum[kw] / max(1, freq))
                })
            # Sort by frequency and impact
            topics.sort(key=lambda x: (x['frequency'], abs(x['sentiment_impact'])), reverse=True)
            return topics[:20]
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []

# Example usage and testing
async def example_usage():
    """
    Example usage of the Generative Sentiment Analysis system
    """
    
    # Create sentiment analyzer
    analyzer = GenerativeSentimentAnalyzer()
    
    # Test with individual symbol
    print("Analyzing sentiment for BTC...")
    btc_sentiment = await analyzer.get_sentiment_summary("BTC", hours_back=24)
    
    if btc_sentiment['status'] == 'success':
        print(f"BTC Sentiment Summary:")
        print(f"  Overall Score: {btc_sentiment['aggregation'].overall_score:.3f}")
        print(f"  Category: {btc_sentiment['aggregation'].overall_category.value}")
        print(f"  Confidence: {btc_sentiment['aggregation'].confidence:.3f}")
        print(f"  Trend: {btc_sentiment['aggregation'].trend}")
        print(f"  Sample Size: {btc_sentiment['aggregation'].sample_size}")
        print(f"  Key Topics: {', '.join(btc_sentiment['aggregation'].key_topics[:3])}")
        print()
    
    # Test with multiple symbols
    symbols = ["BTC", "ETH", "ADA", "SOL", "DOT"]
    print(f"Scanning sentiment for {len(symbols)} symbols...")
    
    market_scan = await analyzer.scan_market_sentiment(symbols, hours_back=12)
    
    print(f"Market Sentiment Scan Results:")
    print(f"  Total Symbols: {market_scan['total_symbols']}")
    print(f"  Successful Analyses: {market_scan['successful_analyses']}")
    print(f"  Timestamp: {market_scan['timestamp']}")
    
    if market_scan['market_sentiment']:
        market_sentiment = market_scan['market_sentiment']
        print(f"  Market Overall Score: {market_sentiment['overall_score']:.3f}")
        print(f"  Market Category: {market_sentiment['category'].value}")
        print(f"  Market Confidence: {market_sentiment['confidence']:.3f}")
        print(f"  Bullish Symbols: {len(market_sentiment['bullish_symbols'])}")
        print(f"  Bearish Symbols: {len(market_sentiment['bearish_symbols'])}")
        print(f"  Neutral Symbols: {len(market_sentiment['neutral_symbols'])}")
        print()
    
    # Show individual symbol results
    print("Individual Symbol Results:")
    for symbol in symbols:
        if symbol in market_scan['scan_results']:
            result = market_scan['scan_results'][symbol]
            if result['status'] == 'success' and result['aggregation']:
                print(f"  {symbol}: {result['aggregation'].overall_category.value} "
                      f"({result['aggregation'].overall_score:.3f}) "
                      f"- {result['aggregation'].sample_size} samples")
    
    print("\nSentiment analysis completed successfully!")

if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())