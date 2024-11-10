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

def hours_report(bill_date):
    bill_date = (bill_date, )
    invoice, columns = DBfunctions.sql_execute("""
SELECT CONCAT(pp.Organization, " - ", lm.Person) as Person, lm.WorkDay , Quantity, ChargeType as "Type/Unit" , Rate, Quantity*Rate as Cost, Description 
from log_money lm
join people2_people pp on pp.Name = lm.Person 
WHERE BilledCustomer = ?
ORDER BY ChargeType, pp.Organization , Person , WorkDay ;
""", bill_date, result_type='table')
    invoice_report = pd.DataFrame(invoice, columns=columns)

    byperson, columns = DBfunctions.sql_execute("""
SELECT CONCAT(pp.Organization, " - ", Person) as "Person", sum(Quantity*Rate) as Total
from log_money lm
join people2_people pp on pp.Name = lm.Person 
WHERE BilledCustomer = ?
GROUP BY Person 
ORDER BY Organization, Person;
""", bill_date, result_type='table')
    byperson_report = pd.DataFrame(byperson, columns=columns)

    bytype, columns = DBfunctions.sql_execute("""
SELECT ChargeType , sum(Quantity*Rate) as Cost
from log_money lm
join people2_people pp on pp.Name = lm.Person 
WHERE BilledCustomer = ?
GROUP BY ChargeType 
ORDER BY ChargeType ;
""", bill_date, result_type='table')
    bytype_report = pd.DataFrame(bytype, columns=columns)

    byinvoice, columns = DBfunctions.sql_execute("""
SELECT CONCAT(pp.Organization, " - ", Person) as "Person", sum(Quantity*Rate) as Total, Description as InvoiceFilenames
from log_money lm
join people2_people pp on pp.Name = lm.Person 
WHERE BilledCustomer = ?
and Description IS NOT NULL 
GROUP BY Description
ORDER BY Organization, Person;
""", bill_date, result_type='table')
    byinvoice_report = pd.DataFrame(byinvoice, columns=columns)

    with pd.ExcelWriter('bi-weekly report.xlsx') as writer:
        invoice_report.to_excel(writer, sheet_name='cr_invoice', index=False)
        byperson_report.to_excel(writer, sheet_name='by_person', index=False)
        # bytype_report.to_excel(writer, sheet_name='by_type', index=False)
        byinvoice_report.to_excel(writer, sheet_name='by_invoicefile', index=False)
  
    return True


# consolidate notes for item b into notes for item a by adjusting the itemID
def consolidate(b, a):
    rows, columns = DBfunctions.sql_execute("""
SELECT FrontDoorID, snid 
from all_notes_cte 
WHERE Item = ? ;
""" , (b, ), 'table')
    
    qms_list = []
    for row in rows:
        qms_list.append((row[0], a, row[1]))

    for qms in qms_list:
        DBfunctions.sql_execute("""
UPDATE str4_notes 
SET ItemID = (
SELECT ItemID
from all_items_cte 
where FrontDoorID = ?
and Item = ?
)
WHERE snid = ? ;
""", qms, 'updatedb')

    DBfunctions.sql_execute("""
DELETE FROM str3_items 
WHERE Item = ? ;
""", (b,), 'updatedb')
    
    return True


# add note to the same item in a list of rooms
def add_note(item_name, rooms_list):
    pass


# add each item identified by 'residence' to each room
def generate_items():
    front_doors_list, columns = DBfunctions.sql_execute("""
SELECT sfid from all_frontdoors_cte afc 
where afc.TypeUnit = 'residence' ;""", False, 'table')
    print(f'Number of units: {len(front_doors_list)}')

    all_items_list, columns = DBfunctions.sql_execute("""
SELECT ItemName FROM list_items li 
WHERE li.Applicability in ('all','residences') ;""", False, 'table')
    print(f'Items per unit: {len(all_items_list)}')

    for sfid in front_doors_list:
        print(f'sfid: {sfid}')
        add_items_list, columns = DBfunctions.sql_execute("""
SELECT ItemName FROM list_items li 
WHERE li.Applicability in ('all','residences')
and ItemName NOT IN
(SELECT Item
from all_items_cte 
WHERE FrontDoorID = ?) ;
""", sfid, 'table')

        print(f'Number of items to be added: {len(add_items_list)}')
        if len(add_items_list) >= 1:

            DBfunctions.sql_execute("""
INSERT INTO str3_items (Item)
SELECT ItemName FROM list_items li 
WHERE li.Applicability in ('all','residences')
and ItemName NOT IN
(SELECT Item
from all_items_cte 
WHERE FrontDoorID = ?) ;
""", sfid, 'updatedb')

            DBfunctions.sql_execute("""
UPDATE str3_items 
SET FrontDoorID = ?
WHERE FrontDoorID is NULL ;
""", sfid, 'updatedb')

            DBfunctions.sql_execute("""
UPDATE str3_items 
SET Status = 'unmarked'
WHERE Status is NULL ;
""", False, 'updatedb')
    

    print(f'Items per unit: {len(all_items_list)}')
    print(f'Number of units: {len(front_doors_list)}')
    items_total, columns = DBfunctions.sql_execute("""
SELECT siid from all_items_cte aic
where TypeUnit = 'residence' ; """, False, 'table')
    print(f'Total number of items should be: {len(all_items_list)*len(front_doors_list)}')
    print(f'Total number of actual: {len(items_total)}')

    return True


# take item with note and list of rooms in building and change the status to status
def change_status(building, rooms_list, item, status, note):
    print(len(rooms_list))
    esses = ','.join(['%s'] * len(rooms_list))
    sql_statement = """
SELECT siid from all_items_cte
WHERE BuildingName = %%s
AND FrontDoor in (%s)
AND Item = %%s ;""" % esses
    qms = (building,) + rooms_list + (item,)
    siid_list, columns = DBfunctions.sql_execute(sql_statement, qms, 'table')
    print(len(siid_list))

    siid_list = tuple([i[0] for i in siid_list])
    esses = ','.join(['%s'] * len(siid_list))
    sql_statement = """
UPDATE str3_items
SET Status = %%s
WHERE siid in (%s) ; """ % esses
    qms = (status,) + siid_list
    DBfunctions.sql_execute(sql_statement, qms, 'updatedb')
    
    sql_statement = "INSERT INTO str4_notes (ItemID, Note, NoteType)\nVALUES "

    for index, siid in enumerate(siid_list):
        sql_statement += "\n(%s, '%s - Status set -%s-', 'statusset')" % (siid, status, note)
        if index < len(siid_list) - 1:
            sql_statement += ","
        else:
            sql_statement += " ;"

    DBfunctions.sql_execute(sql_statement, False, 'updatedb')

    return True


def todo_list_room(building, room):
    sql_statement = """
SELECT CONCAT(BuildingName, " " , FrontDoor) as 'Room' , Item , TradeAssociated , Status , GROUP_CONCAT(CONCAT(Note, " - ", DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %d %b')) order by Moment DESC separator '\n') as 'Notes', siid
from all_notes_cte
where BuildingName = ?
and FrontDoor = ?
GROUP by siid 
ORDER by Item ;"""
    qms = (building, room)
    todo_json = DBfunctions.sql_execute(sql_statement, qms, 'json')

    return todo_json