#!/usr/bin/env python3
"""
IA GAIN - Simple Backtest
Backtest simplificado sem dependências externas problemáticas
"""

import sys
import os
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

class SimpleBacktest:
    """Backtest simplificado para IA GAIN"""
    
    def __init__(self):
        self.results = []
        self.strategies = ['momentum', 'mean_reversion', 'breakout', 'trend_following']
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']
        
    def generate_mock_data(self, symbol, days=30):
        """Gerar dados simulados para teste"""
        data = []
        base_price = random.uniform(100, 50000)
        volatility = random.uniform(0.01, 0.05)
        
        current_time = datetime.now() - timedelta(days=days)
        
        for i in range(days * 24):  # Dados horários
            change = random.uniform(-volatility, volatility)
            base_price *= (1 + change)
            
            data.append({
                'timestamp': current_time.isoformat(),
                'symbol': symbol,
                'open': base_price * random.uniform(0.99, 1.01),
                'high': base_price * random.uniform(1.01, 1.03),
                'low': base_price * random.uniform(0.97, 0.99),
                'close': base_price,
                'volume': random.uniform(1000, 1000000)
            })
            
            current_time += timedelta(hours=1)
            
        return data
    
    def momentum_strategy(self, data):
        """Estratégia de momentum simples"""
        if len(data) < 20:
            return {'signal': 'HOLD', 'strength': 0.0}
            
        recent = data[-20:]
        returns = [(recent[i]['close'] - recent[i-1]['close']) / recent[i-1]['close'] 
                  for i in range(1, len(recent))]
        
        avg_return = sum(returns) / len(returns)
        
        if avg_return > 0.01:
            return {'signal': 'BUY', 'strength': min(avg_return * 10, 1.0)}
        elif avg_return < -0.01:
            return {'signal': 'SELL', 'strength': min(abs(avg_return) * 10, 1.0)}
        else:
            return {'signal': 'HOLD', 'strength': 0.0}
    
    def mean_reversion_strategy(self, data):
        """Estratégia de mean reversion simples"""
        if len(data) < 50:
            return {'signal': 'HOLD', 'strength': 0.0}
            
        prices = [d['close'] for d in data[-50:]]
        mean_price = sum(prices) / len(prices)
        current_price = data[-1]['close']
        
        deviation = (current_price - mean_price) / mean_price
        
        if deviation < -0.02:
            return {'signal': 'BUY', 'strength': min(abs(deviation) * 10, 1.0)}
        elif deviation > 0.02:
            return {'signal': 'SELL', 'strength': min(deviation * 10, 1.0)}
        else:
            return {'signal': 'HOLD', 'strength': 0.0}
    
    def breakout_strategy(self, data):
        """Estratégia de breakout simples"""
        if len(data) < 30:
            return {'signal': 'HOLD', 'strength': 0.0}
            
        prices = [d['close'] for d in data[-30:]]
        high = max(prices[:-5])
        low = min(prices[:-5])
        current_price = data[-1]['close']
        
        if current_price > high * 1.01:
            return {'signal': 'BUY', 'strength': 0.8}
        elif current_price < low * 0.99:
            return {'signal': 'SELL', 'strength': 0.8}
        else:
            return {'signal': 'HOLD', 'strength': 0.0}
    
    def trend_following_strategy(self, data):
        """Estratégia de trend following simples"""
        if len(data) < 25:
            return {'signal': 'HOLD', 'strength': 0.0}
            
        prices = [d['close'] for d in data[-25:]]
        
        # Médias móveis simples
        ma_short = sum(prices[-10:]) / 10
        ma_long = sum(prices[-20:]) / 20
        current_price = data[-1]['close']
        
        if ma_short > ma_long * 1.005 and current_price > ma_short:
            return {'signal': 'BUY', 'strength': 0.7}
        elif ma_short < ma_long * 0.995 and current_price < ma_short:
            return {'signal': 'SELL', 'strength': 0.7}
        else:
            return {'signal': 'HOLD', 'strength': 0.0}
    
    def backtest_strategy(self, strategy_name, symbol, data):
        """Executar backtest de uma estratégia"""
        strategy_func = getattr(self, f'{strategy_name}_strategy')
        
        trades = []
        position = None
        entry_price = 0
        total_return = 0
        max_drawdown = 0
        peak_value = 1000  # Valor inicial simulado
        current_value = peak_value
        
        for i in range(50, len(data)):  # Começar após período inicial
            historical_data = data[:i+1]
            signal = strategy_func(historical_data)
            current_price = data[i]['close']
            
            if signal['signal'] == 'BUY' and position != 'LONG':
                if position == 'SHORT':
                    # Fechar posição short
                    profit = (entry_price - current_price) / entry_price
                    current_value *= (1 + profit)
                    trades.append({'type': 'CLOSE_SHORT', 'price': current_price, 'profit': profit})
                
                # Abrir posição long
                position = 'LONG'
                entry_price = current_price
                trades.append({'type': 'OPEN_LONG', 'price': current_price})
                
            elif signal['signal'] == 'SELL' and position != 'SHORT':
                if position == 'LONG':
                    # Fechar posição long
                    profit = (current_price - entry_price) / entry_price
                    current_value *= (1 + profit)
                    trades.append({'type': 'CLOSE_LONG', 'price': current_price, 'profit': profit})
                
                # Abrir posição short
                position = 'SHORT'
                entry_price = current_price
                trades.append({'type': 'OPEN_SHORT', 'price': current_price})
            
            # Calcular drawdown
            if current_value > peak_value:
                peak_value = current_value
            drawdown = (peak_value - current_value) / peak_value
            max_drawdown = max(max_drawdown, drawdown)
        
        # Fechar posição final
        if position == 'LONG':
            final_price = data[-1]['close']
            profit = (final_price - entry_price) / entry_price
            current_value *= (1 + profit)
            trades.append({'type': 'CLOSE_LONG', 'price': final_price, 'profit': profit})
        elif position == 'SHORT':
            final_price = data[-1]['close']
            profit = (entry_price - final_price) / entry_price
            current_value *= (1 + profit)
            trades.append({'type': 'CLOSE_SHORT', 'price': final_price, 'profit': profit})
        
        total_return = (current_value - 1000) / 1000
        
        return {
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'num_trades': len(trades),
            'final_value': current_value,
            'trades': trades
        }
    
    def run_comprehensive_backtest(self):
        """Executar backtest completo com todas as estratégias e símbolos"""
        print("🚀 Iniciando Backtest Completo")
        print("=" * 60)
        
        all_results = {}
        best_strategy = None
        best_symbol = None
        best_return = -float('inf')
        
        for strategy in self.strategies:
            print(f"\n📊 Testando estratégia: {strategy.upper()}")
            strategy_results = {}
            
            for symbol in self.symbols:
                print(f"  📈 Testando símbolo: {symbol}")
                
                # Gerar dados simulados
                data = self.generate_mock_data(symbol, 30)
                
                # Executar backtest
                result = self.backtest_strategy(strategy, symbol, data)
                
                strategy_results[symbol] = result
                
                # Atualizar melhor resultado
                if result['total_return'] > best_return:
                    best_return = result['total_return']
                    best_strategy = strategy
                    best_symbol = symbol
                
                print(f"    💰 Retorno: {result['total_return']:.2%}")
                print(f"    📉 Drawdown Máx: {result['max_drawdown']:.2%}")
                print(f"    🔄 Trades: {result['num_trades']}")
            
            all_results[strategy] = strategy_results
        
        # Gerar relatório final
        self.generate_report(all_results, best_strategy, best_symbol, best_return)
        
        return {
            'all_results': all_results,
            'best_strategy': best_strategy,
            'best_symbol': best_symbol,
            'best_return': best_return
        }
    
    def generate_report(self, results, best_strategy, best_symbol, best_return):
        """Gerar relatório detalhado do backtest"""
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL DO BACKTEST")
        print("=" * 60)
        
        print(f"\n🏆 MELHOR DESEMPENHO:")
        print(f"   Estratégia: {best_strategy.upper()}")
        print(f"   Símbolo: {best_symbol}")
        print(f"   Retorno: {best_return:.2%}")
        
        print(f"\n📊 RESUMO POR ESTRATÉGIA:")
        for strategy, symbols in results.items():
            avg_return = sum(s['total_return'] for s in symbols.values()) / len(symbols)
            avg_drawdown = sum(s['max_drawdown'] for s in symbols.values()) / len(symbols)
            total_trades = sum(s['num_trades'] for s in symbols.values())
            
            print(f"\n   {strategy.upper()}:")
            print(f"     Retorno Médio: {avg_return:.2%}")
            print(f"     Drawdown Médio: {avg_drawdown:.2%}")
            print(f"     Total de Trades: {total_trades}")
        
        print(f"\n📈 RESUMO POR SÍMBOLO:")
        for symbol in self.symbols:
            symbol_returns = []
            for strategy_results in results.values():
                if symbol in strategy_results:
                    symbol_returns.append(strategy_results[symbol]['total_return'])
            
            if symbol_returns:
                avg_return = sum(symbol_returns) / len(symbol_returns)
                best_symbol_return = max(symbol_returns)
                print(f"\n   {symbol}:")
                print(f"     Retorno Médio: {avg_return:.2%}")
                print(f"     Melhor Retorno: {best_symbol_return:.2%}")
        
        # Salvar resultados em arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backtest_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'best_strategy': best_strategy,
                'best_symbol': best_symbol,
                'best_return': best_return,
                'all_results': results
            }, f, indent=2)
        
        print(f"\n💾 Resultados salvos em: {filename}")

def main():
    """Função principal"""
    print("🎯 IA GAIN - Backtest Simplificado")
    print("=" * 50)
    
    backtest = SimpleBacktest()
    results = backtest.run_comprehensive_backtest()
    
    print(f"\n✅ Backtest concluído com sucesso!")
    print(f"🎯 Melhor estratégia: {results['best_strategy']}")
    print(f"🪙 Melhor ativo: {results['best_symbol']}")
    print(f"💰 Melhor retorno: {results['best_return']:.2%}")

if __name__ == "__main__":
    main()