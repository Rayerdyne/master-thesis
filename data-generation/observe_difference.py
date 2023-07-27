import matplotlib.pyplot as plt
import pandas as pd

PATH = "../nn/data/dataset-real.csv"

def do_boxplot(oks, errors, f):
    data = [oks[f], errors[f]]
    fig, ax = plt.subplots()
    ax.boxplot(data)
    ax.set_title(f"{f} distribution")
    ax.set_ylabel(f)
    ax.set_xticklabels(["Successful simulations", "Unsuccessful simulations"])
    plt.show()

def main():
    df = pd.read_csv(PATH)

    okmask = df["GAMS_error"] != 2
    komask = df["GAMS_error"] == 2

    print("Number of simulations: ", len(df.index))
    errors = df.loc[komask]
    oks = df.loc[okmask]
    features = ["CapacityRatio", "ShareFlex" , "ShareStorage", "ShareWind", "SharePV", "rNTC"]

    # for f in features:
        # do_boxplot(oks, errors, f)
    do_boxplot(oks, errors, "ShareFlex")

    descerr = errors.describe()
    descok  = oks.describe()

    print("[error 2] mean(errors) - mean(oks):    (" + str(len(errors.index)) + ")")
    print((descerr[features] - descok[features]).loc["mean"])
    print(descerr[features])
    print(descok[features])
    print("-" * 80)

    okmask = df["GAMS_error"] != 1
    komask = df["GAMS_error"] == 1

    errors = df.loc[komask]
    oks = df.loc[okmask]
    features = ["CapacityRatio", "ShareFlex" , "ShareStorage", "ShareWind", "SharePV", "rNTC"]

    # for f in features:
    #     do_boxplot(oks, errors, f)
    do_boxplot(oks, errors, "rNTC")

    descerr = errors.describe()
    descok  = oks.describe()

    print("[error 1] mean(errors) - mean(oks):    (" + str(len(errors.index)) + ")")
    print((descerr[features] - descok[features]).loc["mean"])
    print(descerr[features])
    print(descok[features])


if __name__ == "__main__":
    main()