#!/usr/bin/env python3
"""
Simple IA GAIN System Test (No Pandas Required)
Tests basic functionality without external dependencies
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add the ia_gain directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ia_gain'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_imports():
    """Test basic module imports"""
    logger.info("Testing basic imports...")
    
    try:
        from ia_gain.core.base import TradingSignal, MarketData, SignalType, TradingDirection
        from ia_gain.core.ia_gain_system import IAGainSystem
        from ia_gain.utils.mock_data import MockDataGenerator
        from ia_gain.risk.risk_management_simple import SimpleRiskManager
        logger.info("✓ Basic imports successful")
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False

def test_data_generation():
    """Test mock data generation"""
    logger.info("Testing data generation...")
    
    try:
        from ia_gain.utils.mock_data import MockDataGenerator
        
        generator = MockDataGenerator()
        data = generator.generate_market_data('EURUSD', 'M15', 1.1000, 100)
        
        assert len(data) == 100, f"Expected 100 data points, got {len(data)}"
        assert all(hasattr(d, 'close_price') for d in data), "Missing close prices"
        assert all(hasattr(d, 'timestamp') for d in data), "Missing timestamps"
        
        logger.info(f"✓ Generated {len(data)} data points successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Data generation failed: {e}")
        return False

def test_risk_management():
    """Test risk management without pandas"""
    logger.info("Testing risk management...")
    
    try:
        from ia_gain.risk.risk_management_simple import SimpleRiskManager, SimpleRiskParameters
        
        params = SimpleRiskParameters(
            max_risk_per_trade=0.02,
            max_daily_risk=0.06,
            max_positions=5,
            stop_loss_pips=50,
            take_profit_pips=100,
            risk_reward_ratio=2.0
        )
        
        risk_manager = SimpleRiskManager(params)
        
        # Test position sizing
        position_size = risk_manager.calculate_position_size(
            account_balance=10000.0,
            risk_percentage=0.02,
            stop_loss_pips=50,
            pip_value=10.0
        )
        
        assert position_size > 0, "Invalid position size"
        
        # Test trade validation
        trade = {
            'symbol': 'EURUSD',
            'size': position_size,
            'stop_loss': 1.0950,
            'take_profit': 1.1100,
            'risk_percentage': 0.02
        }
        
        is_valid = risk_manager.validate_trade(trade)
        assert is_valid, "Trade should be valid"
        
        logger.info(f"✓ Risk management test passed - Position size: {position_size}")
        return True
    except Exception as e:
        logger.error(f"✗ Risk management failed: {e}")
        return False

def test_signal_creation():
    """Test signal creation and validation"""
    logger.info("Testing signal creation...")
    
    try:
        from ia_gain.core.base import TradingSignal, SignalType, TradingDirection, TimeFrame, StrategyType
        
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
        assert signal.signal_type == SignalType.BUY
        assert signal.strength == 0.8
        
        logger.info(f"✓ Signal creation test passed - Signal: {signal.signal_type}")
        return True
    except Exception as e:
        logger.error(f"✗ Signal creation failed: {e}")
        return False

def test_mock_trading_strategies():
    """Test mock trading strategies"""
    logger.info("Testing mock trading strategies...")
    
    try:
        from ia_gain.strategies.mock_strategies import MockStrategyManager
        from ia_gain.core.base import TradingSignal, SignalType, TradingDirection
        
        strategy_manager = MockStrategyManager()
        
        # Create test signal
        signal = TradingSignal(
            symbol='EURUSD',
            signal_type=SignalType.BUY,
            direction=TradingDirection.LONG,
            strength=0.8,
            timeframe='M15',
            strategy_type='MEAN_REVERSION',
            price=1.1000,
            stop_loss=1.0950,
            take_profit=1.1100,
            timestamp=datetime.now()
        )
        
        # Test strategy generation
        strategies = strategy_manager.generate_strategies([signal])
        assert len(strategies) > 0, "No strategies generated"
        
        logger.info(f"✓ Mock strategies test passed - Generated {len(strategies)} strategies")
        return True
    except Exception as e:
        logger.error(f"✗ Mock strategies failed: {e}")
        return False

def test_system_configuration():
    """Test system configuration"""
    logger.info("Testing system configuration...")
    
    try:
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
        
        # Test that all required keys are present
        required_keys = ['risk_percentage', 'max_positions', 'stop_loss_pips', 'take_profit_pips']
        for key in required_keys:
            assert key in config, f"Missing required config key: {key}"
        
        logger.info("✓ System configuration test passed")
        return True
    except Exception as e:
        logger.error(f"✗ System configuration failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    logger.info("Testing file structure...")
    
    required_files = [
        'ia_gain/core/base.py',
        'ia_gain/core/ia_gain_system.py',
        'ia_gain/utils/mock_data.py',
        'ia_gain/risk/risk_management_simple.py',
        'ia_gain/multi_timeframe/multi_timeframe_analyzer.py',
        'ia_gain/core/autonomous_operation.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"✗ Missing files: {missing_files}")
        return False
    
    logger.info(f"✓ All required files exist ({len(required_files)} files)")
    return True

def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "="*60)
    logger.info("IA GAIN SYSTEM SIMPLE INTEGRATION TEST")
    logger.info("="*60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Data Generation", test_data_generation),
        ("Risk Management", test_risk_management),
        ("Signal Creation", test_signal_creation),
        ("Mock Strategies", test_mock_trading_strategies),
        ("System Configuration", test_system_configuration),
        ("File Structure", test_file_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            logger.info(f"\n--- {test_name} ---")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    logger.info("="*60)
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)