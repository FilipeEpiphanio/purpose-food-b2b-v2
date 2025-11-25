import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

from flask import Flask, render_template_string, request, redirect, url_for, flash

# Garantir que imports de 'src' funcionem ao rodar via scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.brokers.mt5_broker import MT5Broker


app = Flask(__name__)
app.secret_key = "ia-gain-secret"


TEMPLATE_INDEX = """
<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>IA GAIN - Aprovação de Portfólio</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 20px; }
      table { width: 100%; border-collapse: collapse; }
      th, td { border: 1px solid #ddd; padding: 8px; }
      th { background: #f4f4f4; text-align: left; }
      .actions { margin-top: 16px; }
      .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; background: #eee; }
    </style>
  </head>
  <body>
    <h2>IA GAIN - Aprovação de Portfólio</h2>
    <p>Timeframe: <span class="badge">{{ timeframe }}</span> | Universo: <span class="badge">{{ only }}</span> | Top-N: <span class="badge">{{ top_n }}</span> | MT5 All: <span class="badge">{{ 'Sim' if mt5_all else 'Não' }}</span></p>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul>
          {% for msg in messages %}
            <li>{{ msg }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    <form method="post" action="{{ url_for('approve') }}">
      <table>
        <thead>
          <tr>
            <th>Selecionar</th>
            <th>Ativo</th>
            <th>Estratégia</th>
            <th>Score DE</th>
            <th>Score Normalizado</th>
            <th>Win Rate</th>
            <th>Sharpe</th>
            <th>Retorno Total</th>
            <th>Ticket (última execução)</th>
          </tr>
        </thead>
        <tbody>
        {% for p in portfolio %}
          <tr>
            <td><input type="checkbox" name="symbol" value="{{ p.symbol }}" checked></td>
            <td>{{ p.symbol }}</td>
            <td>{{ p.strategy or '-' }}</td>
            <td>{{ '%.2f' % p.decision_engine_score if p.decision_engine_score is not none else '-' }}</td>
            <td>{{ '%.2f' % p.normalized_score if p.normalized_score is not none else '-' }}</td>
            <td>{{ '%.1f%%' % (p.win_rate) if p.win_rate is not none else '-' }}</td>
            <td>{{ '%.2f' % p.sharpe if p.sharpe is not none else '-' }}</td>
            <td>{{ '%.2f' % p.total_return if p.total_return is not none else '-' }}</td>
            <td>{{ p.ticket or '-' }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>

      <div class="actions">
        <label>Tamanho do lote (para todos): <input type="number" name="lot" step="0.01" min="0.01" value="0.10"></label>
        <label style="margin-left:16px;">Direção: 
          <select name="side">
            <option value="buy" selected>Compra</option>
            <option value="sell">Venda</option>
          </select>
        </label>
        <button type="submit" style="margin-left:16px;">Aprovar selecionados</button>
      </div>
    </form>

  </body>
</html>
"""


TEMPLATE_RESULTS = """
<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>IA GAIN - Resultado da Aprovação</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 20px; }
      table { width: 100%; border-collapse: collapse; }
      th, td { border: 1px solid #ddd; padding: 8px; }
      th { background: #f4f4f4; text-align: left; }
    </style>
  </head>
  <body>
    <h2>Resultado da Aprovação</h2>
    <p>Lote: {{ lot }} | Direção: {{ side }}</p>
    <table>
      <thead>
        <tr>
          <th>Ativo</th>
          <th>Status</th>
          <th>Ticket</th>
          <th>Mensagem</th>
        </tr>
      </thead>
      <tbody>
        {% for r in results %}
        <tr>
          <td>{{ r.symbol }}</td>
          <td>{{ r.status }}</td>
          <td>{{ r.ticket or '-' }}</td>
          <td>{{ r.message or '-' }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>

    <p><a href="{{ url_for('index') }}">Voltar</a></p>
  </body>
</html>
"""


def load_portfolio_report() -> Dict[str, Any]:
    path = ROOT / "reports" / "portfolio_selection.json"
    if not path.exists():
        return {
            "timeframe": "",
            "top_n": 0,
            "only": "",
            "mt5_all": False,
            "selected": [],
            "portfolio": [],
        }
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sort_top(portfolio: List[Dict[str, Any]], k: int = 10) -> List[Dict[str, Any]]:
    # Ordena por decision_engine_score (fallback para normalized_score)
    def score_key(x: Dict[str, Any]):
        de = x.get("decision_engine_score")
        ns = x.get("normalized_score")
        return float(de if de is not None else (ns if ns is not None else 0.0))
    return sorted(portfolio, key=score_key, reverse=True)[:k]


# Instância única do broker
_broker: MT5Broker | None = None


async def ensure_broker() -> MT5Broker:
    global _broker
    if _broker is None:
        # Carregar config.json se existir
        cfg_path = ROOT / "config.json"
        cfg: Dict[str, Any] = {}
        if cfg_path.exists():
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                cfg = {}
        _broker = MT5Broker(config=cfg)
        await _broker.initialize()
    elif not _broker.initialized:
        await _broker.initialize()
    return _broker


@app.route("/")
def index():
    report = load_portfolio_report()
    portfolio = sort_top(report.get("portfolio", []), 10)
    return render_template_string(
        TEMPLATE_INDEX,
        timeframe=report.get("timeframe"),
        top_n=report.get("top_n"),
        only=report.get("only"),
        mt5_all=bool(report.get("mt5_all", False)),
        portfolio=portfolio,
    )


@app.route("/approve", methods=["POST"])
def approve():
    symbols = request.form.getlist("symbol")
    lot = float(request.form.get("lot", "0.10") or 0.10)
    side = request.form.get("side", "buy").strip().lower()

    if not symbols:
        flash("Nenhum ativo selecionado.")
        return redirect(url_for("index"))

    results = []
    try:
        broker = asyncio.run(ensure_broker())
        for sym in symbols:
            try:
                trade = asyncio.run(broker.open_order(symbol=sym, side=side, price=0.0, volume=lot, sl=0.0, tp=0.0))
                status = "executado" if trade and not trade.id.startswith("ERR-") else "erro"
                results.append({
                    "symbol": sym,
                    "status": status,
                    "ticket": trade.id if trade else None,
                    "message": None,
                })
            except Exception as e:
                results.append({
                    "symbol": sym,
                    "status": "erro",
                    "ticket": None,
                    "message": str(e),
                })
    except Exception as e:
        flash(f"Falha geral ao executar ordens: {e}")
        return redirect(url_for("index"))

    return render_template_string(TEMPLATE_RESULTS, results=results, lot=lot, side=side)


if __name__ == "__main__":
    # Execução direta (debug)
    app.run(host="127.0.0.1", port=8501, debug=True)