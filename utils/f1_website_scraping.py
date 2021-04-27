import sys
import urllib
from datetime import datetime
from bs4 import BeautifulSoup


def get_circuit_name(url: str):
    """ Given the url to a race, get the name of a circuit.

    :param url - any of the child urls for the race:
            Eg. https://www.formula1.com/en/results.html/{year}/races/{race_no}/{country}/race-result.html
    """
    race_url = urllib.request.urlopen(url).read()
    return BeautifulSoup(race_url, "html5lib").find_all("span", {"class": "circuit-info"})[0].get_text()


def fetch_base_urls(year: str):
    """ Given a year between 1950-2021, scrap the Formula1 website to fetch the base urls
    for each race that took place that year.

    :param year - what year to generate race urls for
    """
    this_year = datetime.now().year

    if int(year) not in range(1950, this_year):  # Formula1 was founded in 1950
        sys.exit(
            f"No race data available in {year} - must be within 1950-{this_year}")

    root_url = f"https://www.formula1.com/en/results.html/{year}/races.html"
    source = urllib.request.urlopen(root_url).read()
    soup = BeautifulSoup(source, "html5lib")

    urls = dict()
    for url in soup.find_all("a"):
        if f"results.html/{year}/races/" in str(url.get("href")):
            race_results_url = "https://www.formula1.com{}".format(
                url.get("href"))
            circuit_name = get_circuit_name(race_results_url)
            urls[circuit_name.upper()] = race_results_url.replace(
                "race-result.html", "")

    return urls


def fetch_race_urls(year: str, circuit_name: str):
    """
    :param year - what year to get race urls for
    :param circuit_name - which race?
    """
    races_in_year = fetch_base_urls(year)
    race_root_url = races_in_year.get(circuit_name.upper())

    if not race_root_url:
        sys.exit(f"Race does not exist.")

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
