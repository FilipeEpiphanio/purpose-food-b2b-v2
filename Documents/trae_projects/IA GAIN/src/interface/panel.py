from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Dict, Optional

try:
    import MetaTrader5 as MT5
except Exception:  # pragma: no cover
    MT5 = None


class TradingDashboard:
    """Painel textual simples inspirado no layout fornecido.

    Mostra: hora do servidor, tempo para próxima barra, acertos (win/total),
    lucro por dia/semana/mês, lucro total do ativo, estratégia atual, e estado.
    """

    def __init__(self, timeframe_seconds: int = 3600):
        self.timeframe_seconds = timeframe_seconds
        self.win_day = 0
        self.trades_day = 0
        self.profit_day = 0.0

        self.win_week = 0
        self.trades_week = 0
        self.profit_week = 0.0

        self.win_month = 0
        self.trades_month = 0
        self.profit_month = 0.0

        self.win_total = 0
        self.trades_total = 0
        self.profit_total = 0.0

        self.current_strategy: Optional[str] = None
        self.current_symbol: Optional[str] = None
        self.current_position_state: str = "Zerado"
        self.current_quantity: float = 0.0
        self.current_result: float = 0.0
        self.robot_status: str = "Robô totalmente carregado."

    def _server_time_str(self) -> str:
        if MT5 is not None:
            try:
                info = MT5.terminal_info()
                # MetaTrader5 não retorna o horário do servidor diretamente; usamos local
            except Exception:
                pass
        return datetime.now().strftime("%H:%M:%S")

    def _next_bar_countdown(self) -> str:
        now = datetime.now()
        seconds = self.timeframe_seconds
        epoch = int(now.timestamp())
        remainder = seconds - (epoch % seconds)
        return str(timedelta(seconds=remainder))

    def record_open(self, symbol: str, strategy_name: str, quantity: float):
        self.current_symbol = symbol
        self.current_strategy = strategy_name
        self.current_position_state = "Aberta"
        self.current_quantity = float(quantity)

    def record_close(self, pnl: float, won: bool):
        self.current_position_state = "Zerado"
        self.current_quantity = 0.0
        self.current_result = float(pnl)

        # Atualizar contadores
        self.trades_total += 1
        self.profit_total += pnl
        if won:
            self.win_total += 1

        # Partições por dia/semana/mês (sessão)
        self.trades_day += 1
        self.profit_day += pnl
        if won:
            self.win_day += 1

        self.trades_week += 1
        self.profit_week += pnl
        if won:
            self.win_week += 1

        self.trades_month += 1
        self.profit_month += pnl
        if won:
            self.win_month += 1

    def render(self) -> str:
        # Cabeçalho estilo terminal
        lines = []
        lines.append("[D]  IA GAIN Dashboard")
        lines.append(f"Hora Serv.: {self._server_time_str()}    Próx.Barra {self._next_bar_countdown()}")
        lines.append(
            f"Dia    {self.win_day}/{self.trades_day}    {self.profit_day:6.2f}"
        )
        lines.append(
            f"Semana {self.win_week}/{self.trades_week}    {self.profit_week:6.2f}"
        )
        lines.append(
            f"Mês    {self.win_month}/{self.trades_month}    {self.profit_month:6.2f}"
        )
        lines.append(
            f"Total  {self.win_total}/{self.trades_total}    {self.profit_total:6.2f}"
        )
        lines.append(f"Posição           {self.current_position_state}")
        lines.append(f"Quantidade        {self.current_quantity:.2f}")
        lines.append(f"Resultado         {self.current_result:.2f}")
        if self.current_symbol and self.current_strategy:
            lines.append(f"Ativo/Strat.     {self.current_symbol} | {self.current_strategy}")
        lines.append(self.robot_status)
        return "\n".join(lines)

    def print(self):
        # Limpar tela de forma simples (Windows/PowerShell)
        try:
            print("\033[2J\033[H", end="")  # ANSI clear
        except Exception:
            pass
        print(self.render())