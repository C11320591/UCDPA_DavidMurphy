import sys
import urllib
from bs4 import BeautifulSoup


def fetch_base_urls(year: str):
    """
    Given a year between 1950-2021, scrap the Formula1 website to fetch the base urls
    for each race that took place that year.

    :param year - what year to generate race urls for.
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

    return [x.replace("race-result.html", "") for x in urls]