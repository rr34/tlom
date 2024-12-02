import sqlstatements

# sqlstatements.consolidate(b='Lights - Lamps', a='Lights - Fixtures')

# sqlstatements.generate_items()

# sqlstatements.test()

sqlstatements.hours_report(['2024-10-28', '2024-11-11', '2024-11-25', '2024-12-09'], '2024-12-09')

# sqlstatements.misc_reports('2024-11-11', '2024-11-25')

# building = 'c'
# rooms_list = () # if single room number, requires a comma after
# item = 'climate control' # not case-sensitive
# status = 'todo' # todo / complete / unmarked
# note = 'Marc ordered 13 for 12 rooms plus spare, expected to arrive 26 Nov.'
# sqlstatements.change_status(building, rooms_list, item, status, note)

# All A rooms: 101,102,103,104,105,106,107,108,110,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,201,202,203,204,205,206,207,208,210,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,301,302,303,304,305,306,307,308,310,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,401,402,403,404,405,406,407,408,410,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,428
# print_this = sqlstatements.todo_list_room('A','428')
# print(print_this)