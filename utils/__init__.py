import os
import re
import sys
import json
import urllib
import pathlib
import numpy as np
import pandas as pd
import configparser
import seaborn as sns
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from exceptions.exceptions import *


# CONFIG_FILE = "./config/system_configs.ini"
CONFIG_FILE = "/home/ubuntu/assignment/repo/config/system_configs.ini"


def fetch_definitions(key: str):
    """
    Given a key, return a dictionary with the data stored in the file.

    :param key: represents any of the keys defined in the definitions file.
    :type str
    """
    definitions_file = fetch_path("DEFINITIONS_FILE")

    with open(definitions_file, "r") as definitions:
        data = json.load(definitions)

    if data[key]:
        return data[key]


def fetch_path(key: str):
    """
    Using the ConfigParser module, return the path to a file/directory
    required for some of the functions in main. For example, the path
    to store the charts generated.

    :param key: represents any of the keys set in the config file.
    :type str
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    try:
        return config['path'][key]
    except KeyError:
        sys.exit(f"There is no configuration for {key} in the config file.")


# Deprecated
def extract_matching_charactors(pattern: str, strings: list):
    """
    Remove charactors from a list of strings that do not match a pattern.
    Example: "[^\d]+" - non-numerical charactors

    :param pattern: the charactors to extract from the list of strings
    :type str

    :param strings: a list of string objects to extract charactors that match
    the specified pattern.
    :type list
    """
    return list(map(lambda x: int(re.sub(r"{}".format(pattern), "", x)), strings))


def convert_milliseconds(time: str):
    """ 
    If provided an elapsed time, convert to milliseconds
    Otherwise, convert from milliseconds to elapsed time.

    :param time: milliseconds / elasped time [Format "mm:ss:ms"]
    :type str
    """
    if "\\N" in str(time):  # Don't execute for NaN values.
        return

    if ":" in str(time):
        mins, sec, milliseconds = re.split(r"[^\d]+", time)
        converted = int(mins) * 60000 + int(sec) * 1000 + int(milliseconds)

    else:
        mins, sec = divmod(int(time) / 1000, 60)
        minutes = str(int(mins))
        seconds = str(int(sec // 1))
        milliseconds = str(sec % 1).split(".")[1][0:3]
        converted = f"{minutes}:{seconds}.{milliseconds}"

    return converted


# Deprecated
def get_average(times: list):
    """
    Given a list of lap times, convert each value to milliseconds and calculate
    the average of all times.

    :param times: list of lap times
    :type list
    """
    if isinstance(times[0], str):
        times = [x for x in times if ":" in x]  # Remove items that do not match a lap time.
        times = list(map(convert_milliseconds, times))
    else:
        times = [x for x in times if isinstance(x, int)]

    average_time = sum(times) / len(times)

    return [convert_milliseconds(average_time), average_time]


"""
Pandas functions
"""

def csv_documents():
    """
    Return a dictionary representing each csv file
    in the directory specified in the config

    {
        "RACE-RESULTS": /path/to/race-results.csv,
        [...]
    }
    """
    root = fetch_path("CSV_DATA_PATH")

    documents = dict()
    for doc in os.listdir(root):
        documents[doc.split(".csv")[0].upper()] = root + doc

    return documents


def generate_dataframe_from_url(url: str, index: str = None):
    """
    Given a url that represents data for a specific race in year,
    use BeautifulSoup to scrap the url for a html table which is
    transformed into a pandas DataFrame - using an index if specified.

    :param url: the url to scrap the html table from
    :type str

    :param index: which column to specify as the index.
    :type str
    """
    html = urllib.request.urlopen(url).read()
    html_table = BeautifulSoup(html, "html5lib").find_all("table")[0]

    data_frame = pd.read_html(str(html_table), flavor="bs4", header=[0])[0]
    if index:
        data_frame.set_index(index.capitalize(), inplace=True)
    data_frame.dropna(axis="columns", inplace=True)  # Drop columns that contain NaN values.

    return data_frame


def generate_dataframe_from_csv(file: str, index: str = None):
    """
    This function loads a csv file as a pandas DataFrame - using an
    index if specified.

    :param file: the path to the csv file to load from.
    :type str

    :param index: which column to specify as the index.
    :type str
    """
    data_frame = pd.read_csv(file)
    if index:
        data_frame.set_index(index, inplace=True)

    return data_frame


def _join_dataframes(dataframes: list, key: str):
    """
    Given a a list of two dataframes, use the join function to merge them together.

    :param dataframes: a list of pandas DataFrames to merge using a specifed key.
    :type list

    :param key: the common index to join the frames on
    :type str
    """
    if not len(dataframes) == 2:
        raise InsufficientParametersException("Two dataframes required.")
    if not key:
        raise MissingParametersException("key parameter required.")

    return dataframes[0].set_index(key).join(dataframes[1].set_index(key))


def fetch_year_data(year: int, entity: str = None):
    """
    Given a year, return a list of race ids and one or more
    pandas DataFrames pertaining to an entity specified.

    :param year: year to collect data for. [Format YYYY]
    :type int

    :param entity: what data to gather for that year [Example: drivers]
    :type str
    """
    documents = csv_documents()

    # Fetch the unique race ids for each races in year specified.
    races_df = generate_dataframe_from_csv(documents["RACES"])
    race_ids = list(races_df.loc[races_df["year"] == int(year)]["raceId"])

    results_df = generate_dataframe_from_csv(documents["RESULTS"])

    if not entity:
        return race_ids, results_df

    if entity.upper() == "LAPS":
        drivers_df = generate_dataframe_from_csv(documents["DRIVERS"])[["driverId", "code", "surname"]]
        for driver, values in drivers_df.iterrows():
            id,  code, surname = values[["driverId", "code", "surname"]]
            if code == "\\N":
                drivers_df.loc[drivers_df["driverId"] == id, ["code"]] = surname.replace(" ", "")[:3].upper()

        full_df = _join_dataframes([results_df, drivers_df], key="driverId")

        full_df.sort_values(by=["raceId"], inplace=True)

        return race_ids, full_df

    if entity.upper() == "DRIVER":
        drivers_df = generate_dataframe_from_csv(documents["DRIVERS"])[["driverId", "code", "surname"]]
        for driver, values in drivers_df.iterrows():  # Pull rows in drivers where code = "\N" and use surname as code
            id,  code, surname = values[["driverId", "code", "surname"]]
            if code == "\\N":
                drivers_df.loc[drivers_df["driverId"] == id, ["code"]] = surname.replace(" ", "")[:3].upper()

        full_df = _join_dataframes([results_df, drivers_df], key="driverId")

        return race_ids, full_df

    if entity.upper() in ["CONSTRUCTOR", "TEAM"]:
        constructors_df = generate_dataframe_from_csv(documents["CONSTRUCTORS"])
        constructors_results_df = generate_dataframe_from_csv(documents["CONSTRUCTOR_RESULTS"])
        results_in_year = constructors_results_df[constructors_results_df.raceId.isin(race_ids)]
        constructor_ids = set(results_in_year["constructorId"])
        full_df = _join_dataframes([constructors_df, results_in_year], key="constructorId")

        return race_ids, constructor_ids, constructors_df, full_df


"""
Graphing functions
"""

def clear_canvas(figsize: tuple = None):
    """
    Clear the canvas and set the default chart theme.

    :param figsize: the size of the chart (width, height)
    :type tuple
    """
    plt.clf()
    if figsize:
        plt.figure(figsize=figsize)
    sns.set_theme(style="darkgrid", font="sans", context="paper")


def configure_graph(title : str,
                    xlabel: str = None,
                    ylabel: str = None, 
                    xticks: str = None,
                    yticks: str = None,
                    set_grid=False):
    """ PLACEHOLDER. FILL THIS IN!

    :param title: set chart title
    :type str

    :param xlabel: set label for the x axis.
    :type str

    :param ylabel: set label for the y axis.
    :type str

    :param xticks: set parameters for the x axis.
    :type str

    :param yticks: set parameters for the y axis.
    :type str

    :param set_grid: draw a grid on the chart.
    :type bool
    :default False
    """
    plt.suptitle(title, fontsize=20, fontfamily="serif")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(set_grid)

    if xticks:
        rotation = xticks["rotation"]
        plt.xticks(rotation=rotation, fontsize=10)

    if yticks:
        rotation = yticks["rotation"]
        plt.yticks(rotation=rotation, fontsize=10)


def export_graph(path: str, use_legend=False):
    """
    Export a chart to a specified location on the disk - with
    a legend if use_legend is set to True.

    :param path: where the graph is stored locally.
    :type str

    :param use_legend: display a legend on the graph.
    :type bool
    :default False
    """
    if use_legend:
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.savefig(path, bbox_inches='tight')
