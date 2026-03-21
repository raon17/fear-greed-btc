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

