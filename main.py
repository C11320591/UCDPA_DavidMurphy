#!/usr/bin/env python3

""" PLACEHOLDER. FILL THIS IN!
"""
import os
import sys
import argparse
import numpy as np

import utils
from utils.f1_website_scraping import *
from exceptions.exceptions import *

PROGRAM_USAGE = """

Please select any of the following options:

Option: "fastest-laps"
Requires:
    1. --years (YYYY) 
    2. --circuit (for example: "Monza")

Option: "year-in-review"
Requires:
    1. --year (YYYY)

Option: ""gained-lost"
Requires:
    1. --year (YYYY)

"""

# Globals
GRAPHS_DIR = utils.fetch_config("GRAPHS_DIR")


def places_gained_lost(year: str):
    """ Identify how many places each driver gained/lost during the races of a year
    """

    drivers = list(utils.generate_dataframe_from_url(
        f"https://www.formula1.com/en/results.html/{year}/drivers.html")["Driver"])

    places = dict()
    base_urls = fetch_base_urls(year)

    for race in base_urls.values():

        # Generate full urls
        starting_grid_url = race + "starting-grid.html"
        race_results_url = race + "race-results.html"

        # Generate dataframes from the tables scrapped using the urls
        start_pos = utils.generate_dataframe_from_url(
            starting_grid_url, index="Driver")
        end_pos = utils.generate_dataframe_from_url(
            race_results_url, index="Driver")

        # Identify race participants from race-results dataframe
        race_participants = list(end_pos.index)

        for driver in drivers:
            if driver not in race_participants:
                continue
            try:
                driver_start_pos = start_pos.index.get_loc(driver)
            except KeyError:  # if driver not in the starting-grid dataframe, put to back of grid
                driver_start_pos = 20

            # Deduce how many places each driver gain/lost
            driver_end_pos = end_pos.index.get_loc(driver)
            diff = driver_start_pos - driver_end_pos
            # Update the value for existing driver places (+/-) - otherwise, add new dict key (driver)

            if driver in places.keys():
                places[driver] += diff
            else:
                places[driver] = diff

    # Sort items using their integer values
    places = dict(
        sorted(places.items(), key=lambda item: item[1], reverse=True))

    # Configure a graph to plot places gained/lost
    utils.configure_graph(
        title=f"Places Gained/Lost in {year}",
        x_label="Round number",
        y_label="Places",
        x_intervals=list(places.values()),
        y_intervals=list(places.values()))

    utils.add_graph_data(places.keys(), places.values(), label="Test", yticks_label=list(
        map(lambda d: d[-3:], places.keys())), barh=True)

    utils.export_graph(
        f"Places Gained/Lost {year}", f"{GRAPHS_DIR}/gained_lost-{year}.png")


def avg_fastest_lap_times(years: list, circuits: list):
    """ Generate a graph to illustrate the average fastest lap for a
    circuit in a range of years
    """
    if not years or not circuits:
        raise MissingParametersException

    # Configure a graph to plot driver data
    utils.configure_graph(
        title="Average Fastest Laps",
        x_label="Year",
        y_label="Time (μs)",
        x_intervals=years,
        set_grid=False)

    for circuit in circuits:

        yearly_avg = dict()
        for year in sorted(years):
            try:
                fastest_lap_url = fetch_race_urls(
                    year, circuit)["FASTEST-LAPS"]
            except RaceDataNotFoundException:
                continue

            df = utils.generate_dataframe_from_url(fastest_lap_url, index="No")
            lap_times_str = list(df["Time"])

            # Convert the time str into microseconds int for the purpose of averaging
            avg_fastest_lap = utils.get_average(
                list(map(lambda d: utils.convert_milliseconds(d), lap_times_str)))

            yearly_avg[int(year)] = avg_fastest_lap

        if not yearly_avg:
            # sys.exit("No races found. Verify params: year={} circuit={}".format(year, circuit))
            continue

        # return yearly_avg
        x = list(yearly_avg.keys())
        y = list(map(lambda d: d[1], yearly_avg.values()))
        labels = list(map(lambda d: d[0], yearly_avg.values()))

        # return x, y, labels
        utils.add_graph_data(x, y, label=circuit, marker=".")

    # Export graph
    utils.export_graph("Average Fastest Laps",
                       "/{}/fl-test.png".format(GRAPHS_DIR), use_legend=True)


