import numpy as np
import prairielearn as pl
import pandas as pd


def generate(data):
    df = pd.io.parsers.read_csv("breast-cancer-train.dat", header=None)

    df2 = pd.DataFrame(
        [
            {
                "city": "Champaign",
                "job": "Professor",
                "age": 35,
                "time": pd.to_datetime("2022-10-06 12:00"),
            },
            {
                "city": "Sunnyvale",
                "job": "Driver",
                "age": 20,
                "time": pd.to_datetime("2020-05-09 12:00"),
            },
            {
                "city": "Mountain View",
                "job": "Data Scientist",
                "age": np.nan,
                "time": pd.to_datetime("2021-12-14 12:00"),
            },
        ]
    )

    dft = pd.DataFrame(
        {
            # Scalars
            "integer": 1,
            "numeric": 3.14,
            "logical": False,
            "character": "foo",
            # TODO adding in complex numbers won't deserialize correctly, fix this (somehow?)
            # "complex": complex(1, 2),
            # Series
            "numeric-list": pd.Series([1.0] * 3).astype("float32"),
            "integer-list": pd.Series([1] * 3, dtype="int8"),
            # "complex-list": pd.Series(np.array([1, 2, 3]) + np.array([4, 5, 6]) *1j).astype("complex128"),
            "character-list": pd.Series(["hello", "world", "stat"]),
            "logical-list": pd.Series([True, False, True]),
            "character-string-list": pd.Series(["a", "b", "c"], dtype="string"),
            # Time Dependency: https://pandas.pydata.org/docs/user_guide/timeseries.html
            "POSIXct-POSIXt-timestamp": pd.Timestamp("20230102"),
            "POSIXct-POSIXt-date_range": pd.date_range("2023", freq="D", periods=3),
            # The below types can't currently be deserialized  by Pandas
            # "POSIXct-POSIXt-period": pd.period_range("1/1/2011", freq="M", periods=3), # Not supported in rpy2
            # "POSIXct-POSIXt-timedelta": pd.to_timedelta(np.arange(3), unit="s"), # Not supported in rpy2
            # Categorical: https://pandas.pydata.org/docs/user_guide/categorical.html
            "factor": pd.Categorical(["a", "b", "c"], ordered=False),
            "ordered-factor": pd.Categorical(
                ["a", "b", "c"], categories=["a", "b", "c"], ordered=True
            ),
        }
    )

    data["params"]["df"] = pl.to_json(df.head(15))
    data["params"]["df2"] = pl.to_json(df2, df_encoding_version=2)
    data["params"]["dft"] = pl.to_json(dft, df_encoding_version=2)
