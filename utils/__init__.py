import sys
import urllib
import pandas as pd
from bs4 import BeautifulSoup


def fetch_base_urls(year: str):
    """ Given a year between 1950-2021, scrap the Formula1 website to fetch the base urls
    for each race that took place that year.

    :param year - what year to generate race urls for
    """

    if int(year) not in range(1950, 2021):  # Formula1 was founded in 1950
        sys.exit(f"No race data available in {year} - must be within 1950-2021")
    
    root_url = f"https://www.formula1.com/en/results.html/{year}/races.html"
    source = urllib.request.urlopen(root_url).read()
    soup = BeautifulSoup(source, "html5lib")

    urls = list()
    for url in soup.find_all("a"):
        if f"results.html/{year}/races/" in str(url.get("href")):
            urls.append("https://www.formula1.com{}".format(url.get("href")))

    base_urls = [x.replace("race-result.html", "") for x in urls]

    urls_index = dict()
    for i in range(0, len(base_urls)):
        urls_index[i] = base_urls[i]

    return urls_index

def fetch_race_urls(year: str, race_number: int):
    """
    :param year - what year to get race urls for
    :param race_number - what race number in the specified year
    """
    races_in_year = fetch_base_urls(year)
    race_root_url = races_in_year.get(race_number)

    if not race_root_url:
        sys.exit(f"Race number does not exist. Please choose an option from 0 -> {len(races_in_year)}")

    data_urls = [
        "race-result.html", 
        "fastest-laps.html", 
        "pit-stop-summary.html", 
        "starting-grid.html", 
        "qualifying.html"
    ]

    race_urls = dict()
    for url in data_urls:
        race_urls[url.split(".")[0].upper()] = race_root_url + url
    
    return race_urls

def generate_dataframe_from_url(url: str):
    """
    :param url - the url to scrap the HTML table from
    """
    html = urllib.request.urlopen(url).read()
    html_table = BeautifulSoup(html, "html5lib").find_all("table")[0]

    data_frame = pd.read_html(str(html_table), flavor="bs4", header=[0])[0]
    data_frame.dropna(axis="columns", inplace=True)  # Clean output

    return data_frame

def merge_dataframes(dataframes: list, key: str):
    """
    :param dataframes - a list of dataframes to merge
    :param key - the index to join the frames on
    """
    if not len(dataframes) == 2:
        raise Exception(f"Two dataframes required. Provided: {dataframes}")
    return dataframes[0].set_index(key).join(dataframes[1].set_index(key))
    