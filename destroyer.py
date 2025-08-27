# Meant to destroy huge csv of meteo data
import pandas as pd


def format_date(x):
    return x[:7]


def sort_values(df):
    return df.sort_values(by=["stebejimo_laikas", "stoties_kodas"])


def group_values(df):
    agg_functions = {
        "oro_temp": "mean",
        "juntamoji_temp": "mean",
        "debesuotumas": "mean",
        "slegis_juros_lyg": "mean",
        "santyk_oro_dregme": "mean",
        "kritutliu_kiekis": "sum",
    }

    grouped_df = df.groupby(
        [
            "stoties_kodas",
            "stebejimo_laikas",
            "ilguma",
            "platuma",
        ]
    )

    return grouped_df.aggregate(agg_functions)


df = pd.read_csv(
    "Matavimas.csv", usecols=[6, 7, 8, 9, 10, 11, 15, 16, 17, 18],
    # nrows=100,
)

df["stebejimo_laikas"] = df["stebejimo_laikas"].apply(format_date)

df = group_values(df)

df = df.reset_index()

df = sort_values(df)

df[["month", "year"]] = df["stebejimo_laikas"].str.split("-", n=1, expand=True)

df = df.drop(columns=["stoties_kodas", "stebejimo_laikas"])

# print(df.to_string())
df.to_csv("data/processed_meteo.csv", index=None)
