#!/usr/bin/env python3
"""
Complete IA GAIN System Integration Test
Tests all components working together in the complete system
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add the ia_gain directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ia_gain'))

from ia_gain.core.base import (
    TradingSignal, MarketData, SignalType, TradingDirection, 
    TimeFrame, StrategyType, RiskLevel, PositionStatus
)
from ia_gain.core.ia_gain_system import IAGainSystem
from ia_gain.core.autonomous_operation import AutonomousOperationManager, AutonomousConfiguration
from ia_gain.utils.mock_data import MockDataGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompleteSystemTest:
    def __init__(self):
        self.mock_data = MockDataGenerator()
        self.system = None
        self.test_results = {}
        
    async def setup_system(self):
        """Initialize the complete IA GAIN system"""
        logger.info("Setting up IA GAIN system...")
        
        # System configuration
        config = {
            'risk_percentage': 2.0,
            'max_positions': 5,
            'stop_loss_pips': 50,
            'take_profit_pips': 100,
            'trailing_stop': True,
            'use_ml_models': True,
            'autonomous_enabled': True,
            'backtest_periods': 100,
            'mt5_enabled': False,  # Use simulation for testing
            'copy_trading_enabled': True,
            'multi_timeframe_enabled': True
        }
        
        self.system = IAGainSystem(config)
        await self.system.initialize()
        
        logger.info("IA GAIN system initialized successfully")
        
    async def test_data_collection(self):
        """Test data collection from multiple sources"""
        logger.info("Testing data collection...")
        
        # Generate mock data for different timeframes
        timeframes = [TimeFrame.M1, TimeFrame.M5, TimeFrame.M15, TimeFrame.H1, TimeFrame.D1]
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD', 'ETHUSD']
        
        for symbol in symbols:
            for timeframe in timeframes:
                data = self.mock_data.generate_market_data(symbol, timeframe, 100)
                self.system.data_collector.add_data(symbol, timeframe, data)
        
        # Verify data collection
        collected_data = self.system.data_collector.get_data()
        assert len(collected_data) > 0, "No data collected"
        
        self.test_results['data_collection'] = {
            'status': 'PASSED',
            'symbols_tested': len(symbols),
            'timeframes_tested': len(timeframes),
            'total_data_points': sum(len(data) for data in collected_data.values())
        }
        
        logger.info(f"Data collection test passed - {len(collected_data)} data streams collected")
        
    async def test_analysis_components(self):
        """Test all analysis components"""
        logger.info("Testing analysis components...")
        
        # Generate test data
        test_data = self.mock_data.generate_market_data('EURUSD', TimeFrame.M15, 200)
        
        # Test technical analysis
        technical_signals = await self.system.technical_analyzer.analyze(test_data)
        assert len(technical_signals) > 0, "No technical signals generated"
        
        # Test fundamental analysis
        fundamental_signals = await self.system.fundamental_analyzer.analyze(test_data)
        assert len(fundamental_signals) > 0, "No fundamental signals generated"
        
        # Test momentum analysis
        momentum_signals = await self.system.momentum_analyzer.analyze(test_data)
        assert len(momentum_signals) > 0, "No momentum signals generated"
        
        # Test pattern recognition
        pattern_signals = await self.system.pattern_recognizer.analyze(test_data)
        assert len(pattern_signals) > 0, "No pattern signals generated"
        
        # Test ML predictions
        ml_signals = await self.system.ml_predictor.predict(test_data)
        assert len(ml_signals) > 0, "No ML signals generated"
        
        # Test multi-timeframe analysis
        if self.system.config.get('multi_timeframe_enabled'):
            multi_timeframe_signals = await self.system.multi_timeframe_analyzer.analyze_multi_timeframe('EURUSD')
            assert len(multi_timeframe_signals) > 0, "No multi-timeframe signals generated"
        
        self.test_results['analysis_components'] = {
            'status': 'PASSED',
            'technical_signals': len(technical_signals),
            'fundamental_signals': len(fundamental_signals),
            'momentum_signals': len(momentum_signals),
            'pattern_signals': len(pattern_signals),
            'ml_signals': len(ml_signals),
            'multi_timeframe_signals': len(multi_timeframe_signals) if self.system.config.get('multi_timeframe_enabled') else 0
        }
        
        logger.info("All analysis components test passed")
        
    async def test_strategy_system(self):
        """Test strategy generation and management"""
        logger.info("Testing strategy system...")
        
        # Generate test signals
        test_signals = [
            TradingSignal(
                symbol='EURUSD',
                signal_type=SignalType.BUY,
                direction=TradingDirection.LONG,
                strength=0.8,
                timeframe=TimeFrame.M15,
                strategy_type=StrategyType.MEAN_REVERSION,
                price=1.1000,
                stop_loss=1.0950,
                take_profit=1.1100,
                timestamp=datetime.now()
            )
        ]
        
        # Test strategy generation
        strategies = await self.system.strategy_manager.generate_strategies(test_signals)
        assert len(strategies) > 0, "No strategies generated"
        
        # Test strategy combination
        combined_strategies = self.system.strategy_manager.combine_strategies(strategies)
        assert len(combined_strategies) > 0, "No combined strategies"
        
        self.test_results['strategy_system'] = {
            'status': 'PASSED',
            'strategies_generated': len(strategies),
            'combined_strategies': len(combined_strategies),
            'strategy_types': list(set(s.strategy_type for s in strategies))
        }
        
        logger.info("Strategy system test passed")
        
    async def test_risk_management(self):
        """Test risk management system"""
        logger.info("Testing risk management...")
        
        # Test position sizing
        account_balance = 10000.0
        risk_per_trade = 0.02
        
        position_size = self.system.risk_manager.calculate_position_size(
            account_balance=account_balance,
            risk_percentage=risk_per_trade,
            stop_loss_pips=50,
            pip_value=10.0
        )
        
        assert position_size > 0, "Invalid position size calculated"
        
        # Test risk validation
        test_position = {
            'symbol': 'EURUSD',
            'size': position_size,
            'stop_loss': 1.0950,
            'take_profit': 1.1100,
            'risk_percentage': risk_per_trade
        }
        
        is_valid = self.system.risk_manager.validate_trade(test_position)
        assert is_valid, "Risk validation failed"
        
        # Test risk metrics
        risk_metrics = self.system.risk_manager.calculate_risk_metrics([test_position])
        assert risk_metrics is not None, "Risk metrics calculation failed"
        
        self.test_results['risk_management'] = {
            'status': 'PASSED',
            'position_size': position_size,
            'risk_validation': is_valid,
            'risk_metrics': risk_metrics
        }
        
        logger.info("Risk management test passed")
        
    async def test_autonomous_operation(self):
        """Test autonomous operation system"""
        logger.info("Testing autonomous operation...")
        
        if not self.system.config.get('autonomous_enabled'):
            logger.info("Autonomous operation disabled - skipping test")
            self.test_results['autonomous_operation'] = {'status': 'SKIPPED'}
            return
        
        # Test learning data collection
        test_decision = {
            'symbol': 'EURUSD',
            'action': 'BUY',
            'price': 1.1000,
            'timestamp': datetime.now(),
            'confidence': 0.8,
            'reasoning': 'Test decision for learning'
        }
        
        self.system.autonomous_operation.collect_learning_data(test_decision)
        
        # Test performance analysis
        performance_data = {
            'total_trades': 100,
            'winning_trades': 60,
            'losing_trades': 40,
            'win_rate': 0.6,
            'profit_factor': 1.5,
            'sharpe_ratio': 1.2,
            'max_drawdown': 0.05
        }
        
        insights = self.system.autonomous_operation.analyze_performance(performance_data)
        assert insights is not None, "Performance analysis failed"
        
        # Test strategy adaptation
        adaptation_result = self.system.autonomous_operation.adapt_strategy(
            current_performance=performance_data,
            market_conditions='trending'
        )
        assert adaptation_result is not None, "Strategy adaptation failed"
        
        self.test_results['autonomous_operation'] = {
            'status': 'PASSED',
            'learning_data_collected': True,
            'performance_insights': insights,
            'adaptation_result': adaptation_result
        }
        
        logger.info("Autonomous operation test passed")
        
    async def test_backtesting(self):
        """Test backtesting system"""
        logger.info("Testing backtesting system...")
        
        # Generate historical data
        historical_data = self.mock_data.generate_market_data('EURUSD', TimeFrame.H1, 500)
        
        # Configure backtest
        backtest_config = {
            'initial_balance': 10000.0,
            'risk_per_trade': 0.02,
            'max_positions': 5,
            'strategy_types': [StrategyType.MEAN_REVERSION, StrategyType.TREND_FOLLOWING]
        }
        
        # Run backtest
        backtest_result = await self.system.backtester.run_backtest(
            data=historical_data,
            config=backtest_config
        )
        
        assert backtest_result is not None, "Backtest failed"
        assert backtest_result.total_trades > 0, "No trades in backtest"
        
        self.test_results['backtesting'] = {
            'status': 'PASSED',
            'total_trades': backtest_result.total_trades,
            'win_rate': backtest_result.win_rate,
            'profit_factor': backtest_result.profit_factor,
            'final_balance': backtest_result.final_balance,
            'max_drawdown': backtest_result.max_drawdown
        }
        
        logger.info("Backtesting test passed")
        
    async def test_system_integration(self):
        """Test complete system integration"""
        logger.info("Testing system integration...")
        
        # Test system startup
        await self.system.start()
        
        # Let system run for a few cycles
        await asyncio.sleep(2)
        
        # Test data flow
        latest_signals = self.system.get_latest_signals()
        assert latest_signals is not None, "No signals generated"
        
        # Test performance metrics
        performance = self.system.get_performance_metrics()
        assert performance is not None, "No performance metrics"
        
        # Test system status
        status = self.system.get_system_status()
        assert status is not None, "No system status"
        
        # Stop system
        await self.system.stop()
        
        self.test_results['system_integration'] = {
            'status': 'PASSED',
            'signals_generated': len(latest_signals) if isinstance(latest_signals, list) else 1,
            'performance_metrics': performance,
            'system_status': status
        }
        
        logger.info("System integration test passed")
        
    async def run_all_tests(self):
        """Run all integration tests"""
        logger.info("Starting complete IA GAIN system integration tests...")
        
        try:
            # Setup
            await self.setup_system()
            
            # Run individual tests
            await self.test_data_collection()
            await self.test_analysis_components()
            await self.test_strategy_system()
            await self.test_risk_management()
            await self.test_autonomous_operation()
            await self.test_backtesting()
            await self.test_system_integration()
            
            # Summary
            self.print_test_summary()
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            self.test_results['test_execution'] = {'status': 'FAILED', 'error': str(e)}
            
    def print_test_summary(self):
        """Print test results summary"""
        logger.info("\n" + "="*60)
        logger.info("IA GAIN SYSTEM INTEGRATION TEST SUMMARY")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'PASSED')
        failed_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'FAILED')
        skipped_tests = sum(1 for result in self.test_results.values() if result.get('status') == 'SKIPPED')
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Skipped: {skipped_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        logger.info("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = result.get('status', 'UNKNOWN')
            logger.info(f"  {test_name}: {status}")
            if status == 'PASSED' and 'error' not in result:
                # Show key metrics for passed tests
                if test_name == 'data_collection':
                    logger.info(f"    - Data points: {result.get('total_data_points', 0)}")
                elif test_name == 'analysis_components':
                    logger.info(f"    - Technical signals: {result.get('technical_signals', 0)}")
                    logger.info(f"    - ML signals: {result.get('ml_signals', 0)}")
                elif test_name == 'backtesting':
                    logger.info(f"    - Total trades: {result.get('total_trades', 0)}")
                    logger.info(f"    - Win rate: {result.get('win_rate', 0):.2f}")
                    logger.info(f"    - Final balance: ${result.get('final_balance', 0):.2f}")
        
        logger.info("="*60)

async def main():
    """Main test execution"""
    tester = CompleteSystemTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())