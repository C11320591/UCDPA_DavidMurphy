import os
import re
import sys
import urllib
import configparser
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns


CONFIG_FILE = "/home/ubuntu/assignment/repo/config/system_configs.ini"


def fetch_config(key: str):
    """ Assuming a key exists in the config file, return its value.
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    try:
        return config['config'][key]
    except KeyError:
        sys.exit(f"There is no configuration for {key} in the config file.")


def extract_matching_charactors(pattern: str, strings: list):
    """ Remove charactors from a list of strings that do not match a pattern.
    Example: "[^\d]+" - non-numerical charactors

    """
    return list(map(lambda x: int(re.sub(r"{}".format(pattern), "", x)), strings))


def convert_milliseconds(time: str):
    """ Converts between lap time and milliseconds, 
    depending on the presence of a colon in the input value which indicates lap time.

    :param time
    """
    if "\\N" in str(time):
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


def get_average(times: list):
    """ Given a list of times, return the average in format {str: float}

    :param times
    """

    if isinstance(times[0], str):
        times = [x for x in times if ":" in x]
        times = list(map(convert_milliseconds, times))
    else:
        times = [x for x in times if isinstance(x, int)]

    average_time = sum(times) / len(times)

    return [convert_milliseconds(average_time), average_time]


"""
Pandas functions
"""


def csv_documents():
    """ PLACEHOLDER. FILL THIS IN!
    """
    root = fetch_config("CSV_DATA_PATH")

    documents = dict()
    for doc in os.listdir(root):
        documents[doc.split(".csv")[0].upper()] = root + doc

    return documents


def generate_dataframe_from_url(url: str, index: str = None):
    """ PLACEHOLDER. FILL THIS IN!
    :param url - the url to scrap the HTML table from
    """
    html = urllib.request.urlopen(url).read()
    html_table = BeautifulSoup(html, "html5lib").find_all("table")[0]

    data_frame = pd.read_html(str(html_table), flavor="bs4", header=[0])[0]
    if index:
        data_frame.set_index(index.capitalize(), inplace=True)
    data_frame.dropna(axis="columns", inplace=True)  # Clean output

    return data_frame


def generate_dataframe_from_csv(file: str, index: str = None):
    """ PLACEHOLDER. FILL THIS IN!
    """
    data_frame = pd.read_csv(file)
    if index:
        data_frame.set_index(index, inplace=True)

    return data_frame


def join_dataframes(dataframes: list, key: str):
    """ PLACEHOLDER. FILL THIS IN!
    :param dataframes - a list of dataframes to merge
    :param key - the index to join the frames on
    """
    if not len(dataframes) == 2 or not key:
        raise Exception(
            "Two dataframes (list) and a index key (string) required.")

    return dataframes[0].set_index(key).join(dataframes[1].set_index(key))


def fetch_year_data(year: int, entity: str = None):
    """ FILL THIS IN!
    """
    documents = csv_documents()
    races_df = generate_dataframe_from_csv(documents["RACES"])
    race_ids = list(races_df.loc[races_df["year"] == int(year)]["raceId"])

    results_df = generate_dataframe_from_csv(documents["RESULTS"])

    if not entity:
        return race_ids, results_df

    if entity.upper() == "LAPS":
        drivers_df = generate_dataframe_from_csv(documents["DRIVERS"])[
            ["driverId", "code", "surname"]]
        # Pull rows in drivers where code = "\N" and use surname as code
        for driver, values in drivers_df.iterrows():
            id,  code, surname = values[["driverId", "code", "surname"]]
            if code == "\\N":
                drivers_df.loc[drivers_df["driverId"] == id, ["code"]] = surname.replace(" ", "")[
                    :3].upper()

        full_df = join_dataframes(
            [results_df, drivers_df], key="driverId")

        full_df.sort_values(by=["raceId"], inplace=True)

        return race_ids, full_df

    if entity.upper() == "DRIVER":
        drivers_df = generate_dataframe_from_csv(
            documents["DRIVERS"])[["driverId", "code", "surname"]]
        # Pull rows in drivers where code = "\N" and use surname as code
        for driver, values in drivers_df.iterrows():
            id,  code, surname = values[["driverId", "code", "surname"]]
            if code == "\\N":
                drivers_df.loc[drivers_df["driverId"] == id, ["code"]] = surname.replace(" ", "")[
                    :3].upper()

        full_df = join_dataframes(
            [results_df, drivers_df], key="driverId")

        return race_ids, full_df

    if entity.upper() in ["CONSTRUCTOR", "TEAM"]:
        constructors_df = generate_dataframe_from_csv(
            documents["CONSTRUCTORS"])
        constructors_results_df = generate_dataframe_from_csv(
            documents["CONSTRUCTOR_RESULTS"])
        results_in_year = constructors_results_df[constructors_results_df.raceId.isin(
            race_ids)]
        constructor_ids = set(results_in_year["constructorId"])
        full_df = join_dataframes(
            [constructors_df, results_in_year], key="constructorId")

        return race_ids, constructor_ids, constructors_df, full_df


"""
Matplotlib functions
"""


def configure_graph(title: str, x_label: str,  y_label: str, x_intervals: list = None, y_intervals: list = None, set_grid=False):
    """ PLACEHOLDER. FILL THIS IN!
    """
    plt.clf()
    plt.grid(set_grid)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    if x_intervals:
        plt.xticks(x_intervals)
    if y_intervals:
        plt.yticks(y_intervals)


def add_graph_data(x_data: list, y_data: list, label: str = None, marker: str = None, color: str = None, xticks_label: list = None, yticks_label: list = None, is_scatter=False, barh=False):
    """ PLACEHOLDER. FILL THIS IN!
    """
    if is_scatter:
        plt.scatter(x_data, y_data, label=label, marker=marker)
    elif barh:
        fig, ax = plt.subplots()
        ax.invert_yaxis()
        plt.yticks(ticks=list(range(1, len(x_data) + 1)), labels=yticks_label)
        for x, y in zip(x_data, y_data):
            label = x[-3:]
            color = "red" if y < 0 else "lime"
            ax.barh(x, y, color=color, label=label, align="center")
    else:
        plt.plot(x_data, y_data, color=color, label=label, marker=marker)


def export_graph(title: str, path: str, use_legend=False):
    """ PLACEHOLDER. FILL THIS IN!
    """
    if use_legend:
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.savefig(path, bbox_inches='tight')


"""
Seaborn functions
"""

# TODO: Add + use some functions here
