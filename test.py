import sqlstatements

# sqlstatements.consolidate(b='WallpaperRemove', a='Paint, Putty, Caulk, Stain, Wallpaper')

# sqlstatements.generate_items()

# sqlstatements.test()

# sqlstatements.hours_report('2024-11-04')

building = 'A'
rooms_list = () # if single room number, requires a comma after
item = 'Kitchen - Stove Top' # not case-sensitive
status = 'todo' # todo / complete / unmarked
note = 'Needs replaced according to Drew list.'
sqlstatements.change_status(building, rooms_list, item, status, note)