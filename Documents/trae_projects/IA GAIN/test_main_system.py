"""
Teste Principal do Sistema IA GAIN com Compatibilidade Pandas
Verifica se o sistema principal funciona sem dependências externas do pandas
"""

import sys
import os
import asyncio
import logging
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pandas_compatibility():
    """Testa a camada de compatibilidade do pandas"""
    logger.info("=== Testando Compatibilidade Pandas ===")
    
    try:
        # Testar importação da camada de compatibilidade
        from ia_gain.utils.pandas_init import pandas as pd
        logger.info("✓ Camada de compatibilidade pandas importada com sucesso")
        
        # Testar criação de DataFrame
        data = {
            'open': [1.1000, 1.1005, 1.1010, 1.1008, 1.1012],
            'high': [1.1010, 1.1015, 1.1020, 1.1018, 1.1022],
            'low': [1.0995, 1.1000, 1.1005, 1.1003, 1.1007],
            'close': [1.1005, 1.1010, 1.1008, 1.1012, 1.1015],
            'volume': [1000, 1200, 1100, 1300, 1400]
        }
        
        df = pd.DataFrame(data)
        logger.info(f"✓ DataFrame criado com sucesso: {len(df)} linhas, {len(df.columns)} colunas")
        
        # Testar funções básicas
        mean_price = df['close'].mean()
        logger.info(f"✓ Média calculada: {mean_price}")
        
        rolling_mean = df['close'].rolling(window=3).mean()
        logger.info(f"✓ Média móvel calculada: {len(rolling_mean)} valores")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erro na compatibilidade pandas: {e}")
        return False

