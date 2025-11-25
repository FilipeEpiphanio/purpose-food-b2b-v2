#!/usr/bin/env python3
"""
Script para verificar símbolos disponíveis no MetaTrader 5
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import json

def verificar_simbolos_disponiveis():
    """Verifica todos os símbolos disponíveis no servidor MT5"""
    
    print("🔍 Verificando símbolos disponíveis no MetaTrader 5...")
    print("=" * 60)
    
    # Inicializar MT5
    if not mt5.initialize():
        print(f"❌ Erro ao inicializar MT5: {mt5.last_error()}")
        return
    
    try:
        # Obter informações da conta
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ Não foi possível obter informações da conta")
            return
            
        print(f"📊 Conta: {account_info.login} | Saldo: ${account_info.balance:.2f}")
        print(f"🏢 Servidor: {account_info.server}")
        print(f"📈 Companhia: {account_info.company}")
        print("=" * 60)
        
        # Obter todos os símbolos disponíveis
        symbols = mt5.symbols_get()
        
        if symbols is None or len(symbols) == 0:
            print("❌ Nenhum símbolo encontrado")
            return
        
        print(f"📋 Total de símbolos encontrados: {len(symbols)}")
        print()
        
        # Categorizar símbolos
        forex_symbols = []
        crypto_symbols = []
        stock_symbols = []
        commodity_symbols = []
        index_symbols = []
        other_symbols = []
        
        for symbol in symbols:
            symbol_name = symbol.name
            
            # Categorizar baseado no nome e path do símbolo
            if any(currency in symbol_name for currency in ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD']):
                if len(symbol_name) == 6 or symbol_name.endswith('m') or symbol_name.endswith('c'):
                    forex_symbols.append(symbol_name)
                else:
                    other_symbols.append(symbol_name)
            elif any(crypto in symbol_name for crypto in ['BTC', 'ETH', 'XRP', 'LTC', 'BCH']):
                crypto_symbols.append(symbol_name)
            elif any(commodity in symbol_name for commodity in ['GOLD', 'SILVER', 'OIL', 'GAS']):
                commodity_symbols.append(symbol_name)
            elif any(index in symbol_name for index in ['IDX', 'INDEX', 'SPX', 'NDX']):
                index_symbols.append(symbol_name)
            elif len(symbol_name) <= 5 and symbol_name.isalpha():
                stock_symbols.append(symbol_name)
            else:
                other_symbols.append(symbol_name)
        
        # Mostrar símbolos por categoria
        print("💰 PARES DE MOEDAS (FOREX):")
        for symbol in sorted(forex_symbols)[:20]:  # Mostrar primeiros 20
            print(f"  • {symbol}")
        if len(forex_symbols) > 20:
            print(f"  ... e mais {len(forex_symbols) - 20} símbolos")
        print()
        
        print("🪙 CRIPTOMOEDAS:")
        for symbol in sorted(crypto_symbols):
            print(f"  • {symbol}")
        print()
        
        print("🥇 COMMODITIES:")
        for symbol in sorted(commodity_symbols):
            print(f"  • {symbol}")
        print()
        
        print("📊 ÍNDICES:")
        for symbol in sorted(index_symbols):
            print(f"  • {symbol}")
        print()
        
        print("📈 AÇÕES:")
        for symbol in sorted(stock_symbols)[:10]:
            print(f"  • {symbol}")
        if len(stock_symbols) > 10:
            print(f"  ... e mais {len(stock_symbols) - 10} símbolos")
        print()
        
        if other_symbols:
            print("🔧 OUTROS SÍMBOLOS:")
            for symbol in sorted(other_symbols)[:10]:
                print(f"  • {symbol}")
            if len(other_symbols) > 10:
                print(f"  ... e mais {len(other_symbols) - 10} símbolos")
        
        print("\n" + "=" * 60)
        print("✅ Verificação concluída!")
        
        # Salvar lista completa em arquivo
        simbolos_data = {
            'data_verificacao': datetime.now().isoformat(),
            'total_simbolos': len(symbols),
            'conta': account_info.login,
            'servidor': account_info.server,
            'categorias': {
                'forex': len(forex_symbols),
                'crypto': len(crypto_symbols),
                'commodities': len(commodity_symbols),
                'indices': len(index_symbols),
                'stocks': len(stock_symbols),
                'outros': len(other_symbols)
            },
            'simbolos': {
                'forex': sorted(forex_symbols),
                'crypto': sorted(crypto_symbols),
                'commodities': sorted(commodity_symbols),
                'indices': sorted(index_symbols),
                'stocks': sorted(stock_symbols),
                'outros': sorted(other_symbols)
            }
        }
        
        with open('simbolos_mt5_disponiveis.json', 'w', encoding='utf-8') as f:
            json.dump(simbolos_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Lista completa salva em: simbolos_mt5_disponiveis.json")
        
    except Exception as e:
        print(f"❌ Erro durante a verificação: {e}")
        
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    verificar_simbolos_disponiveis()