def constructors_season(year: str, highlighted_team: str = None):
    """ Using some CSVs documents, generate graphs to illustrate
    constructors championship in a specified year
    """
    if not year:
        raise MissingParametersException

    documents = utils.csv_documents()
    race_results = dict()

    races_df = utils.generate_dataframe_from_csv(documents["RACES"])
    race_ids = list(races_df.loc[races_df["year"] == int(year)]["raceId"])

    constructors_df = utils.generate_dataframe_from_csv(
        documents["CONSTRUCTORS"])

    constructors_results_df = utils.generate_dataframe_from_csv(
        documents["CONSTRUCTOR_RESULTS"])
    results_in_year = constructors_results_df[constructors_results_df.raceId.isin(
        race_ids)]
    constructor_ids = set(results_in_year["constructorId"])
    full_df = utils.join_dataframes(
        [constructors_df, results_in_year], key="constructorId")

    for constructor in constructor_ids:
        constructor_name = constructors_df.loc[constructors_df["constructorId"] == constructor]["name"].item(
        )
        constructor_points = list(
            full_df.loc[full_df.index == constructor]["points"])
        race_results[constructor_name] = constructor_points

    utils.configure_graph(
        title="Constructors Championship {}".format(year),
        x_label="Race Number",
        y_label="Points",
        x_intervals=list(range(1, len(race_ids) + 1)),
        set_grid=False)

    for constructor, points in race_results.items():
        color = "orange" if highlighted_team == constructor else "grey"
        utils.add_graph_data(race_ids, points, color=color,
                             label=constructor, marker=".")

    # Export graph
    utils.export_graph("Constructors Championship {}".format(year),
                       "/{}/constructors_h2h-{}.png".format(GRAPHS_DIR, year), use_legend=True)

    race_results_accum = dict()
    for team, points in race_results.items():
        race_results_accum[team] = list(np.cumsum(points))

    # Graph the constructors season for this year
    # Configure a graph to plot driver data
    utils.configure_graph(
        title="Constructors Championship {}".format(year),
        x_label="Race Number",
        y_label="Points",
        x_intervals=list(range(1, len(race_ids) + 1)),
        set_grid=False)

    for constructor, points in race_results_accum.items():
        color = "orange" if highlighted_team == constructor else "grey"
        utils.add_graph_data(race_ids, points, color=color,
                             label=constructor, marker=".")

    # Export graph
    utils.export_graph("Constructors Championship {}".format(year),
                       "/{}/constructors-{}.png".format(GRAPHS_DIR, year), use_legend=True)


def drivers_season(year: str):
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

    drivers = {}

    for race in base_urls.values():
        full_url = race + race_results_url

        race_data = utils.generate_dataframe_from_url(full_url)

        for driver in race_data.iterrows():
            driver_name, points = driver[1]["Driver"], driver[1]["PTS"]

            # If this is a drivers first race, add them to drivers
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

    # Configure a graph to plot driver data
    utils.configure_graph(
        title="F1 Results {}".format(year),
        x_label="Round number",
        y_label="Points",
        x_intervals=race_number,
        y_intervals="",
        set_grid=False)

    # Plot a line for each driver that participated in the season
    for driver, points in drivers.items():
        utils.add_graph_data(race_number, points, driver,
                             ".", is_scatter=False)

    # Export graph
    utils.export_graph("F1 Results {}".format(
        year), "/{}/results-{}.png".format(GRAPHS_DIR, year), use_legend=True)


if __name__ == "__main__":

    # Handle arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option")
    parser.add_argument("-y", "--year")
    parser.add_argument("--team")
    parser.add_argument("--circuit")
    args = parser.parse_args()

    options = [
        "fastest-laps",
        "year-in-review",
        "constructors-year",
        "gained-lost"
    ]

    if not args.option or args.option not in options:
        sys.exit(PROGRAM_USAGE)

    if args.option == "year-in-review":
        drivers_season(args.year)

    if args.option == "gained-lost":
        places_gained_lost(args.year)

    if args.option == "constructors-year":
        team = args.team if args.team else None
        constructors_season(args.year, highlighted_team=team)

    if args.option == "fastest-laps":
        start, end = args.year.split("-")
        circuits = ["Monza", "Silverstone",
                    "Monaco", "Spielberg", "Marina Bay"]

        avg_fastest_lap_times(years=list(
            range(int(start), int(end))), circuits=circuits)
