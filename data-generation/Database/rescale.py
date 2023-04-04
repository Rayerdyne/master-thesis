import os

import pandas as pd

PARENT = "PowerPlants"
FILENAME = "JRC_EU_TIMES_ProRes1_2019_NOP2H_STO.csv"

# SCALED_VAR <- SCALING_FACTOR * REFERENCE
REFERENCE = "PowerCapacity"
SCALED_VAR = "STOCapacity"
SCALING_FACTOR = 4

def main():
    for dir in os.listdir(PARENT):
        path = PARENT + os.sep + dir + os.sep + FILENAME
        df = pd.read_csv(path, index_col=0)

        mask = (~df[SCALED_VAR].isna()) & (df["Technology"] == "BATS")
        df.loc[mask, SCALED_VAR] = SCALING_FACTOR * df.loc[mask, REFERENCE]

        # in the process, some "1" will become "1.0" as well
        df.to_csv(path)
        print(f"File {path} rescaled")

def print_ratios():
    for dir in os.listdir(PARENT):
        path = PARENT + os.sep + dir + os.sep + FILENAME
        df = pd.read_csv(path, index_col=0)

        mask = ~df["STOCapacity"].isna()
        df.loc[mask, "Ratio"] = df.loc[mask, "STOCapacity"] / df.loc[mask, "PowerCapacity"]

        print(df.loc[mask, ["PowerCapacity", "STOCapacity", "Ratio"]])


if __name__ == "__main__":
    main()