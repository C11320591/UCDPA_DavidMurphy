#!/usr/bin/env python3

"""
"""
import os
import sys
import argparse

import utils  # utils/__init__.py
from utils.f1_website_scraping import *


def get_average_track_fl_times(year: str, circuit: str):
    """ Get the average fastest lap time for a circuit in a specified year
    """
    try:
        fastest_lap_url = fetch_race_urls(year, circuit)["FASTEST-LAPS"]
    except RaceDataNotFound:
        print("Nothing here.")
        raise

    df = utils.generate_dataframe_from_url(fastest_lap_url, index="No")

    lap_times_ms = list(map(utils.convert_milliseconds, list(df["Time"])))

    average_lap_time = sum(lap_times_ms) / len(lap_times_ms)

    return {year: [utils.convert_milliseconds(average_lap_time), str(average_lap_time)]}


def main():
    """
    """
    print("START_HERE")
    parser = argparse.ArgumentParser()
    parser.add_argument("option")
    parser.add_argument("year")
    # parser.add_argument("circuit")
    # parser.add_argument("driver")
    # parser.add_argument("team")
    args = parser.parse_args()


if __name__ == "__main__":
    main()
