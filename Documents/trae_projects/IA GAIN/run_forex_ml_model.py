#!/usr/bin/env python3
"""
IA GAIN - Forex ML Model Runner
Executa modelos de machine learning para análise forex
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

# Adicionar diretório src ao path
sys.path.append(str(Path(__file__).parent / 'src'))

from utils.config_manager import ConfigManager
from utils.logger import setup_logger
from utils.data_manager import DataManager
from ml.forex_ml_model import ForexMLModel
from forex.forex_data import ForexDataCollector
from utils.notification_manager import NotificationManager

class ForexMLRunner:
    """Executor de modelos ML para forex"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = ConfigManager(config_path)
        self.logger = setup_logger(
            "forex_ml_runner",
            self.config.get('logging.level', 'INFO'),
            self.config.get('logging.file')
        )
        self.data_manager = DataManager(self.config)
        self.data_collector = ForexDataCollector(self.config)
        self.ml_model = ForexMLModel(self.config.get('ml', {}))
        self.notification = NotificationManager(self.config)
        
        self.logger.info("Forex ML Runner inicializado")
    
    async def train_models(self, symbols: List[str] = None) -> Dict:
        """Treinar modelos para símbolos forex"""
        try:
            if not symbols:
                symbols = self.config.get('forex.default_pairs', ['EUR/USD', 'GBP/USD', 'USD/JPY'])
            
            self.logger.info(f"Treinando modelos para: {symbols}")
            
            results = {}
            
            for symbol in symbols:
                try:
                    self.logger.info(f"Processando {symbol}...")
                    
                    # Coletar dados históricos
                    days_back = self.config.get('ml.training_days', 365)
                    start_date = datetime.now() - timedelta(days=days_back)
                    
                    df = await self.data_collector.get_historical_data(
                        symbol=symbol,
                        timeframe=self.config.get('forex.timeframe', '1h'),
                        start_date=start_date
                    )
                    
                    if df is None or len(df) < 100:
                        self.logger.warning(f"Dados insuficientes para {symbol}")
                        continue
                    
                    # Treinar modelo
                    performance = await self.ml_model.train_forex_model(df, symbol)
                    
                    if performance:
                        results[symbol] = performance
                        
                        # Salvar modelo
                        model_path = f"models/forex_{symbol.replace('/', '_')}.pkl"
                        self.ml_model.save_model(symbol, model_path)
                        
                        self.logger.info(f"Modelo treinado para {symbol}: {performance}")
                        
                        # Notificação
                        await self.notification.send_notification(
                            f"🤖 Modelo ML treinado para {symbol}",
                            f"Acurácia: {performance.get('accuracy', 0):.3f}"
                        )
                    
                except Exception as e:
                    self.logger.error(f"Erro ao treinar modelo para {symbol}: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelos: {str(e)}")
            return {}
    
    async def make_predictions(self, symbols: List[str] = None) -> Dict:
        """Fazer previsões com modelos treinados"""
        try:
            if not symbols:
                symbols = self.config.get('forex.default_pairs', ['EUR/USD', 'GBP/USD', 'USD/JPY'])
            
            self.logger.info(f"Fazendo previsões para: {symbols}")
            
            predictions = {}
            
            for symbol in symbols:
                try:
                    # Carregar modelo se existir
                    model_path = f"models/forex_{symbol.replace('/', '_')}.pkl"
                    if not self.ml_model.load_model(symbol, model_path):
                        self.logger.warning(f"Modelo não encontrado para {symbol}")
                        continue
                    
                    # Obter dados recentes
                    df = await self.data_collector.get_historical_data(
                        symbol=symbol,
                        timeframe=self.config.get('forex.timeframe', '1h'),
                        limit=self.ml_model.lookback_period + 10
                    )
                    
                    if df is None or len(df) < self.ml_model.lookback_period:
                        self.logger.warning(f"Dados insuficientes para previsão de {symbol}")
                        continue
                    
                    # Preparar features
                    df_features = self.ml_model.calculate_forex_features(df, symbol)
                    df_lagged = self.ml_model.create_lagged_features(df_features)
                    
                    # Pegar últimos dados
                    feature_columns = [col for col in df_lagged.columns 
                                     if col not in ['close', 'future_price', 'price_change', 'price_category']]
                    
                    latest_data = df_lagged[feature_columns].iloc[-1].values
                    
                    # Fazer previsão
                    prediction = self.ml_model.predict(latest_data, symbol)
                    
                    if prediction:
                        predictions[symbol] = prediction
                        
                        self.logger.info(f"Previsão para {symbol}: {prediction.prediction} "
                                         f"({prediction.confidence:.2f})")
                        
                except Exception as e:
                    self.logger.error(f"Erro ao fazer previsão para {symbol}: {str(e)}")
                    continue
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Erro ao fazer previsões: {str(e)}")
            return {}
    
    async def analyze_forex_opportunities(self) -> Dict:
        """Analisar oportunidades forex com ML"""
        try:
            self.logger.info("Analisando oportunidades forex...")
            
            # Obter previsões
            predictions = await self.make_predictions()
            
            opportunities = []
            
            for symbol, prediction in predictions.items():
                try:
                    # Obter cotação atual
                    current_quote = await self.data_collector.get_live_quote(symbol)
                    
                    if current_quote:
                        opportunity = {
                            'symbol': symbol,
                            'current_price': current_quote['price'],
                            'prediction': prediction.prediction,
                            'confidence': prediction.confidence,
                            'probability_up': prediction.probability_up,
                            'probability_down': prediction.probability_down,
                            'next_price': prediction.next_price,
                            'price_change': prediction.price_change,
                            'model_accuracy': prediction.model_accuracy,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Filtrar por confiança mínima
                        min_confidence = self.config.get('ml.min_confidence', 0.6)
                        if prediction.confidence >= min_confidence:
                            opportunities.append(opportunity)
                            
                            self.logger.info(f"Oportunidade encontrada: {symbol} - "
                                             f"{prediction.prediction} ({prediction.confidence:.2f})")
                            
                            # Notificação para oportunidades de alta confiança
                            if prediction.confidence >= 0.8:
                                await self.notification.send_notification(
                                    f"🎯 Oportunidade Forex: {symbol}",
                                    f"Previsão: {prediction.prediction}\n"
                                    f"Confiança: {prediction.confidence:.2f}\n"
                                    f"Preço atual: {current_quote['price']:.4f}"
                                )
                
                except Exception as e:
                    self.logger.error(f"Erro ao analisar {symbol}: {str(e)}")
                    continue
            
            # Ordenar por confiança
            opportunities.sort(key=lambda x: x['confidence'], reverse=True)
            
            return {
                'opportunities': opportunities,
                'total': len(opportunities),
                'high_confidence': len([o for o in opportunities if o['confidence'] >= 0.8]),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar oportunidades: {str(e)}")
            return {}
    
    async def run_forex_analysis(self, symbols: List[str] = None) -> Dict:
        """Executar análise completa de forex"""
        try:
            self.logger.info("Executando análise forex completa...")
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'symbols': symbols or self.config.get('forex.default_pairs', ['EUR/USD', 'GBP/USD', 'USD/JPY']),
                'predictions': {},
                'opportunities': {},
                'model_performance': {},
                'feature_importance': {}
            }
            
            # Fazer previsões
            predictions = await self.make_predictions(symbols)
            results['predictions'] = {k: v.to_dict() for k, v in predictions.items()}
            
            # Analisar oportunidades
            opportunities = await self.analyze_forex_opportunities()
            results['opportunities'] = opportunities
            
            # Performance dos modelos
            for symbol in self.ml_model.list_trained_models():
                performance = self.ml_model.get_model_performance(symbol)
                if performance:
                    results['model_performance'][symbol] = performance
                
                feature_importance = self.ml_model.get_feature_importance(symbol)
                if feature_importance:
                    results['feature_importance'][symbol] = dict(list(feature_importance.items())[:10])
            
            # Salvar resultados
            output_file = f"logs/forex_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Análise forex completa salva em: {output_file}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na análise forex: {str(e)}")
            return {}
    
    async def run_continuous_analysis(self, interval_minutes: int = 60):
        """Executar análise contínua"""
        try:
            self.logger.info(f"Iniciando análise contínua (intervalo: {interval_minutes} minutos)")
            
            while True:
                try:
                    await self.run_forex_analysis()
                    
                    self.logger.info(f"Próxima análise em {interval_minutes} minutos")
                    await asyncio.sleep(interval_minutes * 60)
                    
                except KeyboardInterrupt:
                    self.logger.info("Análise contínua interrompida pelo usuário")
                    break
                except Exception as e:
                    self.logger.error(f"Erro na análise contínua: {str(e)}")
                    await asyncio.sleep(60)  # Esperar 1 minuto antes de tentar novamente
                    
        except Exception as e:
            self.logger.error(f"Erro ao executar análise contínua: {str(e)}")

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='IA GAIN - Forex ML Model Runner')
    parser.add_argument('--train', action='store_true', help='Treinar modelos')
    parser.add_argument('--predict', action='store_true', help='Fazer previsões')
    parser.add_argument('--analyze', action='store_true', help='Analisar oportunidades')
    parser.add_argument('--continuous', type=int, help='Executar análise contínua (minutos)')
    parser.add_argument('--symbols', nargs='+', help='Símbolos forex (ex: EUR/USD GBP/USD)')
    parser.add_argument('--config', default='config.json', help='Arquivo de configuração')
    
    args = parser.parse_args()
    
    # Criar diretórios necessários
    Path("models").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Inicializar runner
    runner = ForexMLRunner(args.config)
    
    try:
        if args.train:
            results = await runner.train_models(args.symbols)
            print(f"Modelos treinados: {len(results)}")
            
        elif args.predict:
            predictions = await runner.make_predictions(args.symbols)
            print(f"Previsões feitas: {len(predictions)}")
            for symbol, pred in predictions.items():
                print(f"{symbol}: {pred.prediction} ({pred.confidence:.2f})")
                
        elif args.analyze:
            opportunities = await runner.analyze_forex_opportunities()
            print(f"Oportunidades encontradas: {opportunities.get('total', 0)}")
            
        elif args.continuous:
            await runner.run_continuous_analysis(args.continuous)
            
        else:
            # Executar análise completa por padrão
            results = await runner.run_forex_analysis(args.symbols)
            print(f"Análise completa executada. Previsões: {len(results.get('predictions', {}))}")
            
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário")
    except Exception as e:
        print(f"Erro: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())