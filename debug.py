import gui

gui.village_positions_generation_mode.set("Manual")

data_entry = '''
    {
        "village positions": [[501, 118], [266, 414], [289, 838], [907, 821], [29, 158], [931, 523], [733, 428], [875, 784], [992, 233], [758, 859], [102, 322], [775, 560], [826, 656], [88, 688], [464, 752], [896, 741], [745, 571], [233, 124], [124, 64], [972, 811], [706, 972], [409, 434], [99, 373], [786, 143], [545, 78], [629, 687], [751, 895], [29, 274], [65, 359], [435, 120], [510, 417], [869, 269], [245, 653], [432, 679], [561, 789], [315, 598], [725, 496], [567, 913], [398, 45], [835, 302], [453, 601], [469, 514], [968, 704], [547, 416], [700, 361], [241, 48], [618, 953], [77, 343], [804, 407], [72, 369]], 
    
        "warehouse position": [500, 500]
    }
'''

gui.data_entry.insert(0, data_entry)
gui.number_of_sectors_entry.insert(0, "5")
gui.show_display.set(True)
gui.show_display_for_each_step.set(False)

gui.window.after(0, gui.solve_MTSP())

gui.window.mainloop()
