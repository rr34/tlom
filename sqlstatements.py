import os
import DBfunctions
import datetime
import pandas as pd

def test():
    execute_this = """
SELECT Organization, Name, Notes
from people2_people;
"""

    print_this = DBfunctions.sql_execute(execute_this, False)

    for (Organization, Name, Notes) in print_this:
        print(f"Organization: {Organization}, Name: {Name}, Notes: {Notes}")

def hours_report(date_range):
    # if second part is a number of days instead of a date
    if len(date_range[1]) <= 3:
        date_range_dts = (datetime.datetime.strptime(date_range[0], '%Y-%m-%d'), datetime.datetime.strptime(date_range[0], '%Y-%m-%d') + datetime.timedelta(days=date_range[1]))
    else:
        date_range_dts = (datetime.datetime.strptime(date_range[0], '%Y-%m-%d'), datetime.datetime.strptime(date_range[1], '%Y-%m-%d'))

    date_range_strings = (datetime.datetime.strftime(date_range_dts[0], '%Y-%m-%d'), datetime.datetime.strftime(date_range_dts[1], '%Y-%m-%d'))

    date_delta = (date_range_dts[1] - date_range_dts[0]).days
    dates_list = [date_range_dts[0] + datetime.timedelta(days=x) for x in range(date_delta)]

    hours, columns = DBfunctions.sql_execute("""
SELECT CONCAT(pp.Organization, ' - ', Person) as Person , WorkDay , TIME_TO_SEC(TIMEDIFF(lc.EndTime, lc.StartTime))/(60*60)-lc.BreakHours as hourscalc
from log_clock lc
JOIN people2_people pp on pp.Name = lc.Person
WHERE WorkDay BETWEEN ? AND ?
ORDER BY lc.Person , lc.WorkDay ;
""", date_range_strings)
    
    hours_report = pd.DataFrame(hours, columns=columns)

    hours_report_pivoted = hours_report.pivot(index='Person', columns='WorkDay')

    hours_report_pivoted.to_csv('hours_report.csv')
    
    return True