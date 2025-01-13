import os
import DBfunctions
import datetime
import pandas as pd
import openpyxl
import re

def test():
    execute_this = """
SELECT Organization, Name, Notes
from people2_people;
"""

    print_this = DBfunctions.sql_execute(execute_this, False)

    for (Organization, Name, Notes) in print_this:
        print(f"Organization: {Organization}, Name: {Name}, Notes: {Notes}")

def hours_report(bill_dates, this_report):
    for bill_date in bill_dates:
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
ORDER BY Organization, Person, Description;
""", bill_date, result_type='table')
        byinvoice_report = pd.DataFrame(byinvoice, columns=columns)
    
        if bill_date[0] != this_report:
            print(bill_date[0] + ' Total: ' + str(invoice_report['Cost'].sum()))
        elif bill_date[0] == this_report:
            print(bill_date[0] + ' Total: ' + str(invoice_report['Cost'].sum()))
            with pd.ExcelWriter('bi-weekly report.xlsx') as writer:
                invoice_report.to_excel(writer, sheet_name='cr_invoice', index=False)
                byperson_report.to_excel(writer, sheet_name='by_person', index=False)
                # bytype_report.to_excel(writer, sheet_name='by_type', index=False)
                byinvoice_report.to_excel(writer, sheet_name='by_invoicefile', index=False)
  
    return True


def misc_reports(start_date, end_date):
    invoice, columns = DBfunctions.sql_execute("""
SELECT CONCAT(BuildingName, " " , FrontDoor) as 'Unit', Occupancy , OriginalOccupancy 
from all_notes_cte anc 
WHERE TypeUnit = 'residence'
AND (OriginalOccupancy = 'occupied'
OR Occupancy = 'occupied'
OR Priority = 'p0')
GROUP BY BuildingName , FrontDoor 
ORDER by BuildingName , FrontDoor ;
""", False, result_type='table')
    occupied_plus_complete = pd.DataFrame(invoice, columns=columns)

    invoice, columns = DBfunctions.sql_execute("""
SELECT DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %e %b') as 'Date', CONCAT(BuildingName, " " , FrontDoor) as 'Unit' , Occupancy , OriginalOccupancy , Priority , Note 
from all_notes_cte
WHERE Note LIKE '%p0%'
ORDER by Moment DESC , BuildingName , FrontDoor , Step , Item ;
""", False, result_type='table')
    completed_bydate = pd.DataFrame(invoice, columns=columns)

    invoice, columns = DBfunctions.sql_execute("""
SELECT BuildingName as 'Building', Occupancy , COUNT(Occupancy) as 'Count'
FROM all_frontdoors_cte afc 
WHERE TypeUnit = 'residence'
group by BuildingName , Occupancy 
ORDER by BuildingName , Occupancy ;
""", False, result_type='table')
    occupancy_report = pd.DataFrame(invoice, columns=columns)

    invoice, columns = DBfunctions.sql_execute("""
SELECT BuildingName as 'Building' , Status , COUNT(Status) as 'Count' 
from all_notes_cte
WHERE Occupancy = 'vacant'
and TypeUnit = 'residence'
GROUP by BuildingName , Status
ORDER BY BuildingName , FIELD(Status, 'unmarked,','todo','complete') ;
""", False, result_type='table')
    bybuilding_counts = pd.DataFrame(invoice, columns=columns)

    invoice, columns = DBfunctions.sql_execute("""
SELECT Item , Status , COUNT(Status) as 'Count' 
from all_notes_cte
WHERE Occupancy = 'vacant'
and TypeUnit = 'residence'
GROUP by ItemName , Status 
ORDER BY Item , FIELD(Status, 'unmarked,','todo','complete') ;
""", False, result_type='table')
    byitem_counts = pd.DataFrame(invoice, columns=columns)

    invoice, columns = DBfunctions.sql_execute("""
