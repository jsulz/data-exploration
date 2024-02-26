import pandas as pd
import numpy as np
from dateutil import tz


def drop_unnecessary_SVTs(df):
    svts = ["HOOK", "TRAILER", "TEASER_TRAILER"]
    for svt in svts:
        df = df[df["Supplemental Video Type"] != svt]

    return df


def transform_duration(df, column_name):
    duration = df[column_name].str.split(":", expand=True)
    for column in range(duration.shape[1]):
        duration[column] = pd.to_numeric(duration[column])

    duration = duration[0] + duration[1] / 60 + duration[2] / 3600

    df[column_name] = duration

    return df


def drop_columns(df, columns):
    df = df.drop(columns, axis=1)
    return df


def swap_duration(df):
    # print(df["Duration"].sum())
    df["Duration"] = np.where(
        df["Duration"] > df["Bookmark"], df["Bookmark"], df["Duration"]
    )
    # print(df["Duration"].sum())
    return df


def expand_title(df):
    expanded_titles = df["Title"].copy()
    expanded_titles = pd.DataFrame(
        np.where(
            expanded_titles.str.contains("Season \\d") == False, "0", expanded_titles
        )
    )
    expanded_titles.rename(columns={0: "Title"}, inplace=True)
    # print(expanded_titles.head(20))
    expanded_titles = expanded_titles["Title"].str.split(
        "(Season \\d:)", regex=True, expand=True
    )
    # print(expanded_titles.head(30))
    expanded_titles[0] = np.where(
        expanded_titles[0] == "0", df["Title"], expanded_titles[0]
    )
    # print(expanded_titles.head(40))

    column_titles = {}
    for column in range(expanded_titles.shape[1]):
        column_titles[column] = f"Title_{column}"
        expanded_titles[column] = expanded_titles[column].str.strip()
        expanded_titles[column] = np.where(
            expanded_titles[column].str.endswith(":"),
            expanded_titles[column].str.rstrip(to_strip=":"),
            expanded_titles[column],
        )
    expanded_titles.rename(columns=column_titles, inplace=True)
    # print(expanded_titles.head(40))
    df = df.join(expanded_titles)
    return df


def set_time_columns(df):
    time_column = pd.DataFrame(pd.to_datetime(df["Start Time"], utc=True))
    pst = tz.gettz("America/Los_Angeles")
    time_column = time_column["Start Time"].dt.tz_convert(pst)
    time_column.rename("PST Start Time", inplace=True)
    df = df.join(time_column)
    df["Month"] = df["PST Start Time"].dt.month
    df["Day"] = df["PST Start Time"].dt.dayofweek
    df["Year"] = df["PST Start Time"].dt.year
    return df


if __name__ == "__main__":
    df = pd.read_csv("../data/netflix_data.csv")
    # print(df.shape)

    df = drop_unnecessary_SVTs(df)
    # print(df.shape)

    df = transform_duration(df, "Duration")
    # print(df.shape)
    # print(df.head(20))

    df = transform_duration(df, "Bookmark")
    # print(df.shape)
    # print(df.head(20))

    df = swap_duration(df)
    # print(df.shape)
    # print(df.head(20))

    df = drop_columns(
        df, ["Profile Name", "Supplemental Video Type", "Latest Bookmark"]
    )
    # print(df.shape)

    df = expand_title(df)
    # print(df.head(30))

    df = set_time_columns(df)
    df.to_csv("../data/netflix_cleaned_data.csv", index=False)
    # df.to_json("../data/netflix_cleaned_data.json")
