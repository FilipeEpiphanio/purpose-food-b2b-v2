import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import os
from dataclasses import dataclass

@dataclass
class PredictionResult:
    """Resultado de uma previsão"""
    symbol: str
    prediction: float
    confidence: float
    direction: str  # 'buy', 'sell', 'hold'
    features: Dict[str, float]
    timestamp: datetime
    model_used: str
    
@dataclass
class ModelMetrics:
    """Métricas do modelo"""
    mse: float
    mae: float
    r2: float
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    timestamp: datetime

class MLModel:
    """
    Sistema de Machine Learning para previsão de preços de criptomoedas
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configurações do modelo
        self.model_type = config.get('model_type', 'ensemble')
        self.prediction_horizon = config.get('prediction_horizon', 24)  # horas
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        self.retrain_interval = config.get('retrain_interval', 168)  # horas
        self.use_sentiment = config.get('use_sentiment_analysis', True)
        self.use_technical = config.get('use_technical_indicators', True)
        self.use_fundamental = config.get('use_fundamental_data', True)
        
        # Modelos
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.last_training = None
        
        # Diretórios
        self.models_dir = "models"
        self.data_dir = "data"
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Inicializar modelos
        self.initialize_models()
    
    def initialize_models(self):
        """Inicializar modelos de ML"""
        try:
            # Modelos base
            self.base_models = {
                'random_forest': RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                ),
                'gradient_boost': GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=8,
                    learning_rate=0.1,
                    random_state=42
                ),
                'linear_regression': LinearRegression()
            }
            
            # Model ensemble
            self.ensemble_model = self.create_ensemble_model()
            
            self.logger.info("Modelos de ML inicializados com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar modelos: {str(e)}")
            raise
    
    def create_ensemble_model(self):
        """Criar modelo ensemble"""
        class EnsembleModel:
            def __init__(self, base_models):
                self.base_models = base_models
                self.weights = None
                
            def fit(self, X, y):
                # Treinar cada modelo
                for name, model in self.base_models.items():
                    model.fit(X, y)
                
                # Calcular pesos baseados em performance
                self.calculate_weights(X, y)
                
            def calculate_weights(self, X, y):
                """Calcular pesos baseados em performance de validação cruzada"""
                scores = {}
                for name, model in self.base_models.items():
                    scores[name] = np.mean(cross_val_score(model, X, y, cv=5, scoring='r2'))
                
                # Normalizar scores para obter pesos
                total_score = sum(scores.values())
                self.weights = {name: score/total_score for name, score in scores.items()}
                
            def predict(self, X):
                predictions = []
                for name, model in self.base_models.items():
                    pred = model.predict(X)
                    weight = self.weights[name] if self.weights else 1/len(self.base_models)
                    predictions.append(pred * weight)
                
                return np.sum(predictions, axis=0)
                
            def predict_with_confidence(self, X):
                """Prever com intervalo de confiança"""
                predictions = []
                for name, model in self.base_models.items():
                    pred = model.predict(X)
                    predictions.append(pred)
                
                predictions = np.array(predictions)
                mean_pred = np.mean(predictions, axis=0)
                std_pred = np.std(predictions, axis=0)
                confidence = 1 - (std_pred / np.abs(mean_pred))
                
                return mean_pred, np.clip(confidence, 0, 1)
        
        return EnsembleModel(self.base_models)
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preparar features para o modelo"""
        try:
            features = pd.DataFrame()
            
            # Features técnicas
            if self.use_technical:
                technical_features = self.create_technical_features(data)
                features = pd.concat([features, technical_features], axis=1)
            
            # Features fundamentais
            if self.use_fundamental:
                fundamental_features = self.create_fundamental_features(data)
                features = pd.concat([features, fundamental_features], axis=1)
            
            # Features de sentimento
            if self.use_sentiment:
                sentiment_features = self.create_sentiment_features(data)
                features = pd.concat([features, sentiment_features], axis=1)
            
            # Features temporais
            temporal_features = self.create_temporal_features(data)
            features = pd.concat([features, temporal_features], axis=1)
            
            # Remover valores NaN
            features = features.fillna(method='ffill').fillna(0)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Erro ao preparar features: {str(e)}")
            raise
    
    def create_technical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Criar features técnicas"""
        features = pd.DataFrame(index=data.index)
        
        # Preço e volume
        features['price'] = data['close']
        features['volume'] = data['volume']
        features['price_change'] = data['close'].pct_change()
        features['volume_change'] = data['volume'].pct_change()
        
        # Médias móveis
        for period in [5, 10, 20, 50]:
            features[f'ma_{period}'] = data['close'].rolling(period).mean()
            features[f'ma_ratio_{period}'] = data['close'] / features[f'ma_{period}']
        
        # RSI
        features['rsi'] = self.calculate_rsi(data['close'])
        
        # MACD
        ema_fast = data['close'].ewm(span=12).mean()
        ema_slow = data['close'].ewm(span=26).mean()
        features['macd'] = ema_fast - ema_slow
        features['macd_signal'] = features['macd'].ewm(span=9).mean()
        features['macd_histogram'] = features['macd'] - features['macd_signal']
        
        # Bollinger Bands
        bb_middle = data['close'].rolling(20).mean()
        bb_std = data['close'].rolling(20).std()
        features['bb_upper'] = bb_middle + (bb_std * 2)
        features['bb_lower'] = bb_middle - (bb_std * 2)
        features['bb_position'] = (data['close'] - bb_middle) / (2 * bb_std)
        
        # Volatilidade
        features['volatility_10'] = data['close'].pct_change().rolling(10).std()
        features['volatility_30'] = data['close'].pct_change().rolling(30).std()
        
        # Indicadores adicionais
        features['momentum_10'] = data['close'] / data['close'].shift(10) - 1
        features['momentum_30'] = data['close'] / data['close'].shift(30) - 1
        
        return features
    
    def create_fundamental_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Criar features fundamentais"""
        features = pd.DataFrame(index=data.index)
        
        # Se houver dados fundamentais disponíveis
        if 'market_cap' in data.columns:
            features['market_cap'] = data['market_cap']
            features['market_cap_change'] = data['market_cap'].pct_change()
        
        if 'volume_24h' in data.columns:
            features['volume_24h'] = data['volume_24h']
            features['volume_market_cap_ratio'] = data['volume_24h'] / data['market_cap']
        
        # Adicionar features padrão se não houver fundamentais
        if features.empty:
            features['dummy_fundamental'] = 0
        
        return features
    
    def create_sentiment_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Criar features de sentimento"""
        features = pd.DataFrame(index=data.index)
        
        # Se houver dados de sentimento disponíveis
        if 'sentiment_score' in data.columns:
            features['sentiment_score'] = data['sentiment_score']
            features['sentiment_change'] = data['sentiment_score'].pct_change()
        else:
            # Features de sentimento sintéticas baseadas em movimentos de preço
            features['price_sentiment'] = np.where(data['close'].pct_change() > 0, 1, -1)
            features['sentiment_ma_5'] = features['price_sentiment'].rolling(5).mean()
            features['sentiment_ma_10'] = features['price_sentiment'].rolling(10).mean()
        
        return features
    
    def create_temporal_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Criar features temporais"""
        features = pd.DataFrame(index=data.index)
        
        # Converter índice para datetime se necessário
        if not isinstance(data.index, pd.DatetimeIndex):
            index = pd.to_datetime(data.index)
        else:
            index = data.index
        
        # Features temporais
        features['hour'] = index.hour
        features['day_of_week'] = index.dayofweek
        features['day_of_month'] = index.day
        features['month'] = index.month
        
        # Ciclos temporais
        features['hour_sin'] = np.sin(2 * np.pi * features['hour'] / 24)
        features['hour_cos'] = np.cos(2 * np.pi * features['hour'] / 24)
        features['dow_sin'] = np.sin(2 * np.pi * features['day_of_week'] / 7)
        features['dow_cos'] = np.cos(2 * np.pi * features['day_of_week'] / 7)
        
        return features
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcular RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def create_target_variable(self, data: pd.DataFrame) -> pd.Series:
        """Criar variável alvo (preço futuro)"""
        # Prever o preço de fechamento em 'prediction_horizon' horas
        future_price = data['close'].shift(-self.prediction_horizon)
        
        # Retorno futuro
        target = (future_price - data['close']) / data['close']
        
        return target
    
    def train_model(self, data: pd.DataFrame, symbol: str) -> ModelMetrics:
        """Treinar modelo para um símbolo específico"""
        try:
            self.logger.info(f"Treinando modelo para {symbol}")
            
            # Preparar features e target
            features = self.prepare_features(data)
            target = self.create_target_variable(data)
            
            # Remover valores NaN
            valid_idx = ~(features.isnull().any(axis=1) | target.isnull())
            features = features[valid_idx]
            target = target[valid_idx]
            
            if len(features) < 100:
                raise ValueError(f"Dados insuficientes para treinar modelo para {symbol}")
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                features, target, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Escalar features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Treinar modelo ensemble
            self.ensemble_model.fit(X_train_scaled, y_train)
            
            # Fazer previsões
            y_pred, confidence = self.ensemble_model.predict_with_confidence(X_test_scaled)
            
            # Calcular métricas
            metrics = self.calculate_metrics(y_test, y_pred)
            
            # Salvar modelo e scaler
            self.save_model(symbol, self.ensemble_model, scaler, features.columns.tolist())
            
            # Atualizar último treinamento
            self.last_training = datetime.now()
            
            self.logger.info(f"Modelo treinado com sucesso para {symbol}. R²: {metrics.r2:.4f}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelo para {symbol}: {str(e)}")
            raise
    
    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> ModelMetrics:
        """Calcular métricas do modelo"""
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        # Métricas de classificação (direção da previsão)
        y_true_direction = np.sign(y_true)
        y_pred_direction = np.sign(y_pred)
        accuracy = np.mean(y_true_direction == y_pred_direction)
        
        # Calcular precision, recall e f1 (considerando positivos como trades de compra)
        true_positive = np.sum((y_true_direction == 1) & (y_pred_direction == 1))
        false_positive = np.sum((y_true_direction != 1) & (y_pred_direction == 1))
        false_negative = np.sum((y_true_direction == 1) & (y_pred_direction != 1))
        
        precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
        recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return ModelMetrics(
            mse=mse, mae=mae, r2=r2, accuracy=accuracy,
            precision=precision, recall=recall, f1_score=f1,
            timestamp=datetime.now()
        )
    
    def predict(self, data: pd.DataFrame, symbol: str) -> PredictionResult:
        """Fazer previsão para um símbolo"""
        try:
            # Carregar modelo se necessário
            if symbol not in self.models:
                self.load_model(symbol)
            
            # Preparar features
            features = self.prepare_features(data.tail(100))  # Últimos 100 pontos
            latest_features = features.iloc[-1:].values
            
            # Escalar features
            scaler = self.scalers[symbol]
            latest_features_scaled = scaler.transform(latest_features)
            
            # Fazer previsão
            model = self.models[symbol]
            prediction, confidence = model.predict_with_confidence(latest_features_scaled)
            
            pred_value = prediction[0]
            conf_value = confidence[0]
            
            # Determinar direção
            if conf_value >= self.confidence_threshold:
                direction = 'buy' if pred_value > 0 else 'sell' if pred_value < -0.001 else 'hold'
            else:
                direction = 'hold'
            
            # Criar resultado
            result = PredictionResult(
                symbol=symbol,
                prediction=pred_value,
                confidence=conf_value,
                direction=direction,
                features=dict(zip(features.columns, latest_features[0])),
                timestamp=datetime.now(),
                model_used=self.model_type
            )
            
            self.logger.info(f"Previsão para {symbol}: {direction} (confiança: {conf_value:.2f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer previsão para {symbol}: {str(e)}")
            # Retornar previsão neutra em caso de erro
            return PredictionResult(
                symbol=symbol,
                prediction=0.0,
                confidence=0.0,
                direction='hold',
                features={},
                timestamp=datetime.now(),
                model_used=self.model_type
            )
    
    def save_model(self, symbol: str, model, scaler, feature_names: List[str]):
        """Salvar modelo treinado"""
        try:
            model_data = {
                'model': model,
                'scaler': scaler,
                'feature_names': feature_names,
                'timestamp': datetime.now(),
                'config': self.config
            }
            
            model_path = os.path.join(self.models_dir, f"{symbol}_model.pkl")
            joblib.dump(model_data, model_path)
            
            self.models[symbol] = model
            self.scalers[symbol] = scaler
            
            self.logger.info(f"Modelo salvo para {symbol}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar modelo para {symbol}: {str(e)}")
            raise
    
    def load_model(self, symbol: str):
        """Carregar modelo treinado"""
        try:
            model_path = os.path.join(self.models_dir, f"{symbol}_model.pkl")
            
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                self.models[symbol] = model_data['model']
                self.scalers[symbol] = model_data['scaler']
                self.logger.info(f"Modelo carregado para {symbol}")
            else:
                self.logger.warning(f"Modelo não encontrado para {symbol}")
                raise FileNotFoundError(f"Modelo não encontrado para {symbol}")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelo para {symbol}: {str(e)}")
            raise
    
    def should_retrain(self, symbol: str) -> bool:
        """Verificar se o modelo precisa ser retreinado"""
        if self.last_training is None:
            return True
        
        time_since_training = datetime.now() - self.last_training
        return time_since_training.total_seconds() / 3600 >= self.retrain_interval
    
    def get_feature_importance(self, symbol: str) -> Dict[str, float]:
        """Obter importância das features para um símbolo"""
        try:
            if symbol not in self.models:
                self.load_model(symbol)
            
            model = self.models[symbol]
            
            # Para ensemble, obter importância média
            importance = {}
            if hasattr(model, 'base_models'):
                for name, base_model in model.base_models.items():
                    if hasattr(base_model, 'feature_importances_'):
                        importance[name] = base_model.feature_importances_
            
            return importance
            
        except Exception as e:
            self.logger.error(f"Erro ao obter importância das features: {str(e)}")
            return {}
    
    def backtest(self, data: pd.DataFrame, symbol: str, initial_capital: float = 1000) -> Dict:
        """Realizar backtest do modelo"""
        try:
            self.logger.info(f"Iniciando backtest para {symbol}")
            
            # Preparar dados
            features = self.prepare_features(data)
            target = self.create_target_variable(data)
            
            # Remover valores NaN
            valid_idx = ~(features.isnull().any(axis=1) | target.isnull())
            features = features[valid_idx]
            target = target[valid_idx]
            
            # Dividir em período de treino e teste
            train_size = int(len(features) * 0.7)
            X_train = features.iloc[:train_size]
            X_test = features.iloc[train_size:]
            y_train = target.iloc[:train_size]
            y_test = target.iloc[train_size:]
            
            # Treinar modelo
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            self.ensemble_model.fit(X_train_scaled, y_train)
            
            # Fazer previsões
            y_pred, confidence = self.ensemble_model.predict_with_confidence(X_test_scaled)
            
            # Simular trades
            capital = initial_capital
            position = 0
            trades = []
            portfolio_value = []
            
            for i in range(len(y_test)):
                current_price = data['close'].iloc[train_size + i]
                pred_return = y_pred[i]
                conf = confidence[i]
                
                # Sinal de trade
                if conf >= self.confidence_threshold:
                    if pred_return > 0.01 and position <= 0:  # Sinal de compra
                        # Comprar com 90% do capital disponível
                        buy_amount = (capital * 0.9) / current_price
                        position += buy_amount
                        capital -= buy_amount * current_price
                        
                        trades.append({
                            'type': 'buy',
                            'price': current_price,
                            'amount': buy_amount,
                            'confidence': conf,
                            'timestamp': data.index[train_size + i]
                        })
                        
                    elif pred_return < -0.01 and position > 0:  # Sinal de venda
                        # Vender toda a posição
                        capital += position * current_price
                        
                        trades.append({
                            'type': 'sell',
                            'price': current_price,
                            'amount': position,
                            'confidence': conf,
                            'timestamp': data.index[train_size + i]
                        })
                        
                        position = 0
                
                # Valor do portfólio
                current_value = capital + (position * current_price)
                portfolio_value.append(current_value)
            
            # Calcular métricas de backtest
            total_return = (portfolio_value[-1] - initial_capital) / initial_capital
            max_drawdown = self.calculate_max_drawdown(portfolio_value)
            sharpe_ratio = self.calculate_sharpe_ratio(portfolio_value)
            
            results = {
                'symbol': symbol,
                'initial_capital': initial_capital,
                'final_capital': portfolio_value[-1],
                'total_return': total_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'num_trades': len(trades),
                'win_rate': self.calculate_win_rate(trades, data.iloc[train_size:]),
                'trades': trades,
                'portfolio_value': portfolio_value,
                'predictions': y_pred,
                'actual_returns': y_test.values,
                'confidence': confidence
            }
            
            self.logger.info(f"Backtest concluído para {symbol}. Retorno total: {total_return:.2%}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro no backtest para {symbol}: {str(e)}")
            raise
    
    def calculate_max_drawdown(self, portfolio_values: List[float]) -> float:
        """Calcular máximo drawdown"""
        peak = portfolio_values[0]
        max_dd = 0
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def calculate_sharpe_ratio(self, portfolio_values: List[float], risk_free_rate: float = 0.02) -> float:
        """Calcular Sharpe Ratio"""
        returns = [(portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1] 
                   for i in range(1, len(portfolio_values))]
        
        if not returns:
            return 0
        
        excess_returns = [r - risk_free_rate/252 for r in returns]  # 252 dias úteis por ano
        
        if np.std(excess_returns) == 0:
            return 0
        
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    
    def calculate_win_rate(self, trades: List[Dict], price_data: pd.DataFrame) -> float:
        """Calcular taxa de acerto"""
        if not trades:
            return 0
        
        wins = 0
        for i, trade in enumerate(trades):
            if trade['type'] == 'buy':
                # Procurar próxima venda
                for j in range(i+1, len(trades)):
                    if trades[j]['type'] == 'sell':
                        if trades[j]['price'] > trade['price']:
                            wins += 1
                        break
        
        buy_trades = [t for t in trades if t['type'] == 'buy']
        return wins / len(buy_trades) if buy_trades else 0
    
    def get_model_summary(self) -> Dict:
        """Obter resumo do modelo"""
        return {
            'model_type': self.model_type,
            'prediction_horizon': self.prediction_horizon,
            'confidence_threshold': self.confidence_threshold,
            'retrain_interval': self.retrain_interval,
            'use_sentiment': self.use_sentiment,
            'use_technical': self.use_technical,
            'use_fundamental': self.use_fundamental,
            'last_training': self.last_training.isoformat() if self.last_training else None,
            'num_models_trained': len(self.models)
        }