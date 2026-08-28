import json
import urllib.request


def get_btc_data():
    url = "https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1"

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "BTC-15M-Bot/1.0"}
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode())

    if data["error"]:
        raise Exception(str(data["error"]))

    result = data["result"]

    pair_key = [key for key in result.keys() if key != "last"][0]

    candles = result[pair_key]

    return candles[-60:]


def ema(values, period):
    if len(values) < period:
        return sum(values) / len(values)

    multiplier = 2 / (period + 1)

    value = sum(values[:period]) / period

    for price in values[period:]:
        value = (price - value) * multiplier + value

    return value


def calculate_rsi(values, period=14):
    if len(values) <= period:
        return 50

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

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


def analyze_btc():
    candles = get_btc_data()

    closes = [float(candle[4]) for candle in candles]
    volumes = [float(candle[6]) for candle in candles]

    if len(closes) < 30:
        raise Exception("No hay suficientes datos de BTC.")

    price = closes[-1]

    ema_5 = ema(closes, 5)
    ema_15 = ema(closes, 15)
    ema_30 = ema(closes, 30)

    rsi = calculate_rsi(closes)

    momentum_5 = (
        (price - closes[-6]) / closes[-6]
    ) * 100

    momentum_15 = (
        (price - closes[-16]) / closes[-16]
    ) * 100

    recent_volume = sum(volumes[-5:]) / 5
    previous_volume = sum(volumes[-20:-5]) / 15

    score = 0

    # Tendencia corta
    if ema_5 > ema_15:
        score += 2
    else:
        score -= 2

    # Tendencia general
    if ema_15 > ema_30:
        score += 2
    else:
        score -= 2

    # Momentum corto
    if momentum_5 > 0:
        score += 2
    else:
        score -= 2

    # Momentum de 15 minutos
    if momentum_15 > 0:
        score += 2
    else:
        score -= 2

    # RSI
    if rsi >= 50:
        score += 1
    else:
        score -= 1

    # Volumen
    if recent_volume > previous_volume:
        if momentum_5 > 0:
            score += 1
        else:
            score -= 1

    if score >= 0:
        return "SUBE"

    return "BAJA"


def main():
    signal = analyze_btc()

    # ESTA ES LA UNICA RESPUESTA DEL BOT
    print(signal)


if __name__ == "__main__":
    main()
