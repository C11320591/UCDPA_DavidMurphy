#!/usr/bin/env python3

""" PLACEHOLDER. FILL THIS IN!
"""
import os
import sys
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter

import utils
from exceptions.exceptions import *
from utils.f1_website_scraping import *

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


def retirements(years: list):
    """ PLACEHOLDER. FILL THIS IN!
    """
    if not years:
        raise MissingParametersException("year parameter required.")

    _years = years.split("-")
    _years = list(map(lambda d: int(d), _years))
    if len(_years) == 2:
        _years = list(range(min(_years), max(_years) + 1))

    status_df = utils.generate_dataframe_from_csv(
        utils.csv_documents()["STATUS"])

    status_code = dict()
    drivers = Counter()
    constructors = Counter()
    retirements = Counter()
    annual_retirements = Counter()

    for year in _years:
        race_ids, results_df = utils.fetch_year_data(year)
        annual_retirements[year] = {}
        for race in race_ids:
            race_results = results_df.loc[(results_df["raceId"] == race) & (
                results_df["positionText"] == "R")]

            for index, row in race_results.iterrows():
                driver, constructor, status = row.loc["driverId"], row.loc["constructorId"], row.loc["statusId"]
                drivers[driver] += 1
                constructors[constructor] += 1
                retirements[status] += 1

            if not annual_retirements[year].get(status):
                annual_retirements[year][status] = 1
                continue
            annual_retirements[year][status] += 1

    retirements_pc = dict()

    for status, num in retirements.items():
        if not status in status_code.keys():
            status_name = status_df.loc[status_df["statusId"]
                                        == status]["status"].values[0]
            status_code[status] = status_name
        name = status_code[status]
        percentage = (num / sum(retirements.values())) * 100
        retirements_pc[name] = round(percentage, 3)

    print(retirements_pc)
    # TODO: Pick up here, time to generate some graphs based on the above data collected.


def places_gained_lost(year: str):
    """ Identify how many places each driver gained/lost during the races of a year
    """
    if not year:
        raise MissingParametersException("year parameter required.")

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

    drivers = list(map(lambda d: d[-3:], list(places.keys())))
    places = list(places.values())

    plt.clf()
    fig, ax = plt.subplots()
    ax.invert_yaxis()
    ax.set_facecolor('#7E7E7E')
    plt.title("Places Gained/Lost in {}".format(year))
    plt.xlabel("Places (-/+)")

    for index, place in enumerate(places):
        driver = drivers[index]
        color = "red" if place < 0 else "lime"
        ax.barh(driver, place, color=color,
                label="driver", align="center", height=0.5)

    utils.export_graph(
        f"Places Gained/Lost {year}", f"{GRAPHS_DIR}/gained_lost-{year}.png")


def fastest_lap_times(year: str, highlighted_driver: str = None):
    """ FILL THIS IN!
    """
    if not year:
        raise MissingParametersException("year parameter required.")

    if int(year) not in range(2004, 2020):
        sys.exit("Woah, we don't have that year on file.")

    fastest_laps = dict()
    race_ids, full_df = utils.fetch_year_data(year, entity="LAPS")

    races_df = utils.generate_dataframe_from_csv(
        utils.csv_documents()["RACES"])
    race_codes = dict(zip(races_df["raceId"], races_df["name"]))

    for race in race_ids:
        grand_prix = race_codes[race][:3].upper()
        race_fl = dict()

        for index, data in full_df.loc[full_df["raceId"] == race][["code", "fastestLapTime"]].iterrows():
            driver, time = data
            race_fl[driver] = utils.convert_milliseconds(time)

        lap_times = list(race_fl.values())

        try:
            race_fl["Average"] = utils.get_average(lap_times)[1]
            # ignore "None" values
            race_fl["Fastest"] = min([x for x in lap_times if x])
            race_fl["Slowest"] = max([x for x in lap_times if x])
        except ZeroDivisionError:
            print(
                "No lap times recorded for {} Grand Prix in year {}".format(grand_prix, year))
            continue

        fastest_laps[grand_prix] = race_fl

    # Create + configure DataFrame
    fastest_laps_df = pd.DataFrame(fastest_laps).transpose()
    fastest_laps_df.index.name = "Grand Prix"
    fastest_laps_df.replace("\\N", np.NaN, inplace=True)

    # Convert times from microseconds to seconds
    fastest_laps_df = fastest_laps_df.apply(lambda d: d / 1000, axis=1)

    # Configure Graph
    plt.clf()
    sns.set_theme(style="darkgrid", font="sans")
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    plt.title("Fastest Laps {}".format(year))
    plt.xlabel("Grand Prix")
    plt.ylabel("Time (seconds)")
    plt.grid(True)

    # Plot data
    for index, col in enumerate(fastest_laps_df.columns):
        if col == "Average":
            plt.plot(fastest_laps_df.index,
                     fastest_laps_df[col], color="black", label="Average", linestyle="--")
            continue
        if col == "Fastest":
            plt.plot(fastest_laps_df.index,
                     fastest_laps_df[col], color="green", label="Fastest")
            continue
        if col == "Slowest":
            plt.plot(fastest_laps_df.index,
                     fastest_laps_df[col], color="yellow", label="Slowest")
            continue
        if highlighted_driver:
            if col == highlighted_driver.upper():
                plt.plot(fastest_laps_df.index,
                         fastest_laps_df[col], color="red", label=highlighted_driver.upper())
        plt.plot(fastest_laps_df.index,
                 fastest_laps_df[col], color="grey", label=None, alpha=0.25)

    # Export graph
    utils.export_graph("Fastest Laps {}".format(year),
                       "/{}/fastest-laps-{}.png".format(GRAPHS_DIR, year), use_legend=True)


def constructors_season(year: str, highlighted_team: str = None):
    """ Using some CSVs documents, generate graphs to illustrate
    constructors championship in a specified year
    """
    if not year:
        raise MissingParametersException("year parameter required.")

    race_ids, constructor_ids, constructors_df, full_df = utils.fetch_year_data(
        year, entity="CONSTRUCTOR")
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

    race_ids, full_df = utils.fetch_year_data(year, entity="DRIVER")

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
        "gained-lost",
        "retirements"
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
        team = args.constructor if args.constructor else None
        constructors_season(args.year, highlighted_team=team)

    if args.option == "retirements":
        retirements(args.year)
