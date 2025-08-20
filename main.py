import pandas as pd


file_path = "MNQU25_M30.csv"  # Replace with your actual CSV file path


def backtest(path):

    columns_to_use = ['Date', 'Time', 'Open', 'High', 'Low', 'Close']
    df = pd.read_csv(path, usecols=columns_to_use)
    print(df)
    # Ensure column names
    df.columns = [c.lower() for c in df.columns]

    trades = []

    i = 1
    while i < len(df):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]

        # Check red candle followed by green breaking high
        if prev['close'] < prev['open'] and curr['close'] > curr['open'] and curr['high'] > prev['high']:
            entry = prev['high']
            stop = prev['low']
            risk = entry - stop

            outcome = None
            exit_price = None

            # Walk forward until trade resolves
            j = i + 1
            while j < len(df):
                candle = df.iloc[j]

                # Stop hit
                if candle['low'] <= stop:
                    outcome = "loss"
                    exit_price = stop
                    break

                # 1R target closed
                if candle['close'] >= entry + risk:
                    outcome = "win"
                    exit_price = candle['close']
                    break

                j += 1

            trades.append({
                "entry_index": i,
                "entry_price": entry,
                "stop": stop,
                "exit_price": exit_price,
                "outcome": outcome
            })

            # Continue from resolution candle
            i = j
        else:
            i += 1

    results = pd.DataFrame(trades)
    print(results)
    print(f"Total trades: {len(results)}")
    print(results['outcome'].value_counts())

    return df, results


df, results = backtest(file_path)

print(df)