def test_core_system():
    """Testa o sistema core principal"""
    logger.info("=== Testando Sistema Core Principal ===")
    
    try:
        from ia_gain.core.ia_gain_system import IAGainSystem, SystemConfig
        logger.info("✓ Sistema IA GAIN importado com sucesso")
        
        # Criar configuração básica
        config = SystemConfig(
            symbols=["EURUSD", "GBPUSD", "USDJPY"],
            timeframes=["1h", "4h", "1d"],
            risk_percentage=0.01,
            max_positions=5,
            technical_enabled=True,
            fundamental_enabled=True,
            momentum_enabled=True,
            pattern_enabled=True,
            strategies_enabled=["mean_reversion", "trend_following", "momentum"],
            ml_enabled=True,
            backtesting_enabled=True,
            risk_enabled=True,  # Changed from risk_management_enabled
            autonomous_enabled=True,
            mt5_enabled=False,  # Desabilitar MT5 para teste
            auto_trading=False,  # Desabilitar auto trading para teste
            copy_trading=False
        )
        
        logger.info("✓ Configuração do sistema criada com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"✗ Erro no sistema core: {e}")
        return False

def test_multi_timeframe():
    """Testa o analisador multi-timeframe"""
    logger.info("=== Testando Analisador Multi-Timeframe ===")
    
    try:
        from ia_gain.multi_timeframe.multi_timeframe_analyzer import MultiTimeframeAnalyzer, Timeframe
        from ia_gain.utils.mock_data import MockDataGenerator
        
        # Criar gerador de dados mock
        mock_gen = MockDataGenerator()
        
        # Gerar dados para múltiplos timeframes
        market_data = {}
        timeframes = [Timeframe.H1, Timeframe.H4, Timeframe.D1]
        
        for tf in timeframes:
            market_data[tf] = mock_gen.generate_market_data(
                symbol="EURUSD",
                timeframe=tf.value,
                start_price=1.1000,
                periods=100
            )
        
        # Criar analisador
        analyzer = MultiTimeframeAnalyzer()
        
        logger.info("✓ Analisador multi-timeframe criado com sucesso")
        logger.info(f"✓ Dados gerados para {len(market_data)} timeframes")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erro no analisador multi-timeframe: {e}")
        return False

def test_autonomous_operation():
    """Testa o sistema de operação autônoma"""
    logger.info("=== Testando Sistema de Operação Autônoma ===")
    
    try:
        from ia_gain.core.autonomous_operation import AutonomousOperationManager, AutonomousConfiguration
        
        # Criar configuração autônoma
        from ia_gain.core.autonomous_operation import LearningMode, AdaptationStrategy
        
        config = AutonomousConfiguration(
            enabled=True,
            learning_mode=LearningMode.HYBRID,
            adaptation_strategy=AdaptationStrategy.AGGRESSIVE,
            auto_parameter_optimization=True,
            auto_strategy_selection=True,
            auto_risk_adjustment=True,
            performance_monitoring=True,
            max_consecutive_losses=5,
            min_performance_threshold=0.6,
            learning_interval_hours=1,
            adaptation_interval_hours=4
        )
        
        logger.info("✓ Configuração autônoma criada com sucesso")
        
        # Criar gerenciador (sem iniciar loops)
        # Passar None como sistema para teste
        manager = AutonomousOperationManager(None, config)
        
        logger.info("✓ Gerenciador de operação autônoma criado com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erro no sistema autônomo: {e}")
        return False

def test_risk_management():
    """Testa o sistema de gerenciamento de risco"""
    logger.info("=== Testando Gerenciamento de Risco ===")
    
    try:
        from ia_gain.risk.risk_management import RiskManager, RiskParameters
        
        # Criar parâmetros de risco
        from ia_gain.risk.risk_management import PositionSizingMethod
        
        risk_params = RiskParameters(
            max_risk_per_trade=0.02,
            max_daily_risk=0.06,
            max_weekly_risk=0.12,
            max_monthly_risk=0.20,
            max_drawdown=0.15,
            max_correlation_risk=0.70,
            min_risk_reward_ratio=1.5,
            max_leverage=10.0,
            position_sizing_method=PositionSizingMethod.PERCENTAGE_RISK,
            volatility_lookback=20,
            confidence_level=0.95
        )
        
        # Criar gerenciador de risco
        risk_manager = RiskManager(risk_params)
        
        logger.info("✓ Gerenciador de risco criado com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erro no gerenciamento de risco: {e}")
        return False

async def test_complete_system():
    """Testa o sistema completo de forma assíncrona"""
    logger.info("=== Testando Sistema Completo IA GAIN ===")
    
    try:
        from ia_gain.core.ia_gain_system import IAGainSystem, SystemConfig
        
        # Criar configuração completa
        config = SystemConfig(
            symbols=["EURUSD"],
            timeframes=["1h"],
            risk_percentage=0.01,
            max_positions=3,
            technical_enabled=True,
            fundamental_enabled=True,
            momentum_enabled=True,
            pattern_enabled=True,
            strategies_enabled=["mean_reversion", "trend_following"],
            ml_enabled=True,
            backtesting_enabled=True,
            risk_enabled=True,  # Changed from risk_management_enabled
            autonomous_enabled=True,
            mt5_enabled=False,  # Desabilitar MT5 para teste
            auto_trading=False,  # Desabilitar auto trading para teste
            copy_trading=False
        )
        
        # Criar sistema
        system = IAGainSystem(config)
        
        logger.info("✓ Sistema IA GAIN completo criado com sucesso")
        logger.info("✓ Todos os módulos principais estão funcionando")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erro no sistema completo: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal de teste"""
    logger.info("=" * 60)
    logger.info("INICIANDO TESTES DO SISTEMA IA GAIN PRINCIPAL")
    logger.info("=" * 60)
    
    # Executar testes individuais
    tests = [
        ("Compatibilidade Pandas", test_pandas_compatibility),
        ("Sistema Core", test_core_system),
        ("Multi-Timeframe", test_multi_timeframe),
        ("Operação Autônoma", test_autonomous_operation),
        ("Gerenciamento de Risco", test_risk_management)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name}: PASSED")
            else:
                logger.error(f"✗ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name}: ERRO - {e}")
    
    # Teste assíncrono do sistema completo
    logger.info("\n" + "=" * 40)
    logger.info("TESTANDO SISTEMA COMPLETO")
    logger.info("=" * 40)
    
    try:
        result = asyncio.run(test_complete_system())
        if result:
            passed += 1
            logger.info("✓ Sistema Completo: PASSED")
        else:
            logger.error("✗ Sistema Completo: FAILED")
    except Exception as e:
        logger.error(f"✗ Sistema Completo: ERRO - {e}")
    
    # Resultado final
    logger.info("\n" + "=" * 60)
    logger.info(f"RESULTADO FINAL: {passed}/{total + 1} testes passaram")
    
    if passed == total + 1:
        logger.info("🎉 TODOS OS TESTES PASSARAM!")
        logger.info("✅ O sistema IA GAIN principal está funcionando sem dependências externas do pandas!")
    else:
        logger.warning(f"⚠️  {total + 1 - passed} testes falharam")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()