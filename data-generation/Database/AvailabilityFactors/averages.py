import os, sys

import pandas as pd

def main():
    cols = []
    all_cols = []
    for x, y, z in os.walk("."):
        if x != ".":
            all_cols += [x+"/PHOT", x+"/WTON", x+"/WTOF", x+"/HROR"]
            cols.append(x)
    
    df0 = pd.read_csv("./BE/2019.csv")
    bigdf = pd.DataFrame(columns=cols, index=df0.index)
    dfphot = pd.DataFrame(columns=cols, index=df0.index)
    dfwton = pd.DataFrame(columns=cols, index=df0.index)
    dfwtof = pd.DataFrame(columns=cols, index=df0.index)
    dfhror = pd.DataFrame(columns=cols, index=df0.index)

    for x, y, z in os.walk("."):
        if x != ".":
            s = x + os.sep + z[0]
            print("reading: " + s)
            df = pd.read_csv(s)
            dfphot[x+"/PHOT"] = df["PHOT"]
            dfwton[x+"/WTON"] = df["WTON"]
            dfwtof[x+"/WTOF"] = df["WTOF"]
            if "HROR" in df:
                dfhror[x+"/HROR"] = df["HROR"]
    
    # print(dfs["./BE"])
    # PHOT WTOF WTON HROR
    avgphot = dfphot.describe().loc["mean"].dropna()
    avgwton = dfwton.describe().loc["mean"].dropna()
    avgwtof = dfwtof.describe().loc["mean"].dropna()
    avghror = dfhror.describe().loc["mean"].dropna()
    print("PHOT")
    print(avgphot.mean())
    print("WTON")
    print(avgwton.mean())
    print("WTOF")
    print(avgwtof.mean())
    print("HROR")
    print(avghror.mean())

if __name__ == "__main__":
    main()