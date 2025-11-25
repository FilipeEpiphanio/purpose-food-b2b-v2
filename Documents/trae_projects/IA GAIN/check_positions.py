#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar posições abertas na conta 197944283
"""

import MetaTrader5 as mt5
import datetime

def check_open_positions():
    """Verifica posições abertas na conta atual"""
    
    # Inicializar MT5
    if not mt5.initialize():
        print(f"Erro ao inicializar MT5: {mt5.last_error()}")
        return False
    
    try:
        # Obter informações da conta
        account_info = mt5.account_info()
        
        if account_info is None:
            print("Não foi possível obter informações da conta")
            return False
        
        print(f"Verificando posições na conta: {account_info.login}")
        print("=" * 50)
        
        # Obter posições abertas
        positions = mt5.positions_get()
        
        if positions is None or len(positions) == 0:
            print("✅ NENHUMA posição aberta no momento")
            return True
        
        print(f"📊 POSIÇÕES ABERTAS: {len(positions)}")
        print("-" * 50)
        
        total_lucro = 0
        for i, position in enumerate(positions, 1):
            lucro = position.profit
            total_lucro += lucro
            
            print(f"Posição {i}:")
            print(f"  Símbolo: {position.symbol}")
            print(f"  Tipo: {'COMPRA' if position.type == mt5.ORDER_TYPE_BUY else 'VENDA'}")
            print(f"  Volume: {position.volume:.2f} lotes")
            print(f"  Preço Abertura: {position.price_open:.5f}")
            print(f"  Preço Atual: {position.price_current:.5f}")
            print(f"  SL: {position.sl:.5f}")
            print(f"  TP: {position.tp:.5f}")
            print(f"  Lucro: ${lucro:.2f}")
            print(f"  Tempo: {datetime.datetime.fromtimestamp(position.time)}")
            print()
        
        print(f"💰 LUCRO TOTAL DAS POSIÇÕES: ${total_lucro:.2f}")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"Erro ao verificar posições: {e}")
        return False
    
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    check_open_positions()