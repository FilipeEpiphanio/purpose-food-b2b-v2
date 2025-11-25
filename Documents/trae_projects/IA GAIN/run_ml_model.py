#!/usr/bin/env python3
"""
IA GAIN - ML Model Executor
Script executável para modelos de machine learning e predição
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

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
            logging.FileHandler('ml_model.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Verificar dependências necessárias"""
    required_packages = [
        'scikit-learn', 'pandas', 'numpy', 'joblib', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'scikit-learn':
                import sklearn
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Instale com: pip install scikit-learn pandas numpy joblib requests")
        return False
    
    return True

def train_model(symbol, timeframe='1h', days_back=90):
    """Treinar modelo de machine learning"""
    try:
        from ml.ml_model import MLModel
        
        print(f"🧠 Treinando modelo para {symbol}...")
        print(f"Timeframe: {timeframe}, Período: {days_back} dias")
        
        # Criar e treinar modelo
        ml_model = MLModel()
        
        # Preparar dados de treino
        print("📊 Preparando dados de treino...")
        ml_model.prepare_training_data(symbol, timeframe, days_back)
        
        # Treinar modelo
        print("🎯 Treinando modelo...")
        training_results = ml_model.train()
        
        print("\n📈 Resultados do Treinamento:")
        print("-" * 50)
        print(f"Símbolo: {symbol}")
        print(f"Período de treino: {days_back} dias")
        print(f"Acurácia: {training_results.get('accuracy', 0):.2%}")
        print(f"Precisão: {training_results.get('precision', 0):.2%}")
        print(f"Recall: {training_results.get('recall', 0):.2%}")
        print(f"F1-Score: {training_results.get('f1_score', 0):.2%}")
        
        # Salvar modelo
        model_filename = f"ml_models/{symbol.replace('/', '_')}_{timeframe}_model.pkl"
        os.makedirs('ml_models', exist_ok=True)
        
        ml_model.save_model(model_filename)
        print(f"✅ Modelo salvo em: {model_filename}")
        
        return training_results
        
    except Exception as e:
        print(f"❌ Erro no treinamento: {e}")
        raise

def make_prediction(symbol, timeframe='1h'):
    """Fazer predição com modelo treinado"""
    try:
        from ml.ml_model import MLModel
        
        print(f"🔮 Fazendo predição para {symbol}...")
        
        # Carregar modelo
        ml_model = MLModel()
        
        model_filename = f"ml_models/{symbol.replace('/', '_')}_{timeframe}_model.pkl"
        
        if not os.path.exists(model_filename):
            print(f"⚠️  Modelo não encontrado para {symbol}")
            response = input("Deseja treinar um novo modelo? (s/N): ")
            if response.lower() == 's':
                train_model(symbol, timeframe)
                return make_prediction(symbol, timeframe)
            else:
                return None
        
        ml_model.load_model(model_filename)
        
        # Fazer predição
        prediction = ml_model.predict()
        
        print("\n📊 Predição:")
        print("-" * 50)
        print(f"Símbolo: {symbol}")
        print(f"Predição: {'ALTA' if prediction['prediction'] == 1 else 'BAIXA'}")
        print(f"Confiança: {prediction['confidence']:.2%}")
        print(f"Próximo candle: {prediction.get('next_candle_time', 'N/A')}")
        
        if 'feature_importance' in prediction:
            print("\n🔍 Features mais importantes:")
            for feature, importance in prediction['feature_importance'].items():
                print(f"  {feature}: {importance:.4f}")
        
        return prediction
        
    except Exception as e:
        print(f"❌ Erro na predição: {e}")
        raise

def backtest_model(symbol, timeframe='1h', days_back=30):
    """Executar backtest do modelo"""
    try:
        from ml.ml_model import MLModel
        
        print(f"📈 Executando backtest para {symbol}...")
        print(f"Período: {days_back} dias")
        
        # Carregar modelo
        ml_model = MLModel()
        
        model_filename = f"ml_models/{symbol.replace('/', '_')}_{timeframe}_model.pkl"
        
        if not os.path.exists(model_filename):
            print(f"⚠️  Modelo não encontrado para {symbol}")
            response = input("Deseja treinar um novo modelo? (s/N): ")
            if response.lower() == 's':
                train_model(symbol, timeframe)
            else:
                return None
        
        ml_model.load_model(model_filename)
        
        # Executar backtest
        backtest_results = ml_model.backtest(days_back)
        
        print("\n📊 Resultados do Backtest:")
        print("-" * 50)
        print(f"Símbolo: {symbol}")
        print(f"Período: {days_back} dias")
        print(f"Total de predições: {backtest_results.get('total_predictions', 0)}")
        print(f"Predições corretas: {backtest_results.get('correct_predictions', 0)}")
        print(f"Taxa de acerto: {backtest_results.get('accuracy', 0):.2%}")
        print(f"Retorno total: {backtest_results.get('total_return', 0):.2f}%")
        print(f"Retorno médio por trade: {backtest_results.get('avg_return', 0):.2f}%")
        print(f"Drawdown máximo: {backtest_results.get('max_drawdown', 0):.2f}%")
        
        return backtest_results
        
    except Exception as e:
        print(f"❌ Erro no backtest: {e}")
        raise

def update_all_models():
    """Atualizar todos os modelos existentes"""
    try:
        print("🔄 Atualizando todos os modelos...")
        
        # Procurar modelos existentes
        if not os.path.exists('ml_models'):
            print("❌ Nenhum modelo encontrado")
            return
        
        import glob
        model_files = glob.glob('ml_models/*.pkl')
        
        if not model_files:
            print("❌ Nenhum modelo encontrado")
            return
        
        print(f"Encontrados {len(model_files)} modelos")
        
        results = []
        for model_file in model_files:
            try:
                # Extrair símbolo e timeframe do nome do arquivo
                basename = os.path.basename(model_file)
                parts = basename.replace('_model.pkl', '').split('_')
                symbol = f"{parts[0]}/{parts[1]}"
                timeframe = parts[2]
                
                print(f"\n🔄 Atualizando {symbol} ({timeframe})...")
                
                result = train_model(symbol, timeframe)
                results.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'accuracy': result.get('accuracy', 0)
                })
                
            except Exception as e:
                print(f"❌ Erro ao atualizar {model_file}: {e}")
                continue
        
        print("\n✅ Atualização concluída!")
        print("\nResumo das atualizações:")
        print("-" * 50)
        for result in results:
            print(f"{result['symbol']} ({result['timeframe']}): {result['accuracy']:.2%}")
        
    except Exception as e:
        print(f"❌ Erro na atualização: {e}")
        raise

