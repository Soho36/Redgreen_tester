import pandas as pd

file_path = "MNQU25_M30.csv"  # your path


def backtest(path):
    columns_to_use = ['<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>']

    df = pd.read_csv(path, sep="\t", usecols=columns_to_use)

    # Standardize columns
    df = df.rename(columns={
        '<DATE>': 'date',
        '<TIME>': 'time',
        '<OPEN>': 'open',
        '<HIGH>': 'high',
        '<LOW>': 'low',
        '<CLOSE>': 'close',
    })

    # Ensure numeric OHLC
    for c in ['open', 'high', 'low', 'close']:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    trades = []
    i, n = 1, len(df)

    while i < n:
        prev = df.iloc[i - 1]
        curr = df.iloc[i]

        # red candle then green that breaks previous high
        if (prev['close'] < prev['open'] and
            curr['close'] > curr['open'] and
            curr['high'] > prev['high']):

            # Entry at the red candle's high (stop order logic).
            # If you want to account for gaps, consider: entry = max(prev['high'], curr['open'])
            entry = prev['high']
            stop = prev['low']
            risk = entry - stop

            if pd.isna(risk) or risk <= 0:
                i += 1
                continue

            j = i + 1
            outcome = None
            exit_price = None

            # walk forward until stop or a *close* >= 1R
            while j < n:
                candle = df.iloc[j]

                if candle['low'] <= stop:
                    outcome = "loss"
                    exit_price = stop
                    break

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

            # jump to resolution candle (or end if unresolved)
            i = j if outcome is not None else n
        else:
            i += 1

    results = pd.DataFrame(trades)
    print(results)
    print(f"Total trades: {len(results)}")
    if not results.empty and 'outcome' in results.columns:
        print(results['outcome'].value_counts())
    else:
        print("No trades found for these rules.")

    return df, results


df, results = backtest(file_path)
print(df)
