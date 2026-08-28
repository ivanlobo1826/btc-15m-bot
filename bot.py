import json
import urllib.request
from datetime import datetime, timezone

# ==========================================
# BTC 15M SIGNAL BOT
# Solo devuelve: SUBE o BAJA
# ==========================================

def get_btc_data():
    url = (
        "https://api.binance.com/api/v3/klines"
        "?symbol=BTCUSDT&interval=1m&limit=60"
    )

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "BTC-15M-Bot"}
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode())


def ema(values, period):
    multiplier = 2 / (period + 1)
    result = values[0]

    for price in values[1:]:
        result = (price - result) * multiplier + result

    return result


def rsi(values, period=14):
    gains = []
    losses = []

    for i in range(1, len(values)):
        change = values[i] - values[i - 1]

        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    if len(gains) < period:
        return 50

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def analyze():
    candles = get_btc_data()

    closes = [float(candle[4]) for candle in candles]
    volumes = [float(candle[5]) for candle in candles]

    current_price = closes[-1]

    # Tendencias
    ema_5 = ema(closes[-5:], 5)
    ema_15 = ema(closes[-15:], 15)
    ema_30 = ema(closes[-30:], 30)

    # RSI
    current_rsi = rsi(closes)

    # Momentum
    momentum_5 = ((closes[-1] - closes[-6]) / closes[-6]) * 100
    momentum_15 = ((closes[-1] - closes[-16]) / closes[-16]) * 100

    # Volumen
    recent_volume = sum(volumes[-5:]) / 5
    old_volume = sum(volumes[-20:-5]) / 15

    score = 0

    # EMA
    if ema_5 > ema_15:
        score += 2
    else:
        score -= 2

    if ema_15 > ema_30:
        score += 2
    else:
        score -= 2

    # Momentum
    if momentum_5 > 0:
        score += 2
    else:
        score -= 2

    if momentum_15 > 0:
        score += 2
    else:
        score -= 2

    # RSI
    if current_rsi > 50:
        score += 1
    else:
        score -= 1

    # Volumen
    if recent_volume > old_volume:
        if momentum_5 > 0:
            score += 1
        else:
            score -= 1

    # Decisión final
    if score >= 0:
        signal = "SUBE"
    else:
        signal = "BAJA"

    return signal


def main():
    signal = analyze()

    # ÚNICO DATO QUE ENTREGA EL BOT
    print(signal)


if __name__ == "__main__":
    main()
