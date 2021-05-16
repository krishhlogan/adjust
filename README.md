# Adjust Home task solution

The solution is basically built on flask. All the data from sample dataset.csv is dumped into the sqlite database.

Query used to create the dataset database is given below

```
CREATE TABLE dataset
         (ID INT PRIMARY KEY NOT NULL,
         DAY DATE ,
         CHANNEL TEXT  NOT NULL,
         COUNTRY CHAR(10) NOT NULL,
         OS CHAR(10) NOT NULL,
         IMPRESSIONS INT NOT NULL,
        CLICKS INT NOT NULL,
        INSTALLS INT NOT NULL,
        SPEND REAL NOT NULL,
        REVENUE REAL NOT NULL);
```

Suitable URLs for the four sample cases provided on the task is given below. (Currently localhost IP is provided)

Task link : https://gist.github.com/kotik-adjust/4883e33c439db6de582fd0986939045c

case 1:
Show the number of impressions and clicks that occurred before the 1st of June 2017, broken down by channel and country, sorted by clicks in descending order

http://0.0.0.0:5353/api/v1/query/?groupby=channel,country&sortby=clicks=desc&filterby=date_lt=2017-06-01&aggregate=sum&select=impressions,clicks

case 2:
Show the number of installs that occurred in May of 2017 on iOS, broken down by date, sorted by date in ascending order.

http://0.0.0.0:5353/api/v1/query/?groupby=day&sortby=day=asc&filterby=date_from=2017-05-01,date_to=2017-05-31,os=ios&aggregate=sum&select=installs

case 3:
Show revenue, earned on June 1, 2017 in US, broken down by operating system and sorted by revenue in descending order.

http://0.0.0.0:5353/api/v1/query/?groupby=os&sortby=revenue=desc&filterby=date_eq=2017-06-01&aggregate=sum&select=revenue

case 4:
Show CPI and spend for Canada (CA) broken down by channel ordered by CPI in descending order. Please think carefully which is an appropriate aggregate function for CPI.

http://0.0.0.0:5353/api/v1/query/?groupby=channel&sortby=cpi=desc&filterby=country=ca&aggregate=sum&select=spend&derived=cpi


Below are the details of all accepted url parameter for filtering, grouping, sorting, aggregation. The application already contains validation checks to make sure, passed url params are valid.

```
#values accepted for url param filterby
accepted_filter_options = ['date_gt','date_gte','date_lt','date_lte', 'date_to', 'date_eq', 'channel', 'country', 'os']

#values accepted for url param groupby
accepted_groupby_options = ['day', 'channel', 'country', 'os']

#values accepted for url param derived
accepted_derived_metric = ['cpi']

#values accepted for url param sortby
accepted_sortby_options = ['day', 'channel', 'country', 'os', 'impressions', 'clicks', 'installs', 'spend', 'revenue', 'cpi']

#values accepted for url param aggregate
accepted_aggregate_options = ['sum', 'max', 'min']

#values accepted for url param select
acccepted_select_options = ['impressions', 'clicks', 'installs', 'spend', 'revenue']
```
