from urllib.request import Request, urlopen
import pandas as pd
import datetime

from helpers.is_date import is_date
from helpers.normalize_date import normalize_date
from helpers.save_indicator import save_indicator
from helpers.normalize_country import normalize_country

dataset_url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"

req = Request(dataset_url)
req.add_header(
    "User-Agent",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0",
)
content = urlopen(req)

# Parse into dataframe
dataset = pd.read_csv(content, low_memory=False)

# Drop non-countries (e.g., world regions)
dataset = dataset.dropna(subset=["iso_code"])
dataset = dataset.drop(dataset[dataset.iso_code.isin(["OWID_KOS", "OWID_WRL"])].index)

# Normalize date format
dataset["date"] = dataset["date"].apply(lambda date: normalize_date(date, "%Y-%m-%d"))


def run_pipeline(indicator):
    # Get the column name for this indicator
    column = indicator.replace("owid_", "", 1)

    # Create slice of data with country ID, date, and indicator
    frame = dataset[["iso_code", "date", column]]

    # Rename column to indicator
    frame = frame.rename(columns={column: indicator})

    # Drop rows without observation
    frame = frame.dropna(subset=[indicator], axis="index")

    # Save as CSV file
    save_indicator(indicator, dataset=frame)
