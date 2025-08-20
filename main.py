import pandas as pd
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

pd.options.display.width = 0
pd.set_option('display.max_columns', 8)
pd.set_option('display.max_rows', None)
file_path = "MNQU25_M30.csv"  # your path

use_every_red_candle = True  # if True, evaluate every red candle even if in a trade


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
    # Iterate through the DataFrame to find trades
    i, n = 1, len(df)

    while i < n:
        prev = df.iloc[i - 1]
        curr = df.iloc[i]

        # red candle then green that breaks previous high
        if (
                prev['close'] < prev['open'] and
                curr['close'] > curr['open'] and
                curr['high'] > prev['high']
        ):

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
            outcome_dollar = None

            # walk forward until stop or a *close* >= 1R
            while j < n:
                candle = df.iloc[j]

                # check if the low is <= stop (stop loss)
                if candle['low'] <= stop:
                    outcome = "loss"
                    exit_price = stop
                    outcome_dollar = (exit_price - entry)*2
                    break

                # check if the close is >= entry + risk (1R)
                if candle['close'] >= entry + risk:
                    outcome = "win"
                    exit_price = candle['close']
                    outcome_dollar = (exit_price - entry)*2
                    break

                j += 1

            trades.append({
                "Market position": "Long",
                "Entry time": f"{curr['date']} {curr['time']}",
                "Exit time": f"{df.iloc[j]['date']} {df.iloc[j]['time']}" if j < n else None,
                "Entry price": entry,
                "stop": stop,
                "Exit price": exit_price,
                "outcome": outcome,
                "Profit": outcome_dollar,
            })

            # Skip to the next red candle while in a trade
            if use_every_red_candle:
                # If we are using every red candle, we don't skip to the next red candle
                i += 1
            else:
                # If we are not using every red candle, we skip it while in a trade
                i = j if outcome is not None else n

        else:
            i += 1

    results = pd.DataFrame(trades)
    results['Entry time'] = pd.to_datetime(results['Entry time'], errors='coerce')
    results['Exit time'] = pd.to_datetime(results['Exit time'], errors='coerce')

    # Save results to CSV
    try:
        results.to_csv("results.csv", index=False)
    except PermissionError as e:
        print()
        print(Fore.RED + Style.DIM + f"NB!!! Error saving results to CSV: {e}".upper())

    print()
    print(results)
    print()
    print(f"Total trades: {len(results)}")

    if not results.empty and 'outcome' in results.columns:
        print(results['outcome'].value_counts())
        print()
        print(f"Sum: ${results['Profit'].sum()}")
    else:
        print("No trades found for these rules.")

    return df, results


backtest(file_path)

