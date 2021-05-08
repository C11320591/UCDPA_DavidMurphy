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


def fastest_lap_times(year: str, highlighted_driver: str = None):
    """ Scrap the Formula 1 website to generate a graph to
    illustrate the average fastest in year
    """
    if not year:
        raise MissingParametersException

    if int(year) < 2004:
        sys.exit("No race data for {} before 2004".format(year))
        # TODO: Use web scraping to get data for years prior to 2004

    race_ids, full_df = fetch_year_data("LAPS", year)

    if highlighted_driver:
        highlighted_driver_times = dict()

    fastest_laps = dict()
    for race in race_ids:
        data = full_df.loc[full_df["raceId"] == race][[
            "code", "fastestLapTime"]].to_dict()

        drivers = list(data["code"].values())
        lap_times = list(data["fastestLapTime"].values())
        try:
            fastest_laps[race] = utils.get_average(lap_times)[-1]
        except ZeroDivisionError:
            print("No lap times recorded for RaceId {} in year {}".format(race, year))
            continue

        if highlighted_driver and highlighted_driver.upper() in drivers:
            highlighted_driver_index = drivers.index(
                highlighted_driver.upper())
            driver_lap_time = utils.convert_milliseconds(
                lap_times[highlighted_driver_index])
            highlighted_driver_times[race] = driver_lap_time

    number_races = list(range(1, len(race_ids) + 1))
    utils.configure_graph(
        title="Avg. Fastest Lap {}".format(year),
        x_label="Race Number",
        y_label="Time (μs)",
        x_intervals=number_races,
        set_grid=False)

    utils.add_graph_data(fastest_laps.keys(), fastest_laps.values(
    ), color="grey", label="avg", marker=".")

    if highlighted_driver:
        for race, time in highlighted_driver_times.items():
            if not time:
                continue
            utils.add_graph_data([race], [time], marker="x",
                                 color="red", is_scatter=True)

    # Export graph
    utils.export_graph("Avg. Fastest Lap {}".format(year),
                       "/{}/avg_fastest_laps-{}.png".format(GRAPHS_DIR, year), use_legend=True)


def fetch_year_data(entity: str, year: int):
    """ FILL THIS IN!
    """
    documents = utils.csv_documents()
    races_df = utils.generate_dataframe_from_csv(documents["RACES"])
    race_ids = list(races_df.loc[races_df["year"] == int(year)]["raceId"])

    results_df = utils.generate_dataframe_from_csv(documents["RESULTS"])

    if entity.upper() == "LAPS":
        drivers_df = utils.generate_dataframe_from_csv(documents["DRIVERS"])[
            ["driverId", "code", "surname"]]
        # Pull rows in drivers where code = "\N" and use surname as code
        for driver, values in drivers_df.iterrows():
            id,  code, surname = values[["driverId", "code", "surname"]]
            if code == "\\N":
                drivers_df.loc[drivers_df["driverId"] == id, ["code"]] = surname.replace(" ", "")[
                    :3].upper()

        full_df = utils.join_dataframes(
            [results_df, drivers_df], key="driverId")

        full_df.sort_values(by=["raceId"], inplace=True)

        return race_ids, full_df

    if entity.upper() == "DRIVER":
        drivers_df = utils.generate_dataframe_from_csv(
            documents["DRIVERS"])[["driverId", "code"]]
        # Pull rows in drivers where code = "\N" and use surname as code
        for driver, values in drivers_df.iterrows():
            id,  code, surname = values[["driverId", "code", "surname"]]
            if code == "\\N":
                drivers_df.loc[drivers_df["driverId"] == id, ["code"]] = surname.replace(" ", "")[
                    :3].upper()

        full_df = utils.join_dataframes(
            [results_df, drivers_df], key="driverId")

        return race_ids, full_df

    if entity.upper() in ["CONSTRUCTOR", "TEAM"]:
        constructors_df = utils.generate_dataframe_from_csv(
            documents["CONSTRUCTORS"])
        constructors_results_df = utils.generate_dataframe_from_csv(
            documents["CONSTRUCTOR_RESULTS"])
        results_in_year = constructors_results_df[constructors_results_df.raceId.isin(
            race_ids)]
        constructor_ids = set(results_in_year["constructorId"])
        full_df = utils.join_dataframes(
            [constructors_df, results_in_year], key="constructorId")

        return race_ids, constructor_ids, constructors_df, full_df


