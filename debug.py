import gui

gui.village_positions_generation_mode.set("Manual")

data_entry = '''
    {
        "village positions": [[213, 90], [477, 383], [15, 746], [771, 3], [384, 706], [54, 671], [736, 674], [391, 433], [786, 38], [351, 778], [409, 242], [834, 955], [215, 509], [238, 82], [706, 384], [302, 467], [979, 691], [554, 267], [964, 457], [731, 357]], 
        "warehouse position": [500, 500]
    }
'''
data_entry = '''
    {
        "village positions": [[213, 90], [477, 383], [409, 242], [834, 955], [215, 509], [238, 82], [706, 384], [302, 467], [979, 691], [554, 267], [964, 457], [731, 357]], 
        "warehouse position": [500, 500]
    }
'''

gui.data_entry.insert(0, data_entry)
gui.number_of_sectors_entry.insert(0, "2")
gui.show_display.set(True)
gui.show_display_for_each_step.set(True)

gui.window.after(0, gui.solve_MTSP())

gui.window.mainloop()
