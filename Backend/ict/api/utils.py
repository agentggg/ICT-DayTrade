def detect_fvg_from_array(c):
    """
    c must be 3 candles:
    c[0] → first
    c[1] → middle
    c[2] → last
    """

    # Unpack
    c0, c1, c2 = c

    # Validate structure
    for k in ("high", "low"):
        if k not in c0 or k not in c1 or k not in c2:
            raise Exception("Candles missing high/low values")

    # BULLISH FVG:
    # c0.high < c2.low AND middle candle has a gap
    if c0["high"] < c2["low"]:
        return {
            "type": "bullish",
            "gap_high": c2["low"],
            "gap_low": c0["high"],
        }

    # BEARISH FVG:
    # c0.low > c2.high
    if c0["low"] > c2["high"]:
        return {
            "type": "bearish",
            "gap_high": c0["low"],
            "gap_low": c2["high"],
        }

    return None

def is_bullish(c):
    return c["close"] > c["open"]

def is_bearish(c):
    return c["close"] < c["open"]

def body_ratio(c):
    body = abs(c["close"] - c["open"])
    wick_total = c["high"] - c["low"]
    if wick_total == 0:
        return 0
    return body / wick_total

def detect_displacement(prev, curr, direction):
    """
    Basic ICT displacement check:
    - Bullish: strong up candle breaking previous structure
    - Bearish: strong down candle breaking previous structure
    """
    if direction == "bullish":
        return curr["high"] > prev["high"] and is_bullish(curr)
    else:
        return curr["low"] < prev["low"] and is_bearish(curr)

def find_order_blocks(
    candles,
    direction="bullish",
    require_displacement=True,
    min_body_ratio=0.45,
    mss_lookback=3,
    ob_lookback=4,
    min_ob_body=0.25,
):
    """
    ICT-Style Order Block Identification

    Returns a list of:
    {
        "direction": "bullish" | "bearish",
        "ob": {
            "time": ...,
            "high": ...,
            "low": ...
        }
    }
    """

    matches = []

    n = len(candles)
    if n < 5:
        return []

    for i in range(2, n):  # start from 2 to allow lookbacks
        prev = candles[i - 1]
        curr = candles[i]

        # 1️⃣ Check displacement
        if require_displacement and not detect_displacement(prev, curr, direction):
            continue

        # 2️⃣ MSS check: look back mss_lookback candles
        if direction == "bullish":
            mss = any(candles[i]["high"] > candles[i - k]["high"]
                      for k in range(1, min(mss_lookback + 1, i)))
        else:
            mss = any(candles[i]["low"] < candles[i - k]["low"]
                      for k in range(1, min(mss_lookback + 1, i)))

        if not mss:
            continue

        # 3️⃣ Identify the OB candle (last opposite candle before displacement)
        start = max(0, i - ob_lookback)
        ob_candidates = candles[start:i]

        if direction == "bullish":
            # OB = last bearish candle before displacement
            pool = [c for c in ob_candidates if is_bearish(c)]
        else:
            # OB = last bullish candle before displacement
            pool = [c for c in ob_candidates if is_bullish(c)]

        if not pool:
            continue

        ob = pool[-1]  # last valid opposite candle (ICT rule)

        # 4️⃣ Ensure OB body strength
        if body_ratio(ob) < min_ob_body:
            continue

        matches.append({
            "direction": direction,
            "ob": {
                "time": ob["time"],
                "high": ob["high"],
                "low": ob["low"]
            }
        })

    return matches