SELECT CONCAT(BuildingName, ' ', FrontDoor) as 'Unit', Item , Status 
from all_notes_cte
WHERE Occupancy = 'vacant'
and TypeUnit = 'residence'
GROUP by BuildingName , FrontDoor , ItemName 
ORDER BY BuildingName , FrontDoor , ItemName ;
""", False, result_type='table')
    byroom_detail = pd.DataFrame(invoice, columns=columns)

    invoice, columns = DBfunctions.sql_execute("""
SELECT CONCAT(BuildingName, " " , FrontDoor) as 'Room' , COUNT(Status) as 'Remaining Items' , Priority
from all_items_cte aic 
WHERE Occupancy = 'vacant'
and Status != 'complete'
GROUP by BuildingName , FrontDoor
ORDER BY COUNT(Status) ;
""", (start_date, end_date), result_type='table')
    incomplete_byroom = pd.DataFrame(invoice, columns=columns)

    invoice, columns = DBfunctions.sql_execute("""
SELECT Priority , Step, Trade , CONCAT(BuildingName , ' ' ,  FrontDoor) as 'Unit' , Item , GROUP_CONCAT(CONCAT(Note, " - ", DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %e %b')) order by Moment DESC separator '---') as 'Notes'
from all_notes_cte
WHERE Status = 'todo'
and TypeUnit = 'residence'
GROUP by siid 
Order by Priority , Step, BuildingName , FrontDoor , Item ;
""", (start_date, end_date), result_type='table')
    todo_ordered = pd.DataFrame(invoice, columns=columns)

    invoice, columns = DBfunctions.sql_execute("""
SELECT Trade , CONCAT(BuildingName , ' ' ,  FrontDoor) as 'Unit' , Item , GROUP_CONCAT(CONCAT(Note, " - ", DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %e %b')) order by Moment DESC separator '---') as 'Notes'
from all_notes_cte
WHERE Status = 'complete'
and siid IN (
SELECT ItemID from str4_notes
WHERE Note LIKE '%Status->todo%')
and siid IN (
SELECT ItemID from str4_notes
WHERE Note LIKE '%Status->complete%'
and Moment >= ?
and Moment <= ?)
GROUP by siid 
Order by Trade , Item, Note ;
""", (start_date, end_date), result_type='table')
    completed_forperiod = pd.DataFrame(invoice, columns=columns)

    invoice, columns = DBfunctions.sql_execute("""
SELECT CONCAT(BuildingName, " " , FrontDoor) as 'Room' , Item , Note , DATE_FORMAT(DATE_SUB(Moment, INTERVAL 5 hour), '%a, %e %b') as 'Date'
from all_notes_cte
WHERE Note LIKE '%Status->complete%'
AND Moment >= ?
AND Moment <= ?
ORDER BY Item , Note , Moment ;
""", (start_date, end_date), result_type='table')
    markedcomplete = pd.DataFrame(invoice, columns=columns)

    invoice, columns = DBfunctions.sql_execute("""
SELECT CONCAT(BuildingName, " " , FrontDoor) as 'Room' , Item , Note , DATE_FORMAT(DATE_SUB(Moment, INTERVAL 5 hour), '%a, %e %b') as 'Date'
from all_notes_cte
WHERE Note LIKE '%Status->todo%'
AND Moment >= ?
AND Moment <= ?
ORDER BY Item , Note , Moment ;
""", (start_date, end_date), result_type='table')
    markedtodo = pd.DataFrame(invoice, columns=columns)

    with pd.ExcelWriter('misc reports.xlsx') as writer:
        occupied_plus_complete.to_excel(writer, sheet_name='occ_plus_complete', index=False)
        completed_bydate.to_excel(writer, sheet_name='completed_bydate', index=False)
        occupancy_report.to_excel(writer, sheet_name='occupancy', index=False)
        bybuilding_counts.to_excel(writer, sheet_name='bybuilding_counts', index=False)
        byitem_counts.to_excel(writer, sheet_name='byitem_counts', index=False)
        byroom_detail.to_excel(writer, sheet_name='byroom_detail', index=False)
        incomplete_byroom.to_excel(writer, sheet_name='incompletecounts_byroom', index=False)
        todo_ordered.to_excel(writer, sheet_name='todo_ordered', index=False)
        completed_forperiod.to_excel(writer, sheet_name='completed_forperiod', index=False)
        markedcomplete.to_excel(writer, sheet_name='markedcomplete_forperiod', index=False)
        markedtodo.to_excel(writer, sheet_name='markedtodo_forperiod', index=False)
  
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
        if row[1]:
            qms_list.append((row[0], a, row[1]))

    for qms in qms_list:
        print(qms)
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
AND Item = %%s ; """ % esses
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
        sql_statement += "\n(%s, '%s - Status->%s', 'statusset')" % (siid, note, status)
        if index < len(siid_list) - 1:
            sql_statement += ","
        else:
            sql_statement += " ;"

    DBfunctions.sql_execute(sql_statement, False, 'updatedb')

    return True


def todo_list_room(building, room):
    sql_statement = """
SELECT CONCAT(BuildingName, " " , FrontDoor) as 'Unit' , Item , Trade , Status , GROUP_CONCAT(CONCAT(Note, " - ", DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %e %b')) order by Moment DESC separator '---') as 'Notes', Priority , siid
from all_notes_cte
where BuildingName = ?
and FrontDoor = ?
and SortInspect < 100
GROUP by siid 
-- ORDER by FIELD(Status, 'todo','unmarked','complete'), Item ;
ORDER by SortInspect, Item ;
"""
    qms = (building, room)
    todo_json = DBfunctions.sql_execute(sql_statement, qms, 'json')

    return todo_json


def todo_list_current(specify_trade=False):
    if not specify_trade:
        sql_statement = """
SELECT Priority , CONCAT(BuildingName, " " , FrontDoor) as 'Unit' , Step , Item , GROUP_CONCAT(CONCAT(Note, " - ", DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %e %b')) order by Moment DESC separator '---') as 'Notes', Trade , Status , siid
from all_notes_cte
WHERE Occupancy LIKE '%vacant%'
AND Status = 'todo'
AND Priority NOT LIKE 'p0%'
AND Step < 100
GROUP by siid 
ORDER by Priority , BuildingName , FrontDoor , Step , Item ;
"""
        qms = False
        todo_json = DBfunctions.sql_execute(sql_statement, qms, 'json')
    elif specify_trade:
        sql_statement = """
SELECT Priority , CONCAT(BuildingName, " " , FrontDoor) as 'Unit' , Step , Item , GROUP_CONCAT(CONCAT(Note, " - ", DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %e %b')) order by Moment DESC separator '---') as 'Notes', Trade , Status , siid
from all_notes_cte
WHERE (Occupancy LIKE '%vacant%'
AND Status = 'todo'
AND Priority NOT LIKE 'p0%'
AND Step < 100
AND Trade = ?)
OR (Trade = 'tempfilter'
AND Status = 'todo')
GROUP by siid 
ORDER by Priority , BuildingName , FrontDoor , Step , Item ;
"""
        qms = (specify_trade,)
        todo_json = DBfunctions.sql_execute(sql_statement, qms, 'json')

    return todo_json

def rooms_by_priority():
    sql_statement = """
SELECT Priority , CONCAT(BuildingName, " " , FrontDoor) as 'Unit' , Step , Item , GROUP_CONCAT(CONCAT(Note, " - ", DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %e %b')) order by Moment DESC separator '---') as 'Notes', Trade , Status , siid
from all_notes_cte
WHERE Occupancy LIKE '%vacant%'
AND Priority NOT LIKE 'p0%'
GROUP by BuildingName , FrontDoor
ORDER by Priority , BuildingName , FrontDoor , Step , Item ;
"""
    qms = False
    todo_json = DBfunctions.sql_execute(sql_statement, qms, 'json')

    return todo_json

def turned_rooms():
    sql_statement = """
SELECT Priority , CONCAT(BuildingName, " " , FrontDoor) as 'Unit' , Step , Item , GROUP_CONCAT(CONCAT(Note, " - ", DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %e %b')) order by Moment DESC separator '---') as 'Notes', Status , OriginalOccupancy , siid
from all_notes_cte
WHERE (Status = 'todo'
OR Item = 'Priority and Occupancy')
AND Priority LIKE 'p0%'
GROUP by siid 
ORDER by BuildingName , FrontDoor , Step , Item ;
"""
    qms = False
    todo_json = DBfunctions.sql_execute(sql_statement, qms, 'json')

    return todo_json

def turned_recent():
    sql_statement = """
SELECT CONCAT(BuildingName, " " , FrontDoor) as 'Unit' , DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %e %b') as 'Date'
from all_notes_cte
WHERE Note LIKE '%->p0%'
and Priority LIKE 'p0'
GROUP by BuildingName , FrontDoor 
ORDER by Moment DESC , BuildingName , FrontDoor ;
"""
    qms = False
    todo_json = DBfunctions.sql_execute(sql_statement, qms, 'json')

    return todo_json

def all_notes_ticker(look_back):
    sql_statement = """
SELECT DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %e %b') as 'Day', DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%H:%i') as 'Time', CONCAT(BuildingName , ' ' ,  FrontDoor) as 'Unit' , Item , Note 
from all_notes_cte
WHERE Moment >= DATE_SUB(NOW(),INTERVAL ? day)
Order by Moment DESC ;
"""
    qms = (look_back,)
    todo_json = DBfunctions.sql_execute(sql_statement, qms, 'json')

    return todo_json

def completed_ticker(look_back):
    sql_statement = """
SELECT DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%a, %e %b') as 'Day', DATE_FORMAT(DATE_SUB(Moment,INTERVAL 5 hour), '%H:%i') as 'Time', CONCAT(BuildingName , ' ' ,  FrontDoor) as 'Unit' , Item , Note 
from all_notes_cte
WHERE Status = 'complete'
and siid IN (
SELECT ItemID from str4_notes
WHERE Note LIKE '%Status->todo%')
and Note LIKE '%Status->complete%'
and Moment >= DATE_SUB(NOW(),INTERVAL ? day)
Order by Moment DESC ;
"""
    qms = (look_back,)
    todo_json = DBfunctions.sql_execute(sql_statement, qms, 'json')

    return todo_json

def post_to_db(post_values):
    siids_unmarked_list = []
    siids_todo_list = []
    siids_complete_list = []
    siids_addnotes_list = []
    for key,value in post_values.items():
        if key.split(' ')[0] == 'siidnote' and value:
            siids_addnotes_list.append(key.split(' ')[1])
        elif key.split(' ')[0] == 'siid' and value == 'unmarked':
            siids_unmarked_list.append(key.split(' ')[1])
        elif key.split(' ')[0] == 'siid' and value == 'todo':
            siids_todo_list.append(key.split(' ')[1])
        elif key.split(' ')[0] == 'siid' and value == 'complete':
            siids_complete_list.append(key.split(' ')[1])
    siids_unmarked_list = tuple(siids_unmarked_list)
    siids_todo_list = tuple(siids_todo_list)
    siids_complete_list = tuple(siids_complete_list)

# 1 unmarked find changed and prepare note
    if siids_unmarked_list:
        esses = ','.join(['%s'] * len(siids_unmarked_list))
        sql_statement = """
SELECT siid from str3_items
WHERE siid in (%s)
and Status != 'unmarked' ;""" % esses
        siids_setunmarked_list, columns = DBfunctions.sql_execute(sql_statement, siids_unmarked_list, 'table')
        siidsunmarked_notestuples_list = []
        for siid in siids_setunmarked_list:
            siidsunmarked_notestuples_list.append((siid[0], post_values['siidnote '+str(siid[0])], 'unmarked'))
    else:
        siids_setunmarked_list = []

# 2 todo find changed and prepare note
    if siids_todo_list:
        esses = ','.join(['%s'] * len(siids_todo_list))
        sql_statement = """
SELECT siid from str3_items
WHERE siid in (%s)
and Status != 'todo' ;""" % esses
        siids_settodo_list, columns = DBfunctions.sql_execute(sql_statement, siids_todo_list, 'table')
        siidstodo_notestuples_list = []
        for siid in siids_settodo_list:
            siidstodo_notestuples_list.append((siid[0], post_values['siidnote '+str(siid[0])], 'todo'))
    else:
        siids_settodo_list = []


# 3 complete find changed and prepare note
    if siids_complete_list:
        esses = ','.join(['%s'] * len(siids_complete_list))
        sql_statement = """
SELECT siid from str3_items
WHERE siid in (%s)
and Status != 'complete' ;""" % esses
        siids_setcomplete_list, columns = DBfunctions.sql_execute(sql_statement, siids_complete_list, 'table')
        siidscomplete_notestuples_list = []
        for siid in siids_setcomplete_list:
            siidscomplete_notestuples_list.append((siid[0], post_values['siidnote '+str(siid[0])], 'complete'))
    else:
        siids_setcomplete_list = []

    if siids_setunmarked_list:
        siids_setunmarked_list = [str(siid[0]) for siid in siids_setunmarked_list]
    if siids_settodo_list:
        siids_settodo_list = [str(siid[0]) for siid in siids_settodo_list]
    if siids_setcomplete_list:
        siids_setcomplete_list = [str(siid[0]) for siid in siids_setcomplete_list]

# 4 notes without status change
    if siids_addnotes_list:
        siids_addnotes_list = [siid for siid in siids_addnotes_list if siid not in (siids_setunmarked_list+siids_settodo_list+siids_setcomplete_list)]

# 4 no status change prepare note
    if siids_addnotes_list:
        siidsaddnotes_notestuples_list = []
        for siid in siids_addnotes_list:
            siidsaddnotes_notestuples_list.append((siid, post_values['siidnote '+str(siid)]))


# 1 unmarked update statuses
    if siids_setunmarked_list:
        siids_setunmarked_list = tuple(siids_setunmarked_list)
        esses = ','.join(['%s'] * len(siids_setunmarked_list))
        sql_statement = """
UPDATE str3_items
SET Status = 'unmarked'
WHERE siid in (%s) ; """ % esses
        DBfunctions.sql_execute(sql_statement, siids_setunmarked_list, 'updatedb')
    
# 1 unmarked insert notes
        sql_statement = "INSERT INTO str4_notes (ItemID, Note, NoteType)\nVALUES "

        for index, siid_note_status in enumerate(siidsunmarked_notestuples_list):
            sql_statement += "\n(%s, '%s - Status->%s', 'statusset')" % siid_note_status
            if index < len(siidsunmarked_notestuples_list) - 1:
                sql_statement += ","
            else:
                sql_statement += " ;"

        DBfunctions.sql_execute(sql_statement, False, 'updatedb')

# 2 todo update statuses
    if siids_settodo_list:
        siids_settodo_list = tuple(siids_settodo_list)
        esses = ','.join(['%s'] * len(siids_settodo_list))
        sql_statement = """
UPDATE str3_items
SET Status = 'todo'
WHERE siid in (%s) ; """ % esses
        DBfunctions.sql_execute(sql_statement, siids_settodo_list, 'updatedb')
    
# 2 todo insert notes
        sql_statement = "INSERT INTO str4_notes (ItemID, Note, NoteType)\nVALUES "

        for index, siid_note_status in enumerate(siidstodo_notestuples_list):
            sql_statement += "\n(%s, '%s - Status->%s', 'statusset')" % siid_note_status
            if index < len(siidstodo_notestuples_list) - 1:
                sql_statement += ","
            else:
                sql_statement += " ;"

        DBfunctions.sql_execute(sql_statement, False, 'updatedb')

# 3 complete update statuses
    if siids_setcomplete_list:
        siids_setcomplete_list = tuple(siids_setcomplete_list)
        esses = ','.join(['%s'] * len(siids_setcomplete_list))
        sql_statement = """
UPDATE str3_items
SET Status = 'complete'
WHERE siid in (%s) ; """ % esses
        DBfunctions.sql_execute(sql_statement, siids_setcomplete_list, 'updatedb')
    
# 3 complete insert notes
        sql_statement = "INSERT INTO str4_notes (ItemID, Note, NoteType)\nVALUES "

        for index, siid_note_status in enumerate(siidscomplete_notestuples_list):
            sql_statement += "\n(%s, '%s - Status->%s', 'statusset')" % siid_note_status
            if index < len(siidscomplete_notestuples_list) - 1:
                sql_statement += ","
            else:
                sql_statement += " ;"

        DBfunctions.sql_execute(sql_statement, False, 'updatedb')

# 4 no status change insert notes
    if siids_addnotes_list:
        sql_statement = "INSERT INTO str4_notes (ItemID, Note, NoteType)\nVALUES "

        for index, siid_note in enumerate(siidsaddnotes_notestuples_list):
            sql_statement += "\n(%s, '%s', 'miscnote')" % siid_note
            if index < len(siidsaddnotes_notestuples_list) - 1:
                sql_statement += ","
            else:
                sql_statement += " ;"

        DBfunctions.sql_execute(sql_statement, False, 'updatedb')


    return True


def current_vacant_tool(building, all_rooms_txt):
    regex_pattern = re.compile(r'(?<=\n)\d{3}(?=[\w ]*OUT OF ORDER)', re.MULTILINE)
    vacants_current = re.findall(regex_pattern, all_rooms_txt)
    regex_pattern = re.compile(r'(?<=\n)\d{3}(?=[\w ]*CHECKED OUT)', re.MULTILINE)
    vacants_current += re.findall(regex_pattern, all_rooms_txt)
    regex_pattern = re.compile(r'(?<=\n)\d{3}(?=[\w ]*AVAILABLE)', re.MULTILINE)
    vacants_current += re.findall(regex_pattern, all_rooms_txt)
    vacants_current_tuple = tuple([int(x) for x in vacants_current])

    esses = ','.join(['%s'] * len(vacants_current_tuple))
    sql_statement = """
SELECT CONCAT(BuildingName, " " , FrontDoor) as 'Unit', FrontDoor
from all_items_cte
WHERE (BuildingName = %%s
OR BuildingName = %%s)
AND FrontDoor in (%s)
AND Occupancy = 'occupied'
GROUP by BuildingName , FrontDoor
ORDER by BuildingName , FrontDoor ;
""" % esses
    if building == 'a':
        qms = ('a',) + ('a',) + vacants_current_tuple
    elif building == 'b':
        qms = ('b',) + ('c',) + vacants_current_tuple
    new_vacants = DBfunctions.sql_execute(sql_statement, qms, 'json')

    regex_pattern = re.compile(r'(?<=\n)\d{3}(?=[\w ]*INHOUSE)', re.MULTILINE)
    occupieds_current = re.findall(regex_pattern, all_rooms_txt)
    occupieds_current_tuple = tuple([int(x) for x in occupieds_current])

    esses = ','.join(['%s'] * len(occupieds_current))
    sql_statement = """
SELECT CONCAT(BuildingName, " " , FrontDoor) as 'Unit', FrontDoor
from all_items_cte
WHERE (BuildingName = %%s
OR BuildingName = %%s)
AND FrontDoor in (%s)
AND Occupancy = 'vacant'
GROUP by BuildingName , FrontDoor
ORDER by BuildingName , FrontDoor ;
""" % esses
    if building == 'a':
        qms = ('a',) + ('a',) + occupieds_current_tuple
    elif building == 'b':
        qms = ('b',) + ('c',) + occupieds_current_tuple
    new_occupieds = DBfunctions.sql_execute(sql_statement, qms, 'json')

    return new_vacants, new_occupieds