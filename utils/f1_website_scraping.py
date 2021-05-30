import sys
import urllib
from datetime import datetime
from bs4 import BeautifulSoup
from exceptions.exceptions import *


def _get_circuit_name(url: str):
    """
    Given the url to a race, get the name of a circuit.

    :param url - any of the child urls for the race:
            Eg. https://www.formula1.com/en/results.html/{year}/races/{race_no}/{country}/race-result.html
    :type str
    """
    race_url = urllib.request.urlopen(url).read()
    return BeautifulSoup(race_url, "html5lib").find_all("span", {"class": "circuit-info"})[0].get_text()


def fetch_base_urls(year: str):
    """
    Given a year between 1950-2021, scrap the Formula1 website to fetch the base urls
    for each race that took place that year where the base url has the below format:
        https://www.formula1.com/en/results.html/{year}/races/races.html

    This function is required for collecting race data such as starting grid and fastest laps.

    :param year: year to collect data and generate charts for. [Format "YYYY"]
    :type str
    """
    this_year = datetime.now().year

    if int(year) not in range(1950, this_year + 1):  # Formula1 was founded in 1950
        sys.exit(
            f"No race data available in {year} - must be within 1950-{this_year}")

    root_url = f"https://www.formula1.com/en/results.html/{year}/races.html"
    source = urllib.request.urlopen(root_url).read()
    soup = BeautifulSoup(source, "html5lib")

    urls = dict()
    for url in soup.find_all("a"):
        if f"results.html/{year}/races/" in str(url.get("href")):
            race_results_url = f"https://www.formula1.com{url.get('href')}"
            circuit_name = _get_circuit_name(race_results_url)
            urls[circuit_name.upper()] = race_results_url.replace("race-result.html", "")

    return urls


# Deprecated
def fetch_race_urls(year: str, circuit_name: str):
    """
    Given a year and the name of a circuit, fetch the race data urls for
    that race if it exists in that year. This can be handy for collecting 
    and comparing the data for a number years a race took place at the circuit.

    :param year: year to collect data and generate charts for. [Format "YYYY"]
    :type str

    :param circuit_name: self explanatory. Example: "Monza"
    :type str
    """
    races_in_year = fetch_base_urls(year)
    try:
        race_root_url = [v for k, v in races_in_year.items()
                         if circuit_name.upper() in k][0]
    except IndexError:
        raise RaceDataNotFoundException

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
