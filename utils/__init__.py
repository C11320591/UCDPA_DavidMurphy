import re
import sys
import urllib
import pandas as pd
# from datetime import datetime
from bs4 import BeautifulSoup


def generate_dataframe_from_url(url: str, index: str):
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
