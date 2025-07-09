from flask import Flask, jsonify, request
import numpy as np

app = Flask(__name__)

@app.route("/")
def home():
    return "API da IA Bitcoin rodando com sucesso."

@app.route("/analisar", methods=["GET"])
def analisar():
    try:
        closes_str = request.args.get("closes")
        if not closes_str:
            return jsonify({"erro": "Parâmetro 'closes' não fornecido"}), 400

        closes = [float(x) for x in closes_str.split(",")]

        rsi = calcular_rsi(closes)
        macd = calcular_macd(closes)
        padrao = detectar_padrao_grafico(closes)

        # Sinal baseado em RSI + MACD
        sinal = "⏳ Nenhum sinal claro"
        if rsi < 30 and macd > 0:
            sinal = "✅ Entrada de compra (RSI + MACD)"
        elif rsi > 70 and macd < 0:
            sinal = "❌ Entrada de venda (RSI + MACD)"

        # Reforça sinal com base em padrão gráfico
        if padrao == "Topo Duplo":
            sinal = "❌ Entrada de venda (Topo Duplo detectado)"
        elif padrao == "Fundo Duplo":
            sinal = "✅ Entrada de compra (Fundo Duplo detectado)"
        elif padrao == "Triângulo Ascendente":
            sinal = "✅ Entrada de compra (Triângulo Ascendente)"
        elif padrao == "Triângulo Descendente":
            sinal = "❌ Entrada de venda (Triângulo Descendente)"

        return jsonify({
            "sinal": sinal,
            "rsi": round(rsi, 2),
            "macd": round(macd, 2),
            "padrao": padrao or "Nenhum"
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

def detectar_padrao_grafico(closes):
    if len(closes) < 20:
        return None

    # Topo Duplo
    if closes[-1] < closes[-2] and abs(closes[-2] - closes[-4]) < 1 and closes[-3] < closes[-2]:
        return "Topo Duplo"

    # Fundo Duplo
    if closes[-1] > closes[-2] and abs(closes[-2] - closes[-4]) < 1 and closes[-3] > closes[-2]:
        return "Fundo Duplo"

    # Triângulo Ascendente (simplificado)
    if closes[-1] > closes[-2] > closes[-3] and closes[-4] < closes[-2] and closes[-5] < closes[-3]:
        return "Triângulo Ascendente"

    # Triângulo Descendente (simplificado)
    if closes[-1] < closes[-2] < closes[-3] and closes[-4] > closes[-2] and closes[-5] > closes[-3]:
        return "Triângulo Descendente"

    return None
