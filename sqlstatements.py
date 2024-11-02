import os
import DBfunctions
import datetime
import pandas as pd
import openpyxl

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

    invoice, columns = DBfunctions.sql_execute("""
SELECT CONCAT(pp.Organization, " - ", lm.Person) as Person, lm.WorkDay , TIME_TO_SEC(TIMEDIFF(lm.EndTime, lm.StartTime))/(60*60)-lm.BreakHours as Quantity, ChargeType as "Type/Unit" , Rate, (TIME_TO_SEC(TIMEDIFF(lm.EndTime, lm.StartTime))/(60*60)-lm.BreakHours)*Rate as Cost, Description 
from log_money lm
join people2_people pp on pp.Name = lm.Person 
WHERE WorkDay BETWEEN ? AND ?
and BilledCustomer = 1
ORDER BY ChargeType, pp.Organization , Person , WorkDay ;
""", date_range_strings, result_type='table')
    invoice_report = pd.DataFrame(invoice, columns=columns)

    byperson, columns = DBfunctions.sql_execute("""
SELECT CONCAT(pp.Organization, " - ", Person) as "Person", sum((TIME_TO_SEC(TIMEDIFF(lm.EndTime, lm.StartTime))/(60*60)-lm.BreakHours)*Rate) as Total
from log_money lm
join people2_people pp on pp.Name = lm.Person 
WHERE WorkDay BETWEEN ? AND ?
and BilledCustomer = 1
GROUP BY Person 
ORDER BY Organization, Person;
""", date_range_strings, result_type='table')
    byperson_report = pd.DataFrame(byperson, columns=columns)

    bytype, columns = DBfunctions.sql_execute("""
SELECT ChargeType , sum((TIME_TO_SEC(TIMEDIFF(lm.EndTime, lm.StartTime))/(60*60)-lm.BreakHours)*Rate) as Cost
from log_money lm
join people2_people pp on pp.Name = lm.Person 
WHERE WorkDay BETWEEN ? AND ?
and BilledCustomer = 1
GROUP BY ChargeType 
ORDER BY ChargeType ;
""", date_range_strings, result_type='table')
    bytype_report = pd.DataFrame(bytype, columns=columns)

    byinvoice, columns = DBfunctions.sql_execute("""
SELECT CONCAT(pp.Organization, " - ", Person) as "Person", sum((TIME_TO_SEC(TIMEDIFF(lm.EndTime, lm.StartTime))/(60*60)-lm.BreakHours)*Rate) as Total, Description as InvoiceFilenames
from log_money lm
join people2_people pp on pp.Name = lm.Person 
WHERE WorkDay BETWEEN ? AND ?
and Description IS NOT NULL 
and BilledCustomer = 1
GROUP BY Description
ORDER BY Organization, Person;
""", date_range_strings, result_type='table')
    byinvoice_report = pd.DataFrame(byinvoice, columns=columns)

    with pd.ExcelWriter('bi-weekly report.xlsx') as writer:
        invoice_report.to_excel(writer, sheet_name='cr_invoice', index=False)
        byperson_report.to_excel(writer, sheet_name='by_person', index=False)
        # bytype_report.to_excel(writer, sheet_name='by_type', index=False)
        byinvoice_report.to_excel(writer, sheet_name='by_invoicefile', index=False)
  
    return True


def all_tasks()