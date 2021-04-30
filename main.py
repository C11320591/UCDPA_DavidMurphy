#!/usr/bin/env python3

"""
"""
import os
import sys
import argparse
# from collections import Counter

import utils
from utils.f1_website_scraping import *
from exceptions.exceptions import *

PROGRAM_USAGE = """

Please select any of the following options:

Option: "fastest-laps"
Requires:
    1. --year (YYYY) 
    2. --circuit (for example: "Monza")

Option: "year-in-review"
Requires:
    1. --year (YYYY)

"""


def get_fastest_lap_times(year: str, circuit: str):
    """ Return a DataFrame for the fastest laps for a circuit in year.
    """
    if not year or not circuit:
        raise MissingParametersException

    try:
        fastest_lap_url = fetch_race_urls(year, circuit)["FASTEST-LAPS"]
    except RaceDataNotFoundException:
        print("Nothing here.")
        raise

    return utils.generate_dataframe_from_url(fastest_lap_url, index="No")


def year_in_review(year: str):
    """ Generate a graph illustrating the points accumulated
    by each driver in a specified year.
    """
    if not year:
        raise MissingParametersException

    # Get list of race-results urls for year
    base_urls = fetch_base_urls(year)
    race_results_url = "race-results.html"

    number_of_races = len(base_urls)  # This will be the x-axis
    race_number = list(range(1, number_of_races + 1))

    # Configure a graph to plot driver data

    utils.configure_graph(
        title="F1 Results {}".format(year),
        x_label="Round number",
        y_label="Points",
        x_intervals=race_number,
        y_intervals="",
        set_grid=True)

    drivers = {}

    for race in base_urls.values():
        full_url = race + race_results_url

        race_data = utils.generate_dataframe_from_url(full_url)

        for driver in race_data.iterrows():
            driver_name, points = driver[1]["Driver"], driver[1]["PTS"]

            # If this is a drivers first race, add them to the drivers dictionary
            if not driver_name in drivers.keys():
                drivers.update({driver_name: [points]})
                continue

            current_points = drivers[driver_name][-1]
            drivers[driver_name].append(current_points + points)

        # If a driver was not included in this race, append the same points as their previous race.
        not_racing = list(set(drivers.keys()) - set(race_data["Driver"]))
        if not_racing:
            for driver in not_racing:
                drivers[driver].append(drivers[driver][-1])

    # For drivers who did not start the season (eg. reserve drivers), prepend a list of n zeros
    # for the races they did not participate in.
    for driver in drivers:
        if len(drivers[driver]) < number_of_races:
            missed = number_of_races - len(drivers[driver])
            for m in range(missed):
                drivers[driver].insert(0, 0)

    # Plot the data
    for driver, points in drivers.items():
        utils.add_graph_data(race_number, points, driver,
                             ".", is_scatter=False)

    # Export graph
    utils.export_graph("F1 Results {}".format(
        year), "/home/ubuntu/results-{}.png".format(year))


if __name__ == "__main__":

    # Handle arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--option")
    parser.add_argument("--year")
    parser.add_argument("--circuit")
    args = parser.parse_args()

    options = [
        "fastest-laps",
        "year-in-review"
    ]

    if not args.option or args.option not in options:
        sys.exit(PROGRAM_USAGE)

    if args.option == "year-in-review":
        year_in_review(args.year)
