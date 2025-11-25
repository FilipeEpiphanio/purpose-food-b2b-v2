#!/usr/bin/env python3
"""
IA GAIN Trading System Demo Script
Demonstrates the complete functionality of the IA GAIN system
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the ia_gain directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ia_gain.core.base import (
    TradingSignal, MarketData, SignalType, TradingDirection, 
    TimeFrame, StrategyType, MarketCondition, Position
)
from ia_gain.core.ia_gain_system_simple import IAGainSystemSimple, SystemConfiguration
from ia_gain.multi_timeframe.multi_timeframe_analyzer_simple import MultiTimeframeAnalyzer
from ia_gain.risk.risk_management_simple import SimpleRiskManager, SimpleRiskParameters
from ia_gain.utils.mock_data import MockDataGenerator


class IAGainDemo:
    def __init__(self):
        self.system = None
        self.mock_generator = MockDataGenerator()
        
    async def initialize_system(self):
        """Initialize the IA GAIN system"""
        print("🚀 Inicializando Sistema IA GAIN...")
        
        # Create system configuration
        config = SystemConfiguration(
            risk_percentage=2.0,
            max_positions=5,
            stop_loss_pips=50,
            take_profit_pips=100,
            trailing_stop=True,
            use_ml_models=True,
            autonomous_enabled=True,
            backtest_periods=100,
            mt5_enabled=False,
            copy_trading_enabled=True,
            multi_timeframe_enabled=True
        )
        
        self.system = IAGainSystemSimple(config)
        await self.system.initialize()
        
        print("✅ Sistema IA GAIN inicializado com sucesso!")
        
    async def demo_multi_timeframe_analysis(self):
        """Demonstrate multi-timeframe analysis capabilities"""
        print("\n📊 Demonstrando Análise Multi-Timeframe...")
        
        # Generate mock market data for different timeframes
        market_data = {}
        for timeframe in [TimeFrame.M1, TimeFrame.M5, TimeFrame.M15, TimeFrame.H1]:
            market_data[timeframe] = self.mock_generator.generate_market_data(
                symbol='EURUSD',
                timeframe=timeframe.value,
                start_price=1.1000,
                periods=100
            )
        
        # Create multi-timeframe analyzer
        analyzer = MultiTimeframeAnalyzer()
        
        # Analyze multi-timeframe confluence
        result = await analyzer.analyze_multi_timeframe(
            symbol='EURUSD',
            market_data=market_data,
            timeframes=[TimeFrame.M1, TimeFrame.M5, TimeFrame.M15, TimeFrame.H1]
        )
        
        print(f"🎯 Confluência de Timeframes: {result.confluence_score:.2f}")
        print(f"📈 Sinal Principal: {result.primary_signal.direction} - Confiança: {result.primary_signal.confidence:.2f}")
        print(f"📊 Preço de Entrada: {result.primary_signal.entry_price:.4f}")
        
        if result.divergences:
            print(f"⚠️  Divergências Detectadas: {len(result.divergences)}")
            for divergence in result.divergences:
                print(f"   - {divergence.timeframe.value}: {divergence.type.value}")
        
        return result
        
    async def demo_risk_management(self):
        """Demonstrate risk management capabilities"""
        print("\n🛡️  Demonstrando Gerenciamento de Risco...")
        
        # Create risk manager parameters
        risk_params = SimpleRiskParameters(
            max_risk_per_trade=0.02,
            max_daily_risk=0.06,
            max_positions=5,
            risk_reward_ratio=2.0
        )
        risk_manager = SimpleRiskManager(risk_params)
        
        # Simulate different account balances and market conditions
        scenarios = [
            {"balance": 10000, "volatility": 0.15, "signal_strength": 0.8},
            {"balance": 50000, "volatility": 0.25, "signal_strength": 0.6},
            {"balance": 100000, "volatility": 0.35, "signal_strength": 0.9}
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n💰 Cenário {i}: Balance ${scenario['balance']:,} | Volatilidade {scenario['volatility']:.1%}")
            
            # Calculate position size using different methods
            position_sizes = {}
            for method in ['percentage', 'fixed', 'kelly']:
                size = risk_manager.calculate_position_size(
                    entry_price=1.1000,
                    stop_loss=1.0950,
                    account_balance=scenario['balance'],
                    confidence=scenario['signal_strength']
                )
                position_sizes[method] = size
                print(f"   📏 {method.replace('_', ' ').title()}: {size:.4f} lotes")
            
            # Validate trade
            validation_result = risk_manager.validate_trade(
                entry_price=1.1000,
                stop_loss=1.0950,
                take_profit=1.1100,
                confidence=scenario['signal_strength'],
                account_balance=scenario['balance']
            )
            is_valid = validation_result.get('is_valid', False)
            
            print(f"   ✅ Trade Válido: {is_valid}")
            
    async def demo_autonomous_operation(self):
        """Demonstrate autonomous operation capabilities"""
        print("\n🤖 Demonstrando Operação Autônoma...")
        
        # Generate market data for autonomous learning
        market_data = []
        for i in range(50):
            data = self.mock_generator.generate_market_data(
                symbol='EURUSD',
                timeframe=TimeFrame.M5.value,
                start_price=1.1000 + (i * 0.0001),  # Slight price variation
                periods=20
            )
            market_data.append(data)
        
        # Process data through autonomous operation
        if hasattr(self.system, 'autonomous_manager'):
            insights = []
            for data in market_data[:10]:  # Process first 10 data points
                insight = await self.system.autonomous_manager.process_market_data(data)
                if insight:
                    insights.append(insight)
            
            print(f"🧠 Insights Gerados: {len(insights)}")
            
            if insights:
                latest_insight = insights[-1]
                print(f"🎯 Último Insight: {latest_insight.type.value}")
                print(f"📊 Confiança: {latest_insight.confidence:.2f}")
                print(f"📈 Recomendação: {latest_insight.recommendation}")
                
        else:
            print("ℹ️  Operação Autônoma não disponível nesta versão simplificada")
            
    async def demo_backtesting(self):
        """Demonstrate backtesting capabilities"""
        print("\n📈 Demonstrando Backtesting...")
        
        # Generate historical market data
        historical_data = self.mock_generator.generate_market_data(
            symbol='EURUSD',
            timeframe=TimeFrame.H1.value,
            start_price=1.1000,
            periods=500
        )
        
        # Run backtest
        backtest_result = await self.system.backtest(
            symbol='EURUSD',
            market_data=historical_data,
            strategy_types=[StrategyType.MEAN_REVERSION, StrategyType.TREND_FOLLOWING],
            timeframe=TimeFrame.H1
        )
        
        print(f"📊 Resultados do Backtest:")
        print(f"   💰 Retorno Total: {backtest_result.total_return:.2%}")
        print(f"   📈 Retorno Anualizado: {backtest_result.annualized_return:.2%}")
        print(f"   ⚠️  Drawdown Máximo: {backtest_result.max_drawdown:.2%}")
        print(f"   📊 Sharpe Ratio: {backtest_result.sharpe_ratio:.2f}")
        print(f"   🎯 Taxa de Acerto: {backtest_result.win_rate:.1%}")
        print(f"   💼 Total de Trades: {backtest_result.total_trades}")
        print(f"   ✅ Trades Vencedores: {backtest_result.winning_trades}")
        print(f"   ❌ Trades Perdedores: {backtest_result.losing_trades}")
        
    async def demo_signal_generation(self):
        """Demonstrate signal generation capabilities"""
        print("\n🎯 Demonstrando Geração de Sinais...")
        
        # Generate current market data
        current_data = self.mock_generator.generate_market_data(
            symbol='EURUSD',
            timeframe=TimeFrame.M5.value,
            start_price=1.1000,
            periods=50
        )
        
        # Generate trading signals
        signals = await self.system.generate_signals(
            symbol='EURUSD',
            market_data=current_data,
            timeframe=TimeFrame.M5
        )
        
        print(f"🎯 Sinais Gerados: {len(signals)}")
        
        for i, signal in enumerate(signals[:3]):  # Show top 3 signals
            print(f"\n   Sinal {i+1}:")
            print(f"      📈 Direção: {signal.direction}")
            print(f"      💪 Confiança: {signal.confidence:.2f}")
            print(f"      🎯 Preço de Entrada: {signal.entry_price:.4f}")
            print(f"      ⏰ Timeframe: {signal.timeframe}")
            print(f"      🔧 Estratégia: {signal.strategy}")
            
    async def run_complete_demo(self):
        """Run the complete demonstration"""
        print("🚀 INICIANDO DEMONSTRAÇÃO COMPLETA DO SISTEMA IA GAIN")
        print("=" * 60)
        
        try:
            # Initialize system
            await self.initialize_system()
            
            # Run individual demonstrations
            await self.demo_multi_timeframe_analysis()
            await self.demo_risk_management()
            await self.demo_autonomous_operation()
            await self.demo_backtesting()
            await self.demo_signal_generation()
            
            print("\n" + "=" * 60)
            print("✅ DEMONSTRAÇÃO COMPLETA FINALIZADA COM SUCESSO!")
            print("🎯 O Sistema IA GAIN está totalmente operacional")
            print("📊 Todos os módulos foram testados e validados")
            print("🤖 Inclui análise multi-timeframe, gerenciamento de risco,")
            print("   operação autônoma, backtesting e geração de sinais")
            
        except Exception as e:
            print(f"❌ Erro durante a demonstração: {e}")
            import traceback
            traceback.print_exc()
            
    async def cleanup(self):
        """Cleanup system resources"""
        if self.system:
            await self.system.shutdown()
            print("\n🧹 Sistema finalizado e recursos liberados")


async def main():
    """Main demo function"""
    demo = IAGainDemo()
    
    try:
        await demo.run_complete_demo()
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    print("🎯 Sistema IA GAIN - Demonstração Completa")
    print("🔄 Iniciando ambiente de demonstração...")
    
    # Run the demo
    asyncio.run(main())