def constructors_season(year: str, highlighted_team: str = None):
    """ Using some CSVs documents, generate graphs to illustrate
    constructors championship in a specified year
    """
    if not year:
        raise MissingParametersException

    race_ids, constructor_ids, constructors_df, full_df = fetch_year_data(
        "CONSTRUCTOR", year)
    race_results = dict()

    for constructor in constructor_ids:
        constructor_name = constructors_df.loc[constructors_df["constructorId"] == constructor]["name"].item(
        )
        constructor_points = list(
            full_df.loc[full_df.index == constructor]["points"])
        race_results[constructor_name] = constructor_points

    number_races = list(range(1, len(race_ids) + 1))

    utils.configure_graph(
        title="Constructors Championship {}".format(year),
        x_label="Race Number",
        y_label="Points",
        x_intervals=number_races,
        set_grid=False)

    for constructor, points in race_results.items():
        color = "grey"
        if highlighted_team and highlighted_team.upper() == constructor.upper():
            color = "orange"
        utils.add_graph_data(race_ids, points, color=color,
                             label=constructor, marker=".")

    # Export graph
    utils.export_graph("Constructors Championship {}".format(year),
                       "/{}/constructors_championship_h2h-{}.png".format(GRAPHS_DIR, year), use_legend=True)

    race_results_accum = dict()
    for team, points in race_results.items():
        race_results_accum[team] = list(np.cumsum(points))

    # Graph the constructors season for this year
    # Configure a graph to plot driver data
    utils.configure_graph(
        title="Constructors Championship {}".format(year),
        x_label="Race Number",
        y_label="Points",
        x_intervals=number_races,
        set_grid=False)

    for constructor, points in race_results_accum.items():
        color = "grey"
        if highlighted_team and highlighted_team.upper() == constructor.upper():
            color = "orange"
        utils.add_graph_data(race_ids, points, color=color,
                             label=constructor, marker=".")

    # Export graph
    utils.export_graph("Constructors Championship {}".format(year),
                       "/{}/constructors_championship-{}.png".format(GRAPHS_DIR, year), use_legend=True)


def drivers_season(year: str, highlighted_driver: str = None):
    """ Generate a graph illustrating the points accumulated
    by each driver in a specified year.
    """
    if not year:
        raise MissingParametersException

    race_ids, full_df = fetch_year_data("DRIVER", year)

    # race_results = dict()
    race_results = dict()
    for race in race_ids:
        data = full_df.loc[full_df["raceId"] ==
                           race][["code", "points"]].to_dict()
        drivers, points = list(data["code"].values()), list(
            data["points"].values())

        for r in range(0, len(drivers)):
            driver = drivers[r]
            point = int(points[r])

            if driver in race_results.keys():
                race_results[driver].append(point)
                continue
            race_results[driver] = [point]

        for not_racing in [x for x in race_results.keys() if x not in drivers]:
            race_results[not_racing].append(0)

    # Prepend zeros for drivers who did not start the season
    for driver in race_results.keys():
        missed = len(race_ids) - len(race_results[driver])

        for missed_race in range(missed):
            race_results[driver].insert(0, 0)

    number_races = list(range(1, len(race_ids) + 1))

    utils.configure_graph(
        title="Drivers Championship {}".format(year),
        x_label="Race Number",
        y_label="Points",
        x_intervals=number_races,
        set_grid=False)

    for driver, points in race_results.items():
        color = "grey"
        if highlighted_driver and highlighted_driver.upper() == driver.upper():
            color = "orange"
        utils.add_graph_data(race_ids, points, color=color,
                             label=driver, marker=".")

    # Export graph
    utils.export_graph("Drivers Championship {}".format(year),
                       "/{}/drivers_championship_per_race-{}.png".format(GRAPHS_DIR, year), use_legend=True)

    race_results_accum = dict()
    for driver, points in race_results.items():
        race_results_accum[driver] = list(np.cumsum(points))

    max_points = max(list(map(lambda d: d[-1], race_results_accum.values())))

    y_intervals = list(np.arange(0, max_points, 25))

    utils.configure_graph(
        title="Drivers Championship {}".format(year),
        x_label="Race Number",
        y_label="Points",
        x_intervals=number_races,
        y_intervals=y_intervals,
        set_grid=False)

    for driver, points in race_results_accum.items():
        color = "grey"
        if highlighted_driver and highlighted_driver.upper() == driver.upper():
            color = "orange"
        utils.add_graph_data(race_ids, points, color=color,
                             label=driver, marker=".")

    # Export graph
    utils.export_graph("Drivers Championship {}".format(year),
                       "/{}/drivers_championship-{}.png".format(GRAPHS_DIR, year), use_legend=True)


if __name__ == "__main__":

    # Handle arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option")
    parser.add_argument("-y", "--year")
    parser.add_argument("-c", "--constructor")
    parser.add_argument("-d", "--driver")
    parser.add_argument("-t", "--track")
    args = parser.parse_args()

    options = [
        "fastest-laps",
        "drivers-year",
        "constructors-year",
        "gained-lost"
    ]

    if not args.option or args.option not in options:
        sys.exit(PROGRAM_USAGE)

    if args.option == "gained-lost":
        places_gained_lost(args.year)

    if args.option == "fastest-laps":
        driver = args.driver if args.driver else None
        fastest_lap_times(args.year, highlighted_driver=driver)

    if args.option == "drivers-year":
        driver = args.driver if args.driver else None
        drivers_season(args.year, highlighted_driver=driver)

    if args.option == "constructors-year":
        team = args.team if args.team else None
        constructors_season(args.year, highlighted_team=team)
