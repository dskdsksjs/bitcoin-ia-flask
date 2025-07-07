from flask import Flask, jsonify, request
import numpy as np

app = Flask(__name__)

@app.route("/")
def home():
    return "API da IA Bitcoin rodando com sucesso."

@app.route("/analisar", methods=["GET"])
def analisar():
    try:
        closes = request.args.get("closes")
        if not closes:
            return jsonify({"erro": "Parâmetro 'closes' não fornecido"}), 400

        closes = [float(x) for x in closes.split(",")]

        rsi = calcular_rsi(closes)
        macd = calcular_macd(closes)

        sinal = "⏳ Nenhum sinal claro"
        if rsi < 30 and macd > 0:
            sinal = "✅ Entrada de compra"
        elif rsi > 70 and macd < 0:
            sinal = "❌ Entrada de venda"

        return jsonify({
            "sinal": sinal,
            "rsi": round(rsi, 2),
            "macd": round(macd, 2)
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def calcular_rsi(closes, periodo=14):
    ganhos = []
    perdas = []
    for i in range(1, periodo + 1):
        delta = closes[-i] - closes[-i - 1]
        if delta >= 0:
            ganhos.append(delta)
        else:
            perdas.append(-delta)
    media_ganhos = np.mean(ganhos)
    media_perdas = np.mean(perdas)
    rs = media_ganhos / media_perdas if media_perdas != 0 else 100
    return 100 - (100 / (1 + rs))

def calcular_ema(closes, periodo):
    k = 2 / (periodo + 1)
    ema = closes[0]
    for preco in closes[1:]:
        ema = preco * k + ema * (1 - k)
    return ema

def calcular_macd(closes):
    ema12 = calcular_ema(closes[-26:], 12)
    ema26 = calcular_ema(closes[-26:], 26)
    return ema12 - ema26
