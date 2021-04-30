import re
import sys
import urllib
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


def extract_matching_charactors(pattern: str, strings: list):
    """ Remove charactors from a list of strings that do not match a pattern.
    Example: "[^\d]+" - non-numerical charactors

    :param strings (list)
    """
    return list(map(lambda x: int(re.sub(r"{}".format(pattern), "", x)), strings))


def convert_milliseconds(time: str):
    """ Converts between lap time and milliseconds, 
    depending on the presence of a colon in the input value which indicates lap time.

    :param time
    """
    # TODO - how to convert a list of times: list(map(convert_to_milliseconds, list_of_times))

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
        times = list(map(convert_milliseconds, times))

    average_time = sum(times) / len(times)

    return {convert_milliseconds(average_time): average_time}


# Pandas functions

def generate_dataframe_from_url(url: str, index: str = None):
    """
    :param url - the url to scrap the HTML table from
    """
    html = urllib.request.urlopen(url).read()
    html_table = BeautifulSoup(html, "html5lib").find_all("table")[0]

    data_frame = pd.read_html(str(html_table), flavor="bs4", header=[0])[0]
    if index:
        data_frame.set_index(index.capitalize(), inplace=True)
    data_frame.dropna(axis="columns", inplace=True)  # Clean output

    return data_frame


def merge_dataframes(dataframes: list, key: str):
    """
    :param dataframes - a list of dataframes to merge
    :param key - the index to join the frames on
    """
    if not len(dataframes) == 2 or not key:
        raise Exception(
            "Two dataframes (list) and a index key (string) required.")

    return dataframes[0].set_index(key).join(dataframes[1].set_index(key))

# Matplotlib functions


def configure_graph(title: str, x_label: str,  y_label: str, x_intervals: list, y_intervals: list, set_grid=False):
    """
    """
    plt.clf()
    plt.grid(set_grid)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(x_intervals)
    # plt.yticks(y_intervals)


def add_graph_data(x_data: list, y_data: list, label: str, marker: str, is_scatter=False):
    """
    """
    if is_scatter:
        plt.scatter(x_data, y_data, label=label, marker=marker)
    else:
        plt.plot(x_data, y_data, label=label, marker=marker)


def export_graph(title: str, path: str):
    """
    """
    plt.legend(title=title, bbox_to_anchor=(1.05, 1))
    plt.savefig(path, bbox_inches='tight')
