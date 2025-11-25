"""
Modelos de Machine Learning para Análise Forex
Previsão de movimentos de pares de moedas
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import asyncio
from loguru import logger

@dataclass
class ForexMLPrediction:
    """Resultado da previsão ML para forex"""
    symbol: str
    prediction: str  # buy, sell, hold
    confidence: float
    probability_up: float
    probability_down: float
    next_price: float
    price_change: float
    features_used: List[str]
    model_accuracy: float
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'prediction': self.prediction,
            'confidence': self.confidence,
            'probability_up': self.probability_up,
            'probability_down': self.probability_down,
            'next_price': self.next_price,
            'price_change': self.price_change,
            'features_used': self.features_used,
            'model_accuracy': self.model_accuracy,
            'timestamp': self.timestamp.isoformat()
        }

class ForexMLModel:
    """Modelos de ML para análise forex"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logger.bind(component="ForexMLModel")
        
        # Configurações
        self.lookback_period = self.config.get('lookback_period', 60)
        self.forecast_horizon = self.config.get('forecast_horizon', 1)
        self.test_size = self.config.get('test_size', 0.2)
        self.random_state = self.config.get('random_state', 42)
        
        # Modelos
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.model_performance = {}
        
        # Features
        self.technical_features = [
            'rsi', 'macd', 'macd_signal', 'bb_position', 'atr', 'adx',
            'stoch_k', 'stoch_d', 'ema_20_slope', 'ema_50_slope', 'volume_ratio'
        ]
        
        self.forex_specific_features = [
            'spread', 'volatility_pips', 'correlation_score', 'carry_trade_score',
            'session_volume', 'economic_calendar_impact', 'central_bank_bias'
        ]
        
        self.sentiment_features = [
            'news_sentiment', 'social_sentiment', 'commitment_of_traders',
            'positioning_extreme', 'safe_haven_demand'
        ]
        
        self.all_features = (self.technical_features + 
                             self.forex_specific_features + 
                             self.sentiment_features)
    
    def calculate_forex_features(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Calcular features específicas para forex"""
        try:
            df_features = df.copy()
            
            # Spread (diferença entre high e low em pips)
            df_features['spread'] = (df_features['high'] - df_features['low']) * 10000
            
            # Volatilidade em pips
            df_features['volatility_pips'] = df_features['close'].rolling(20).std() * 10000
            
            # Slope das EMAs
            df_features['ema_20'] = df_features['close'].ewm(span=20).mean()
            df_features['ema_50'] = df_features['close'].ewm(span=50).mean()
            df_features['ema_20_slope'] = df_features['ema_20'].diff()
            df_features['ema_50_slope'] = df_features['ema_50'].diff()
            
            # Volume ratio
            df_features['volume_ratio'] = (df_features['volume'] / 
                                           df_features['volume'].rolling(20).mean())
            
            # Correlação com principais pares (simulada)
            if 'EUR' in symbol:
                df_features['correlation_score'] = np.random.normal(0.5, 0.1, len(df_features))
            elif 'JPY' in symbol:
                df_features['correlation_score'] = np.random.normal(-0.3, 0.1, len(df_features))
            else:
                df_features['correlation_score'] = np.random.normal(0.1, 0.1, len(df_features))
            
            # Carry trade score (diferença de taxas de juros simulada)
            carry_scores = {
                'EUR/USD': 0.02, 'GBP/USD': 0.015, 'USD/JPY': -0.01,
                'USD/CHF': -0.005, 'AUD/USD': 0.025, 'USD/CAD': 0.01,
                'NZD/USD': 0.03, 'EUR/GBP': 0.005
            }
            base_carry = carry_scores.get(symbol, 0.01)
            df_features['carry_trade_score'] = np.random.normal(base_carry, 0.005, len(df_features))
            
            # Session volume (impacto das sessões de trading)
            df_features['session_volume'] = np.sin(np.arange(len(df_features)) * 2 * np.pi / 24) * 0.3 + 0.5
            
            # Economic calendar impact (simulado)
            df_features['economic_calendar_impact'] = np.random.choice(
                [0, 0.1, 0.3, 0.5], len(df_features), p=[0.7, 0.2, 0.08, 0.02]
            )
            
            # Central bank bias (simulado)
            cb_bias = {
                'EUR': 0.1, 'USD': 0.05, 'GBP': 0.08, 'JPY': -0.05,
                'CHF': -0.02, 'AUD': 0.12, 'CAD': 0.07, 'NZD': 0.15
            }
            
            base_currency = symbol.split('/')[0] if '/' in symbol else symbol[:3]
            bias_value = cb_bias.get(base_currency, 0.05)
            df_features['central_bank_bias'] = np.random.normal(bias_value, 0.02, len(df_features))
            
            # Sentiment features (simuladas)
            df_features['news_sentiment'] = np.random.normal(0.5, 0.2, len(df_features))
            df_features['social_sentiment'] = np.random.normal(0.5, 0.15, len(df_features))
            df_features['commitment_of_traders'] = np.random.normal(0.5, 0.1, len(df_features))
            df_features['positioning_extreme'] = np.random.choice([0, 1], len(df_features), p=[0.9, 0.1])
            df_features['safe_haven_demand'] = np.random.normal(0.3, 0.1, len(df_features))
            
            return df_features
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular features forex: {str(e)}")
            return df
    
    def create_lagged_features(self, df: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
        """Criar features defasadas (lagged features)"""
        try:
            df_lagged = df.copy()
            
            for feature in self.all_features:
                if feature in df.columns:
                    for lag in range(1, lookback + 1):
                        df_lagged[f'{feature}_lag_{lag}'] = df[feature].shift(lag)
            
            # Features de momentum
            for feature in ['close', 'volume']:
                if feature in df.columns:
                    for period in [5, 10, 20]:
                        df_lagged[f'{feature}_momentum_{period}'] = (
                            df[feature] / df[feature].shift(period) - 1
                        )
            
            return df_lagged
            
        except Exception as e:
            self.logger.error(f"Erro ao criar features defasadas: {str(e)}")
            return df
    
    def create_target_variable(self, df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
        """Criar variável alvo (direção do preço)"""
        try:
            df_target = df.copy()
            
            # Preço futuro
            df_target['future_price'] = df_target['close'].shift(-horizon)
            
            # Direção do movimento
            df_target['price_direction'] = np.where(
                df_target['future_price'] > df_target['close'], 1, 0
            )
            
            # Magnitude da mudança
            df_target['price_change'] = (
                df_target['future_price'] / df_target['close'] - 1
            )
            
            # Categorizar magnitude
            df_target['price_category'] = pd.cut(
                df_target['price_change'],
                bins=[-np.inf, -0.01, 0.01, np.inf],
                labels=['down', 'neutral', 'up']
            )
            
            return df_target
            
        except Exception as e:
            self.logger.error(f"Erro ao criar variável alvo: {str(e)}")
            return df
    
    def prepare_data(self, df: pd.DataFrame, symbol: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Preparar dados para treinamento"""
        try:
            # Calcular features
            df_features = self.calculate_forex_features(df, symbol)
            
            # Criar features defasadas
            df_lagged = self.create_lagged_features(df_features)
            
            # Criar target
            df_target = self.create_target_variable(df_lagged)
            
            # Remover valores NaN
            df_clean = df_target.dropna()
            
            if len(df_clean) < 100:
                raise ValueError("Dados insuficientes para treinamento")
            
            # Selecionar features
            feature_columns = [col for col in df_clean.columns 
                             if col not in ['close', 'future_price', 'price_change', 'price_category']]
            
            X = df_clean[feature_columns].values
            y = df_clean['price_direction'].values
            
            return X, y, feature_columns
            
        except Exception as e:
            self.logger.error(f"Erro ao preparar dados: {str(e)}")
            return np.array([]), np.array([]), []
    
    def train_model(self, X: np.ndarray, y: np.ndarray, symbol: str) -> Dict:
        """Treinar modelo para um símbolo"""
        try:
            self.logger.info(f"Treinando modelo para {symbol}...")
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.test_size, random_state=self.random_state
            )
            
            # Escalar features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Treinar múltiplos modelos
            models = {
                'random_forest': RandomForestClassifier(n_estimators=100, random_state=self.random_state),
                'logistic_regression': LogisticRegression(random_state=self.random_state),
                'svm': SVC(probability=True, random_state=self.random_state)
            }
            
            best_model = None
            best_score = 0
            best_name = ""
            
            for name, model in models.items():
                try:
                    # Treinar modelo
                    model.fit(X_train_scaled, y_train)
                    
                    # Avaliar
                    y_pred = model.predict(X_test_scaled)
                    accuracy = accuracy_score(y_test, y_pred)
                    
                    # Cross-validation
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
                    cv_score = cv_scores.mean()
                    
                    self.logger.info(f"Modelo {name} - Acurácia: {accuracy:.3f}, CV: {cv_score:.3f}")
                    
                    if cv_score > best_score:
                        best_score = cv_score
                        best_model = model
                        best_name = name
                        
                except Exception as e:
                    self.logger.error(f"Erro ao treinar {name}: {str(e)}")
                    continue
            
            if best_model is None:
                raise ValueError("Nenhum modelo treinado com sucesso")
            
            # Salvar modelo e scaler
            self.models[symbol] = best_model
            self.scalers[symbol] = scaler
            
            # Feature importance (para Random Forest)
            if hasattr(best_model, 'feature_importances_'):
                self.feature_importance[symbol] = best_model.feature_importances_
            
            # Performance do modelo
            self.model_performance[symbol] = {
                'model_name': best_name,
                'accuracy': best_score,
                'test_accuracy': accuracy_score(y_test, best_model.predict(X_test_scaled)),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
            self.logger.info(f"Melhor modelo para {symbol}: {best_name} (Acurácia: {best_score:.3f})")
            
            return self.model_performance[symbol]
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelo para {symbol}: {str(e)}")
            return {}
    
    def predict(self, X: np.ndarray, symbol: str) -> Optional[ForexMLPrediction]:
        """Fazer previsão com modelo treinado"""
        try:
            if symbol not in self.models:
                self.logger.error(f"Modelo não encontrado para {symbol}")
                return None
            
            model = self.models[symbol]
            scaler = self.scalers[symbol]
            
            # Escalar features
            X_scaled = scaler.transform(X.reshape(1, -1))
            
            # Fazer previsões
            prediction = model.predict(X_scaled)[0]
            probabilities = model.predict_proba(X_scaled)[0]
            
            # Calcular confiança e probabilidades
            confidence = max(probabilities)
            probability_up = probabilities[1]  # Classe 1 = subida
            probability_down = probabilities[0]  # Classe 0 = descida
            
            # Determinar direção
            if prediction == 1:
                direction = "buy"
            else:
                direction = "sell"
            
            # Estimar próximo preço (simplificado)
            current_price = X[0] if len(X) > 0 else 1.0  # Usar primeira feature como proxy
            price_change = (probability_up - probability_down) * 0.01  # 1% max change
            next_price = current_price * (1 + price_change)
            
            # Obter acurácia do modelo
            model_accuracy = self.model_performance.get(symbol, {}).get('accuracy', 0.5)
            
            return ForexMLPrediction(
                symbol=symbol,
                prediction=direction,
                confidence=confidence,
                probability_up=probability_up,
                probability_down=probability_down,
                next_price=next_price,
                price_change=price_change,
                features_used=self.all_features,
                model_accuracy=model_accuracy,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer previsão para {symbol}: {str(e)}")
            return None
    
    def save_model(self, symbol: str, filepath: str):
        """Salvar modelo treinado"""
        try:
            if symbol not in self.models:
                self.logger.error(f"Modelo não encontrado para {symbol}")
                return False
            
            model_data = {
                'model': self.models[symbol],
                'scaler': self.scalers[symbol],
                'feature_importance': self.feature_importance.get(symbol),
                'performance': self.model_performance.get(symbol),
                'config': self.config
            }
            
            joblib.dump(model_data, filepath)
            self.logger.info(f"Modelo salvo para {symbol}: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar modelo para {symbol}: {str(e)}")
            return False
    
    def load_model(self, symbol: str, filepath: str) -> bool:
        """Carregar modelo treinado"""
        try:
            model_data = joblib.load(filepath)
            
            self.models[symbol] = model_data['model']
            self.scalers[symbol] = model_data['scaler']
            self.feature_importance[symbol] = model_data.get('feature_importance')
            self.model_performance[symbol] = model_data.get('performance')
            
            self.logger.info(f"Modelo carregado para {symbol}: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo para {symbol}: {str(e)}")
            return False
    
    async def train_forex_model(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Treinar modelo completo para forex"""
        try:
            self.logger.info(f"Treinando modelo ML para forex {symbol}...")
            
            # Preparar dados
            X, y, features = self.prepare_data(df, symbol)
            
            if len(X) == 0 or len(y) == 0:
                raise ValueError("Dados insuficientes para treinamento")
            
            # Treinar modelo
            performance = self.train_model(X, y, symbol)
            
            self.logger.info(f"Modelo ML treinado com sucesso para {symbol}")
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelo ML para {symbol}: {str(e)}")
            return {}
    
    def get_feature_importance(self, symbol: str) -> Optional[Dict]:
        """Obter importância das features"""
        try:
            if symbol not in self.feature_importance:
                return None
            
            importance_dict = {}
            for i, importance in enumerate(self.feature_importance[symbol]):
                if i < len(self.all_features):
                    importance_dict[self.all_features[i]] = importance
            
            # Ordenar por importância
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            self.logger.error(f"Erro ao obter importância das features: {str(e)}")
            return None
    
    def get_model_performance(self, symbol: str) -> Optional[Dict]:
        """Obter performance do modelo"""
        return self.model_performance.get(symbol)
    
    def list_trained_models(self) -> List[str]:
        """Listar modelos treinados"""
        return list(self.models.keys())