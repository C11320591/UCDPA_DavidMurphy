## Project Description

Generate a series of charts to visualize Formula 1 race statistics from a specified year or list of years.
* Example: [2020 Charts](https://github.com/C11320591/UCDPA_DavidMurphy/blob/master/data/exported/2020-charts.pdf)

### Notes
* Charts are generated using data collected from either local csv files or via scraping the Formula1 website.
* The bar/line/pie charts are generated depending on the option selected during execution and are stored in a directory
specified in the [config](https://github.com/C11320591/UCDPA_DavidMurphy/blob/master/config/system_configs.ini) file.

### Usage
```
./main -o OPTION --year YEAR --params PARAMS 
```

#### Options
* **drivers-year**: two charts representing statistics for each driver.
* **retirements**: two charts breakdown of the retirements that took place.
* **gained-lost**: bar chart representing the total number of places lost + gained.
* **fastest-laps**: line chart representing the fastest lap times per driver in each race.

#### Params
Comma-separated list of driver codes. For example &rarr; `"HAM,VER,BOT,PER"`


### Resources
* Course &rarr; [**UCDPA: Certificate in Introductory Data Analytics**](https://www.ucd.ie/professionalacademy/findyourcourse/pd_data_analytics/)