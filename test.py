import sqlstatements

# sqlstatements.consolidate(b='WallpaperRemove', a='Paint, Putty, Caulk, Stain, Wallpaper')

# sqlstatements.generate_items()

# sqlstatements.test()

# sqlstatements.hours_report('2024-11-04')

# building = 'A'
# rooms_list = () # if single room number, requires a comma after
# item = 'climate control' # not case-sensitive
# status = 'complete' # todo / complete / unmarked
# note = 'Has new register on it. Looks new. NMR'
# sqlstatements.change_status(building, rooms_list, item, status, note)

print_this = sqlstatements.todo_list_room('A','428')
print(print_this)