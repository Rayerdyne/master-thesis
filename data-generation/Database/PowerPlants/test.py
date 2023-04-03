import os

import pandas as pd

def main():
    dirs = os.listdir(".")
    # dirs = ["BE", "DE"]
    fname = "JRC_EU_TIMES_ProRes1_2019_NOP2H_STO.csv"
    for dir in dirs:
        if dir.endswith(".py"):
            break
        path = dir + os.sep + fname
        df = pd.read_csv(path)
        bats = df[df["Technology"] == "BATS"]
        print(f"[{dir}] -> {path}")
        print( bats.STOCapacity / bats.PowerCapacity )

        

if __name__ == "__main__":
    main()