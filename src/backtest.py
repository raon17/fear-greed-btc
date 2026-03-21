import pandas as pd
from scipy import stats

def zone_stats(df, horizon=30):
    col = f"fwd_{horizon}d_pct"
    clean = df.dropna(subset=[col]) # Only keep rows where we have a valid forward return for the given horizon

    results = []

    for zone, grp in clean.groupby("zone", observed=True) : # .groupyby to calculate stats for each zone. observed=True to only include zones that actually appear in the data
        results.append({
            "zone":           str(zone),
            "n":              len(grp),
            "avg_return":     round(grp[col].mean(), 2),
            "median_return":  round(grp[col].median(), 2),
            "win_rate":       round((grp[col] > 0).mean() * 100, 1) # % days when return was positive, grp[col] > 0 gives a boolean series where True=1 and False=0, so mean() gives the proportion of True values
        })

    return pd.DataFrame(results)

def threshold_backtest(df, threshold=25, horizon=30):
    col = f"fwd_{horizon}d_pct"
 
    # Signal: only days where F&G was below the threshold
    signal = df[df["value"] < threshold].dropna(subset=[col])
 
    # Buy-and-hold benchmark: every day with valid forward return data
    bah = df.dropna(subset=[col])
 
    return {
        "threshold":          threshold,
        "signal_trades":      len(signal),
        "signal_avg_return":  round(signal[col].mean(), 2),
        "signal_win_rate":    round((signal[col] > 0).mean() * 100, 1),
        "bah_avg_return":     round(bah[col].mean(), 2),
        "bah_win_rate":       round((bah[col] > 0).mean() * 100, 1),
    }
 
def significance_test(df, threshold=25, horizon=30):
    col = f"fwd_{horizon}d_pct"
 
    fear  = df[df["value"] < threshold][col].dropna()
    other = df[df["value"] >= threshold][col].dropna()

    t_stat, p_value = stats.ttest_ind(fear, other)  # Independent samples t-test
 
    return {
        "t_stat":      round(t_stat, 3),
        "p_value":     round(p_value, 4),
        "significant": p_value < 0.05,
        "fear_n":      len(fear),
        "other_n":     len(other),
    }
 