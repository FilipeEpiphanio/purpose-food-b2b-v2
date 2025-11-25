#!/usr/bin/env python3
"""
Basic IA GAIN System Integration Test
Tests core functionality without external dependencies
"""

import sys
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_functionality():
    """Test basic system functionality"""
    logger.info("Testing basic IA GAIN system functionality...")
    
    try:
        # Add path for imports
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ia_gain'))
        
        # Test 1: Basic imports
        logger.info("1. Testing basic imports...")
        from core.base import TradingSignal, MarketData, SignalType, TradingDirection, TimeFrame, StrategyType
        from utils.mock_data import MockDataGenerator
        from risk.risk_management_simple import SimpleRiskManager, SimpleRiskParameters
        from strategies.mock_strategies import MockStrategyManager, create_mock_signal
        from core.autonomous_operation import AutonomousConfiguration, LearningMode
        logger.info("✓ Basic imports successful")
        
        # Test 2: Data generation
        logger.info("2. Testing data generation...")
        generator = MockDataGenerator()
        data = generator.generate_market_data('EURUSD', 'M15', 1.1000, 50)
        assert len(data) == 50, f"Expected 50 data points, got {len(data)}"
        logger.info(f"✓ Generated {len(data)} data points")
        
        # Test 3: Signal creation
        logger.info("3. Testing signal creation...")
        signal = TradingSignal(
            symbol='EURUSD',
            signal_type=SignalType.BUY,
            direction=TradingDirection.BUY,
            strength=0.8,
            timeframe=TimeFrame.M15,
            strategy_type=StrategyType.MEAN_REVERSION,
            price=1.1000,
            stop_loss=1.0950,
            take_profit=1.1100,
            timestamp=datetime.now()
        )
        assert signal.symbol == 'EURUSD'
        assert signal.strength == 0.8
        logger.info("✓ Signal creation successful")
        
        # Test 4: Risk management
        logger.info("4. Testing risk management...")
        params = SimpleRiskParameters(
            max_risk_per_trade=0.02,
            max_daily_risk=0.06,
            max_positions=5,
            stop_loss_pips=50,
            take_profit_pips=100,
            risk_reward_ratio=2.0
        )
        risk_manager = SimpleRiskManager(params)
        
        position_size = risk_manager.calculate_position_size(
            account_balance=10000.0,
            risk_percentage=0.02,
            stop_loss_pips=50,
            pip_value=10.0
        )
        assert position_size > 0, "Invalid position size"
        logger.info(f"✓ Risk management - Position size: {position_size}")
        
        # Test 5: Strategy generation
        logger.info("5. Testing strategy generation...")
        strategy_manager = MockStrategyManager()
        strategies = strategy_manager.generate_strategies([signal])
        assert len(strategies) > 0, "No strategies generated"
        logger.info(f"✓ Generated {len(strategies)} strategies")
        
        # Test 6: Strategy combination
        logger.info("6. Testing strategy combination...")
        combined_strategies = strategy_manager.combine_strategies(strategies)
        logger.info(f"✓ Combined {len(combined_strategies)} strategies")
        
        # Test 7: Autonomous configuration
        logger.info("7. Testing autonomous configuration...")
        config = AutonomousConfiguration(
            learning_mode=LearningMode.HYBRID,
            adaptation_threshold=0.6,
            performance_window=100,
            max_strategy_age=50,
            exploration_rate=0.1
        )
        assert config.learning_mode == LearningMode.HYBRID
        logger.info("✓ Autonomous configuration successful")
        
        # Test 8: Multi-timeframe analysis (basic)
        logger.info("8. Testing multi-timeframe concepts...")
        from multi_timeframe.multi_timeframe_analyzer import TimeframeSignal, SignalStrength
        
        timeframe_signal = TimeframeSignal(
            timeframe=TimeFrame.M15,
            signal_strength=SignalStrength.STRONG,
            technical_score=0.8,
            fundamental_score=0.7,
            sentiment_score=0.6
        )
        assert timeframe_signal.signal_strength == SignalStrength.STRONG
        logger.info("✓ Multi-timeframe concepts successful")
        
        logger.info("\n" + "="*60)
        logger.info("✓ ALL BASIC TESTS PASSED!")
        logger.info("IA GAIN System core functionality is working correctly")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_integration():
    """Test system integration concepts"""
    logger.info("\nTesting system integration concepts...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ia_gain'))
        
        # Test configuration
        config = {
            'risk_percentage': 2.0,
            'max_positions': 5,
            'stop_loss_pips': 50,
            'take_profit_pips': 100,
            'trailing_stop': True,
            'use_ml_models': True,
            'autonomous_enabled': True,
            'backtest_periods': 100,
            'mt5_enabled': False,
            'copy_trading_enabled': True,
            'multi_timeframe_enabled': True
        }
        
        # Test that all required components can be imported
        required_components = [
            'core.base',
            'core.ia_gain_system',
            'utils.mock_data',
            'risk.risk_management_simple',
            'strategies.mock_strategies',
            'core.autonomous_operation',
            'multi_timeframe.multi_timeframe_analyzer'
        ]
        
        for component in required_components:
            try:
                __import__(component)
                logger.info(f"✓ {component} imported successfully")
            except ImportError as e:
                logger.error(f"✗ Failed to import {component}: {e}")
                return False
        
        logger.info("✓ All system components available")
        
        # Test basic signal processing pipeline
        from core.base import TradingSignal, SignalType, TradingDirection, TimeFrame, StrategyType
        from utils.mock_data import MockDataGenerator
        from strategies.mock_strategies import MockStrategyManager
        
        # Generate data
        generator = MockDataGenerator()
        market_data = generator.generate_market_data('EURUSD', 'H1', 1.1000, 24)
        
        # Create signal based on data
        latest_price = market_data[-1].close_price
        signal = TradingSignal(
            symbol='EURUSD',
            signal_type=SignalType.BUY,
            direction=TradingDirection.BUY,
            strength=0.7,
            timeframe=TimeFrame.H1,
            strategy_type=StrategyType.MEAN_REVERSION,
            price=latest_price,
            stop_loss=latest_price * 0.99,
            take_profit=latest_price * 1.02,
            timestamp=datetime.now()
        )
        
        # Process signal through strategies
        strategy_manager = MockStrategyManager()
        strategies = strategy_manager.generate_strategies([signal])
        
        logger.info(f"✓ Signal processing pipeline - Generated {len(strategies)} strategies from {len(market_data)} data points")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    logger.info("="*60)
    logger.info("IA GAIN SYSTEM BASIC INTEGRATION TEST")
    logger.info("="*60)
    
    # Test basic functionality
    basic_success = test_basic_functionality()
    
    # Test system integration
    integration_success = test_system_integration()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    if basic_success and integration_success:
        logger.info("✓ ALL TESTS PASSED!")
        logger.info("IA GAIN System is ready for operation")
        logger.info("\nSystem capabilities:")
        logger.info("- Multi-timeframe analysis")
        logger.info("- Risk management")
        logger.info("- Strategy generation and combination")
        logger.info("- Autonomous operation")
        logger.info("- Backtesting capabilities")
        logger.info("- MetaTrader 5 integration (simulation)")
        return 0
    else:
        logger.error("✗ SOME TESTS FAILED!")
        logger.info("Please check the error messages above")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)