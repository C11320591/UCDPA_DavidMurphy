## Project Description

Generate a series of charts to visualize Formula 1 race statistics from a specified year or list of years.



### Notes
* Charts are generated using data collected from either local csv files or via scraping the Formula1 website.
* The bar/line/pie charts are generated depending on the option selected during execution and are stored in a directory
specified in the [config][https://github.com/C11320591/UCDPA_DavidMurphy/blob/master/config/system_configs.ini] file.

### Usage
```
./main -o OPTION --year YEAR --params PARAMS 
```

#### Options
* **drivers-year**: charts representing statistics for each driver in a specified year.
* **retirements**: breakdown of the retirements that took place in a specified list of years.
* **gained-lost**: bar chart representing the total number of places lost + gained in a specified year.
* **fastest-laps**: line graph representing the fastest lap times per driver in each race of a specified year.


### Resources
* [**UCDPA: Certificate in Introductory Data Analytics**](https://www.ucd.ie/professionalacademy/findyourcourse/pd_data_analytics/)