import gui

gui.number_of_villages_entry.insert(0, "10")
gui.number_of_sectors_entry.insert(0, "2")
gui.show_diagram.set(True)
gui.show_diagram_for_each_step.set(True)

gui.solve_MTSP()
