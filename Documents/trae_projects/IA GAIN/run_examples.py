#!/usr/bin/env python3
"""
IA GAIN - Examples and Backtesting
Executar exemplos e backtests do sistema
"""

import asyncio
import sys
import os
from pathlib import Path
import argparse
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    import ccxt
    import pandas as pd
    import numpy as np
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Erro ao importar dependências: {e}")
    print("Instale com: pip install ccxt pandas numpy python-dotenv")
    sys.exit(1)

from utils.config_manager import ConfigManager
from utils.logger import setup_logger
from data.data_collector import DataCollector
from ml.ml_model import MLModel


class ExamplesRunner:
    """Executor de exemplos e backtests para IA GAIN"""
    
    def __init__(self, config_path: str = None):
        self.config = ConfigManager(config_path)
        self.logger = setup_logger('ExamplesRunner')
        self.data_collector = None
        self.results = []
        
    def setup_environment(self):
        """Configurar ambiente e variáveis"""
        load_dotenv()
        
        # Criar diretórios necessários
        directories = [
            'logs',
            'data',
            'backtests',
            'exports',
            'examples_results'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            
    def check_dependencies(self) -> bool:
        """Verificar dependências necessárias"""
        required_packages = [
            'ccxt', 'pandas', 'numpy', 'python-dotenv', 'requests', 'scikit-learn'
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
            print("Instale com: pip install ccxt pandas numpy python-dotenv requests scikit-learn")
            return False
        
        return True
        
    def check_config(self) -> bool:
        """Verificar configuração necessária"""
        try:
            config = self.config.get_config()
            
            # Verificar seções básicas
            required_sections = ['trading', 'api']
            for section in required_sections:
                if section not in config:
                    print(f"❌ Seção '{section}' não encontrada na configuração")
                    return False
                    
            print("✅ Configuração verificada com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao verificar configuração: {e}")
            return False
            
    async def initialize_data_collector(self):
        """Inicializar coletor de dados"""
        try:
            self.data_collector = DataCollector(self.config.get_config())
            await self.data_collector.initialize()
            self.logger.info("Coletor de dados inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar coletor de dados: {e}")
            raise
            
    async def run_basic_example(self):
        """Executar exemplo básico de trading"""
        print("\n📈 Exemplo Básico de Trading")
        print("=" * 50)
        
        try:
            # Coletar dados de exemplo
            symbol = "BTC/USDT"
            timeframe = "1h"
            days = 7
            
            print(f"Coletando dados para {symbol}...")
            data = await self.data_collector.collect_data(symbol, timeframe, days)
            
            if data is None or data.empty:
                print("❌ Não foi possível coletar dados")
                return None
                
            print(f"✅ Dados coletados: {len(data)} registros")
            
            # Análise básica
            print(f"\n📊 Análise Básica:")
            print(f"   Preço médio: ${data['close'].mean():.2f}")
            print(f"   Preço máximo: ${data['high'].max():.2f}")
            print(f"   Preço mínimo: ${data['low'].min():.2f}")
            print(f"   Volatilidade: {data['close'].std():.2f}")
            
            # Sinal simples de média móvel
            data['sma_20'] = data['close'].rolling(window=20).mean()
            data['sma_50'] = data['close'].rolling(window=50).mean()
            
            if len(data) > 50:
                current_price = data['close'].iloc[-1]
                sma20 = data['sma_20'].iloc[-1]
                sma50 = data['sma_50'].iloc[-1]
                
                print(f"\n💡 Sinal de Média Móvel:")
                print(f"   Preço atual: ${current_price:.2f}")
                print(f"   SMA 20: ${sma20:.2f}")
                print(f"   SMA 50: ${sma50:.2f}")
                
                if current_price > sma20 > sma50:
                    signal = "COMPRA"
                    strength = "Forte"
                elif current_price < sma20 < sma50:
                    signal = "VENDA"
                    strength = "Forte"
                elif current_price > sma20:
                    signal = "COMPRA"
                    strength = "Fraca"
                else:
                    signal = "VENDA"
                    strength = "Fraca"
                    
                print(f"   🔔 Sinal: {signal} ({strength})")
            
            # Salvar resultados
            result = {
                'example': 'basic_trading',
                'symbol': symbol,
                'timeframe': timeframe,
                'period_days': days,
                'data_points': len(data),
                'analysis': {
                    'mean_price': float(data['close'].mean()),
                    'max_price': float(data['high'].max()),
                    'min_price': float(data['low'].min()),
                    'volatility': float(data['close'].std())
                },
                'signal': signal if len(data) > 50 else 'N/A',
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no exemplo básico: {e}")
            return None
            
    async def run_ml_backtest_example(self):
        """Executar exemplo de backtest com ML"""
        print("\n🤖 Exemplo de Backtest com Machine Learning")
        print("=" * 50)
        
        try:
            symbol = "BTC/USDT"
            timeframe = "1h"
            days = 30
            
            print(f"Preparando backtest ML para {symbol}...")
            
            # Coletar dados
            data = await self.data_collector.collect_data(symbol, timeframe, days)
            if data is None or data.empty:
                print("❌ Não foi possível coletar dados")
                return None
                
            print(f"✅ Dados coletados: {len(data)} registros")
            
            # Criar e treinar modelo simples
            ml_model = MLModel()
            
            # Preparar features
            features = ml_model.prepare_features(data)
            target = ml_model.create_target_variable(data)
            
            # Remover valores NaN
            valid_idx = ~(features.isnull().any(axis=1) | target.isnull())
            features = features[valid_idx]
            target = target[valid_idx]
            
            if len(features) < 100:
                print("❌ Dados insuficientes para treinamento")
                return None
                
            # Dividir dados
            train_size = int(len(features) * 0.7)
            X_train = features.iloc[:train_size]
            X_test = features.iloc[train_size:]
            y_train = target.iloc[:train_size]
            y_test = target.iloc[train_size:]
            
            print(f"Treinando modelo com {len(X_train)} amostras...")
            
            # Treinar modelo simples
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import StandardScaler
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Fazer predições
            y_pred = model.predict(X_test_scaled)
            accuracy = (y_pred == y_test).mean()
            
            print(f"✅ Modelo treinado - Acurácia: {accuracy:.2%}")
            
            # Simular trades baseados em predições
            initial_capital = 10000
            capital = initial_capital
            position = 0
            trades = []
            portfolio_values = [capital]
            
            test_data = data.iloc[train_size:].copy()
            test_prices = test_data['close'].values
            
            for i in range(1, len(y_pred)):
                current_price = test_prices[i]
                
                if y_pred[i] == 1 and position == 0:  # Sinal de compra
                    position = capital / current_price
                    capital = 0
                    trades.append({
                        'type': 'buy',
                        'price': current_price,
                        'position': position,
                        'timestamp': i
                    })
                    
                elif y_pred[i] == 0 and position > 0:  # Sinal de venda
                    capital = position * current_price
                    position = 0
                    trades.append({
                        'type': 'sell',
                        'price': current_price,
                        'capital': capital,
                        'timestamp': i
                    })
                    
                # Valor do portfólio
                current_value = capital + (position * current_price if position > 0 else 0)
                portfolio_values.append(current_value)
            
            # Resultados finais
            final_value = portfolio_values[-1]
            total_return = (final_value - initial_capital) / initial_capital
            
            print(f"\n📊 Resultados do Backtest:")
            print(f"   Capital inicial: ${initial_capital:,.2f}")
            print(f"   Capital final: ${final_value:,.2f}")
            print(f"   Retorno total: {total_return:.2%}")
            print(f"   Total de trades: {len(trades)}")
            print(f"   Acurácia do modelo: {accuracy:.2%}")
            
            # Calcular drawdown máximo
            peak = max(portfolio_values)
            trough = min(portfolio_values[portfolio_values.index(peak):])
            max_drawdown = (peak - trough) / peak if peak > 0 else 0
            
            print(f"   Drawdown máximo: {max_drawdown:.2%}")
            
            result = {
                'example': 'ml_backtest',
                'symbol': symbol,
                'timeframe': timeframe,
                'period_days': days,
                'model_accuracy': accuracy,
                'initial_capital': initial_capital,
                'final_capital': final_value,
                'total_return': total_return,
                'total_trades': len(trades),
                'max_drawdown': max_drawdown,
                'trades': trades,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no backtest ML: {e}")
            return None
            
    async def run_forex_example(self):
        """Executar exemplo de Forex"""
        print("\n💱 Exemplo de Trading Forex")
        print("=" * 50)
        
        try:
            # Pares forex principais
            forex_pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD"]
            timeframe = "1h"
            days = 7
            
            print(f"Analisando pares forex: {', '.join(forex_pairs)}")
            
            results = []
            for pair in forex_pairs:
                try:
                    print(f"\n📊 Analisando {pair}...")
                    data = await self.data_collector.collect_data(pair, timeframe, days)
                    
                    if data is None or data.empty:
                        print(f"⚠️  Dados não disponíveis para {pair}")
                        continue
                        
                    # Análise básica
                    current_price = data['close'].iloc[-1]
                    price_change = (data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]
                    volatility = data['close'].std()
                    
                    # Sinal simples baseado em médias móveis
                    if len(data) >= 20:
                        sma20 = data['close'].rolling(20).mean().iloc[-1]
                        signal = "COMPRA" if current_price > sma20 else "VENDA"
                    else:
                        signal = "NEUTRO"
                    
                    pair_result = {
                        'pair': pair,
                        'current_price': current_price,
                        'price_change_pct': price_change * 100,
                        'volatility': volatility,
                        'signal': signal,
                        'data_points': len(data)
                    }
                    
                    results.append(pair_result)
                    
                    print(f"   Preço atual: {current_price:.5f}")
                    print(f"   Variação: {price_change:.2%}")
                    print(f"   Sinal: {signal}")
                    
                except Exception as e:
                    print(f"⚠️  Erro ao analisar {pair}: {e}")
                    continue
            
            # Resumo geral
            if results:
                print(f"\n📈 Resumo Forex:")
                buy_signals = [r for r in results if r['signal'] == 'COMPRA']
                sell_signals = [r for r in results if r['signal'] == 'VENDA']
                
                print(f"   Total de pares analisados: {len(results)}")
                print(f"   Sinais de COMPRA: {len(buy_signals)}")
                print(f"   Sinais de VENDA: {len(sell_signals)}")
                print(f"   Melhor desempenho: {max(results, key=lambda x: x['price_change_pct'])['pair']}")
                
            result = {
                'example': 'forex_analysis',
                'pairs_analyzed': len(results),
                'buy_signals': len(buy_signals),
                'sell_signals': len(sell_signals),
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no exemplo forex: {e}")
            return None
            
    async def run_risk_management_example(self):
        """Executar exemplo de gerenciamento de risco"""
        print("\n🛡️  Exemplo de Gerenciamento de Risco")
        print("=" * 50)
        
        try:
            # Exemplo de cálculo de posição baseada em risco
            account_balance = 10000  # Saldo da conta
            risk_per_trade = 0.02  # 2% de risco por trade
            stop_loss_pips = 50  # Stop loss em pips para forex
            
            # Cálculo do tamanho da posição
            risk_amount = account_balance * risk_per_trade  # $200
            
            print(f"Saldo da conta: ${account_balance:,.2f}")
            print(f"Risco por trade: {risk_per_trade:.1%}")
            print(f"Valor do risco: ${risk_amount:,.2f}")
            print(f"Stop loss: {stop_loss_pips} pips")
            
            # Para diferentes pares forex (exemplo de cálculo)
            forex_pairs = {
                'EUR/USD': {'pip_value': 10},  # $10 por pip para 1 lote
                'GBP/USD': {'pip_value': 10},
                'USD/JPY': {'pip_value': 8.5},  # Aproximado
            }
            
            calculations = []
            for pair, info in forex_pairs.items():
                pip_value = info['pip_value']
                lot_size = risk_amount / (stop_loss_pips * pip_value)
                
                print(f"\n📊 {pair}:")
                print(f"   Valor do pip: ${pip_value}")
                print(f"   Tamanho do lote: {lot_size:.2f}")
                print(f"   Risco em dinheiro: ${lot_size * stop_loss_pips * pip_value:,.2f}")
                
                calculations.append({
                    'pair': pair,
                    'lot_size': lot_size,
                    'risk_amount': lot_size * stop_loss_pips * pip_value
                })
            
            # Exemplo de gestão de risco com múltiplas posições
            max_positions = 5
            total_risk = risk_per_trade * max_positions
            
            print(f"\n📋 Gestão de Risco Completa:")
            print(f"   Máximo de posições simultâneas: {max_positions}")
            print(f"   Risco total: {total_risk:.1%}")
            print(f"   Risco total em dinheiro: ${account_balance * total_risk:,.2f}")
            
            result = {
                'example': 'risk_management',
                'account_balance': account_balance,
                'risk_per_trade': risk_per_trade,
                'risk_amount': risk_amount,
                'stop_loss_pips': stop_loss_pips,
                'max_positions': max_positions,
                'total_risk': total_risk,
                'calculations': calculations,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no exemplo de risco: {e}")
            return None
            
    def export_results(self, filename: str = None):
        """Exportar todos os resultados"""
        if not filename:
            filename = f"examples_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'total_examples': len(self.results),
                'results': self.results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Resultados exportados para {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar resultados: {e}")
            return None
            
    async def close(self):
        """Fechar conexões"""
        if self.data_collector:
            await self.data_collector.close()


async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='IA GAIN - Examples and Backtesting')
    parser.add_argument('--example', choices=['basic', 'ml', 'forex', 'risk', 'all'], 
                       default='all', help='Tipo de exemplo a executar')
    parser.add_argument('--symbols', type=str, help='Símbolos específicos (separados por vírgula)')
    parser.add_argument('--days', type=int, default=30, help='Dias de dados para análise')
    parser.add_argument('--export', action='store_true', help='Exportar resultados')
    parser.add_argument('--config', type=str, help='Caminho do arquivo de configuração')
    parser.add_argument('--output', type=str, help='Arquivo de saída para exportação')
    
    args = parser.parse_args()
    
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║            IA GAIN - Examples and Backtesting              ║
║         Exemplos e Testes do Sistema                       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Inicializar executor
    runner = ExamplesRunner(args.config)
    
    # Configurar ambiente
    runner.setup_environment()
    
    # Verificar dependências
    print("🔍 Verificando dependências...")
    if not runner.check_dependencies():
        return 1
        
    # Verificar configuração
    print("🔍 Verificando configuração...")
    if not runner.check_config():
        return 1
        
    try:
        # Inicializar coletor de dados
        print("📊 Inicializando coletor de dados...")
        await runner.initialize_data_collector()
        
        # Executar exemplos solicitados
        if args.example == 'basic' or args.example == 'all':
            await runner.run_basic_example()
            
        if args.example == 'ml' or args.example == 'all':
            await runner.run_ml_backtest_example()
            
        if args.example == 'forex' or args.example == 'all':
            await runner.run_forex_example()
            
        if args.example == 'risk' or args.example == 'all':
            await runner.run_risk_management_example()
            
        # Mostrar resumo
        print(f"\n📋 Resumo da Execução:")
        print("=" * 50)
        print(f"Total de exemplos executados: {len(runner.results)}")
        
        for result in runner.results:
            print(f"✅ {result['example']}: {result.get('timestamp', 'N/A')}")
            
        # Exportar resultados se solicitado
        if args.export or args.output:
            filename = runner.export_results(args.output)
            if filename:
                print(f"\n💾 Resultados exportados para: {filename}")
                
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        runner.logger.error(f"Erro na execução: {e}")
        return 1
    finally:
        await runner.close()
        
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)