import pandas as pd


def format_date(x):
    return x[:7]


def group_values(df):
    agg_functions = {
        "stebejimo_laikas": "first",
    }

    grouped_df = df.groupby(
        [
            "stoties_kodas",
        ]
    )

    return grouped_df.aggregate(agg_functions)


df = pd.read_csv(
    "data/Matavimas.csv", usecols=[6, 9],
    # nrows=100,
)

df["stebejimo_laikas"] = df["stebejimo_laikas"].apply(format_date)

df = df.sort_values(by=["stebejimo_laikas", "stoties_kodas"])

df = group_values(df)
df = df.reset_index()

df[["year", "month"]] = df["stebejimo_laikas"].str.split("-", n=1, expand=True)

df = df.drop(columns=["stebejimo_laikas"])

# print(df.to_string())
df.to_csv("data/first_station_mention.csv", index=None)
