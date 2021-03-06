import os
import pandas
from time import localtime, strftime

from config import INDICATOR_FOLDER
from helpers.save_indicator import save_indicator


def generate_classification(row):
    positive_rate = row["positive_rate_smoothed"]
    new_cases_per_million = row["new_cases_per_million_smoothed"]

    # We make an exception for China, as requested by Jeffrey Sachs:
    # And for China, we know the incidence is so low and the testing so
    # extensive whenever there is an outbreak (comprehensive testing, for
    # example, in Beijing and Wuhan after small outbreaks) that China should be
    # classified as having sufficient testing, so just based on new cases.
    if row["iso_code"] == "CHN":
        positive_rate = 0.01

    # Whether the country has testing data
    has_test_data = not pandas.isna(positive_rate)

    # If new_cases_per_million are missing, set no classification
    if pandas.isna(new_cases_per_million):
        return None

    # Suppression
    if (new_cases_per_million <= 5) and (positive_rate <= 0.05):
        return 1

    # Low
    if new_cases_per_million <= 10 and has_test_data:
        return 2

    # Moderate
    if new_cases_per_million <= 50 and has_test_data:
        return 3

    # High
    if new_cases_per_million <= 100 and has_test_data:
        return 4

    # Very high if a lot of new cases per million, even if no test data
    if new_cases_per_million > 100:
        return 5


def run_pipeline(indicator):
    # Get smoothed new cases per million
    new_cases_per_million_path = os.path.join(
        INDICATOR_FOLDER, "sdsn_new_cases_per_million_smoothed.csv"
    )
    new_cases_per_million = pandas.read_csv(new_cases_per_million_path)
    new_cases_per_million.rename(
        columns={
            "sdsn_new_cases_per_million_smoothed": "new_cases_per_million_smoothed"
        },
        inplace=True,
    )

    # Get smoothed positive rate
    positive_rate_path = os.path.join(
        INDICATOR_FOLDER, "sdsn_positive_test_rate_smoothed.csv"
    )
    positive_rate = pandas.read_csv(positive_rate_path)
    positive_rate.rename(
        columns={"sdsn_positive_test_rate_smoothed": "positive_rate_smoothed"},
        inplace=True,
    )

    # Merge datasets
    dataset = pandas.merge(
        new_cases_per_million,
        positive_rate,
        how="outer",
        on=["iso_code", "country", "date"],
    )

    # Generate classification
    dataset[indicator] = dataset.apply(generate_classification, axis=1)

    # Drop country name
    dataset = dataset[["iso_code", "date", indicator]]

    # Drop rows without classification
    dataset = dataset.dropna(subset=[indicator], axis="index")

    # Save as CSV file
    save_indicator(indicator, dataset=dataset)
