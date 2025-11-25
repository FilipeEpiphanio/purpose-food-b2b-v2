#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a conta atual conectada no MT5
"""

import MetaTrader5 as mt5
import datetime

def check_current_account():
    """Verifica qual conta está conectada no MT5"""
    
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
        
        print("=== INFORMAÇÕES DA CONTA ATUAL ===")
        print(f"Número da Conta: {account_info.login}")
        print(f"Nome da Conta: {account_info.name}")
        print(f"Servidor: {account_info.server}")
        print(f"Balanço: ${account_info.balance:.2f}")
        print(f"Equidade: ${account_info.equity:.2f}")
        print(f"Margem: ${account_info.margin:.2f}")
        print(f"Margem Livre: ${account_info.margin_free:.2f}")
        print(f"Alavancagem: 1:{account_info.leverage}")
        print(f"Moeda da Conta: {account_info.currency}")
        print("=" * 40)
        
        # Verificar se é a conta correta
        if account_info.login == 197944283:
            print("✅ CONTA CORRETA! (197944283)")
            return True
        else:
            print(f"❌ CONTA ERRADA! (Esperado: 197944283, Atual: {account_info.login})")
            print("\n⚠️  É necessário trocar a conta no MT5 Desktop:")
            print("   1. Abra o MT5 Desktop")
            print("   2. Vá em 'Arquivo' → 'Login para Negociação'")
            print("   3. Digite login: 197944283")
            print("   4. Digite a senha")
            print("   5. Selecione o servidor correto")
            print("   6. Clique em 'Login'")
            return False
            
    except Exception as e:
        print(f"Erro ao verificar conta: {e}")
        return False
    
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    check_current_account()