def list_models():
    """Listar modelos disponíveis"""
    try:
        if not os.path.exists('ml_models'):
            print("❌ Nenhum modelo encontrado")
            return
        
        import glob
        model_files = glob.glob('ml_models/*.pkl')
        
        if not model_files:
            print("❌ Nenhum modelo encontrado")
            return
        
        print("📋 Modelos disponíveis:")
        print("-" * 50)
        
        for i, model_file in enumerate(model_files, 1):
            basename = os.path.basename(model_file)
            # Obter informações do arquivo
            file_stats = os.stat(model_file)
            file_size = file_stats.st_size / 1024  # KB
            modified_time = datetime.fromtimestamp(file_stats.st_mtime)
            
            print(f"{i}. {basename}")
            print(f"   Tamanho: {file_size:.1f} KB")
            print(f"   Modificado: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        
    except Exception as e:
        print(f"❌ Erro ao listar modelos: {e}")
        raise

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="IA GAIN - ML Model Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_ml_model.py --train BTC/USDT              # Treinar modelo para BTC
  python run_ml_model.py --predict BTC/USDT            # Fazer predição para BTC
  python run_ml_model.py --backtest BTC/USDT --days 60 # Backtest de 60 dias
  python run_ml_model.py --update-all                  # Atualizar todos os modelos
  python run_ml_model.py --list                        # Listar modelos disponíveis
  python run_ml_model.py --train BTC/USDT --timeframe 1d  # Treinar com timeframe diário
        """
    )
    
    parser.add_argument('--train',
                       help='Treinar modelo para símbolo (ex: BTC/USDT)')
    parser.add_argument('--predict',
                       help='Fazer predição para símbolo (ex: BTC/USDT)')
    parser.add_argument('--backtest',
                       help='Executar backtest para símbolo (ex: BTC/USDT)')
    parser.add_argument('--timeframe', '-t',
                       default='1h',
                       choices=['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'],
                       help='Timeframe dos dados (padrão: 1h)')
    parser.add_argument('--days', '-d',
                       type=int,
                       default=30,
                       help='Período em dias para backtest/treino (padrão: 30)')
    parser.add_argument('--update-all',
                       action='store_true',
                       help='Atualizar todos os modelos existentes')
    parser.add_argument('--list',
                       action='store_true',
                       help='Listar modelos disponíveis')
    parser.add_argument('--check',
                       action='store_true',
                       help='Verificar dependências')
    
    args = parser.parse_args()
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║              IA GAIN - ML Model Executor                     ║
║         Machine Learning para Criptomoedas                 ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar dependências
    if args.check:
        print("🔍 Verificando dependências...")
        if check_dependencies():
            print("✅ Todas as dependências estão instaladas")
        else:
            print("❌ Dependências faltando")
            sys.exit(1)
        return
    
    # Verificar dependências antes de executar
    if not check_dependencies():
        sys.exit(1)
    
    # Configurar ambiente
    setup_environment()
    
    try:
        if args.train:
            print(f"🧠 Treinando modelo para {args.train}...")
            train_model(args.train, args.timeframe, args.days)
            
        elif args.predict:
            print(f"🔮 Fazendo predição para {args.predict}...")
            make_prediction(args.predict, args.timeframe)
            
        elif args.backtest:
            print(f"📈 Executando backtest para {args.backtest}...")
            backtest_model(args.backtest, args.timeframe, args.days)
            
        elif args.update_all:
            print("🔄 Atualizando todos os modelos...")
            update_all_models()
            
        elif args.list:
            print("📋 Listando modelos disponíveis...")
            list_models()
            
        else:
            print("❌ Nenhuma ação especificada")
            print("Use --help para ver as opções disponíveis")
            sys.exit(1)
        
        print("✅ Operação concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()