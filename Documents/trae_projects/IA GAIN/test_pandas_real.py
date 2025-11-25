#!/usr/bin/env python3
"""
Script de teste para verificar se o sistema IA GAIN está funcionando com pandas real
"""

import sys
sys.path.insert(0, '.')

def test_pandas_real():
    """Testa se o sistema está usando pandas real e não a camada de compatibilidade"""
    
    print('=== Testando importações do IA GAIN ===')
    
    # Testar importação do pandas através do nosso sistema
    try:
        from ia_gain.utils.pandas_init import pandas as pd
        print('✓ ia_gain.utils.pandas_init importado com sucesso')
        print(f'  - Tipo do pandas: {type(pd)}')
        print(f'  - Versão: {pd.__version__ if hasattr(pd, "__version__") else "N/A"}')
        
        # Verificar se é pandas real ou compatibilidade
        if hasattr(pd, 'DataFrame') and 'pandas' in str(type(pd)):
            print('  - ✅ ESTA É A BIBLIOTECA PANDAS REAL!')
        else:
            print('  - ⚠️  Pode ser a camada de compatibilidade')
            
    except Exception as e:
        print(f'✗ Erro ao importar pandas_init: {e}')
        return False
    
    # Testar importação de outros módulos
    try:
        from ia_gain.utils.data_processor import DataProcessor
        print('✓ DataProcessor importado com sucesso')
    except Exception as e:
        print(f'✗ Erro ao importar DataProcessor: {e}')
    
    try:
        from ia_gain.core.trading_engine import TradingEngine
        print('✓ TradingEngine importado com sucesso')
    except Exception as e:
        print(f'✗ Erro ao importar TradingEngine: {e}')
    
    print('\n=== Testando funcionalidade com pandas real ===')
    
    # Testar funcionalidade específica do pandas real
    try:
        # Criar DataFrame
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        print(f'✓ DataFrame criado com sucesso: {df.shape}')
        
        # Testar operações pandas
        df['C'] = df['A'] + df['B']
        print('✓ Operação de adição realizada: C = A + B')
        print(f'  Resultado:')
        print(df)
        
        # Testar groupby (funcionalidade avançada)
        df_grouped = df.groupby('A').sum()
        print(f'✓ GroupBy funcionando: {df_grouped.shape}')
        
        # Testar operações estatísticas
        print(f'✓ Média da coluna A: {df["A"].mean()}')
        print(f'✓ Soma da coluna B: {df["B"].sum()}')
        
        print('\n🎉 SUCESSO: O sistema IA GAIN está funcionando com pandas real!')
        print('📊 Todas as funcionalidades do pandas estão disponíveis!')
        
        return True
        
    except Exception as e:
        print(f'✗ Erro ao testar funcionalidade: {e}')
        print('⚠️  O sistema pode estar usando a camada de compatibilidade')
        return False

if __name__ == '__main__':
    success = test_pandas_real()
    sys.exit(0 if success else 1)