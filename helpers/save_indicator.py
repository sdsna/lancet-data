import pandas
import os
from config import INDICATOR_FOLDER

codelist = pandas.read_csv("helpers/codelist.csv")
codelist = codelist[["iso3c", "country.name.en"]]
codelist = codelist.rename(columns={"iso3c": "iso_code", "country.name.en": "country"})

# Save the dataframe under the given name
def save_indicator(name, dataset):
    # Add country name
    dataset = pandas.merge(dataset, codelist, how="left", on=["iso_code"])

    # Re-order columns
    dataset = dataset[["iso_code", "country", "date", name]]

    # Sort by country ID, then date
    dataset = dataset.sort_values(by=["iso_code", "date"])

    # Verify there are no empty countries or dates
    nulls = dataset[["iso_code", "date"]].isnull()
    if nulls.any(axis=None):
        raise Exception("Null values for country/date detected")

    # Verify that there are no duplicate entries for country and date
    if dataset.duplicated(["iso_code", "date"]).any(axis=None):
        duplicates = dataset.duplicated(["iso_code", "date"])
        print(dataset[duplicates])
        raise Exception("Duplicate country-date in data detected")

    # Verify that there are no empty observations
    if dataset[name].isnull().any(axis=None):
        raise Exception("Empty observations in data detected")

    # Save
    file_name = os.path.join(INDICATOR_FOLDER, name + ".csv")
    dataset.to_csv(file_name, index=False)
