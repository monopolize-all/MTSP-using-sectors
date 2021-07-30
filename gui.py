import tkinter
import random
import MTSP
import diagram
  
window = tkinter.Tk()  
window.title("MTSP Solver")

village_positions_generation_mode = tkinter.StringVar()
village_positions_generation_mode.set("Automatic")

def on_village_positions_generation_mode_change():
    if village_positions_generation_mode.get() == "Automatic":
        village_positions_label.grid_forget()
        village_positions_entry.grid_forget()
        warehouse_position_label.grid_forget()
        warehouse_position_entry.grid_forget()
        number_of_villages_label.grid(row = 2, column = 0)
        number_of_villages_entry.grid(row = 2, column = 1)

    elif village_positions_generation_mode.get() == "Manual":
        number_of_villages_label.grid_forget()
        number_of_villages_entry.grid_forget()
        village_positions_label.grid(row = 2, column = 0)
        village_positions_entry.grid(row = 2, column = 1)
        warehouse_position_label.grid(row = 3, column = 0)
        warehouse_position_entry.grid(row = 3, column = 1)

tkinter.Label(window, text = "Village Positions Generation Mode: ").grid(row = 0)

tkinter.Radiobutton(window, text = "Automatic", 
                    variable = village_positions_generation_mode, 
                    value = "Automatic",
                    
                    command=on_village_positions_generation_mode_change).grid(row = 0, column = 1)

tkinter.Radiobutton(window, text = "Manual", 
                    variable = village_positions_generation_mode, 
                    value = "Manual", 
                    command=on_village_positions_generation_mode_change).grid(row = 1, column = 1)

number_of_villages_label = tkinter.Label(window, text = "Number of Villages: ")
number_of_villages_label.grid(row = 2, column = 0)
number_of_villages_entry = tkinter.Entry()
number_of_villages_entry.grid(row = 2, column = 1)

village_positions_label = tkinter.Label(window, text = "Village positions: ")
village_positions_label.grid(row = 2, column = 0)
village_positions_entry = tkinter.Entry()
village_positions_entry.grid(row = 2, column = 1)

warehouse_position_label = tkinter.Label(window, text = "Warehouse position: ")
warehouse_position_label.grid(row = 3, column = 0)
warehouse_position_entry = tkinter.Entry()
warehouse_position_entry.grid(row = 3, column = 1)

village_positions_label.grid_forget()
village_positions_entry.grid_forget()
warehouse_position_label.grid_forget()
warehouse_position_entry.grid_forget()

tkinter.Label(window, text = "Number of Sectors: ").grid(row = 4, column = 0)
number_of_sectors_entry = tkinter.Entry()
number_of_sectors_entry.grid(row = 4, column = 1)

MAP_SIZE_FOR_RANDOM_GENERATION = 1000
def generate_random_village_positions(number_of_villages):
    village_positions = []

    for index in range(number_of_villages):
        village_position = random.randint(0, MAP_SIZE_FOR_RANDOM_GENERATION), random.randint(0, MAP_SIZE_FOR_RANDOM_GENERATION)
        village_positions.append(village_position)

    return village_positions

def generate_random_warehouse_position():
    warehouse_position = random.randint(0, MAP_SIZE_FOR_RANDOM_GENERATION), random.randint(0, MAP_SIZE_FOR_RANDOM_GENERATION)
    
    return warehouse_position

def solve_MTSP():
    if village_positions_generation_mode.get() == "Automatic":
        number_of_villages = eval(number_of_villages_entry.get())
        number_of_sectors = int(number_of_sectors_entry.get())

        village_positions = generate_random_village_positions(number_of_villages)
        warehouse_position = generate_random_warehouse_position()

    elif village_positions_generation_mode.get() == "Manual":
        village_positions = eval(village_positions_entry.get())
        warehouse_position = eval(warehouse_position_entry.get())
        number_of_sectors = int(number_of_sectors_entry.get())

    mtsp = MTSP.MTSP(village_positions, warehouse_position, number_of_sectors)

    if show_diagram.get():
        diagram.plot_warehouse(warehouse_position)
        diagram.plot_villages(village_positions)
        diagram.show_plot()

    solution = mtsp.solve()

    if show_diagram.get():
        print(solution)
        for sector_route in solution:
            diagram.plot_route(sector_route)
        diagram.plot_warehouse(warehouse_position)
        diagram.plot_villages(village_positions)
        diagram.show_plot()

def on_show_diagram():
    if show_diagram.get():
        show_diagram_for_each_step_checkbutton.grid(row = 6, columnspan = 2)

    else:
        show_diagram_for_each_step_checkbutton.grid_forget()

show_diagram = tkinter.BooleanVar()
show_diagram_checkbutton = tkinter.Checkbutton(window, text = "Show diagram", command = on_show_diagram,
                variable = show_diagram, onvalue = True, offvalue = False)
show_diagram_checkbutton.grid(row = 5, columnspan = 2)

show_diagram_for_each_step = tkinter.BooleanVar()
show_diagram_for_each_step_checkbutton = tkinter.Checkbutton(window, text = "Show diagram for each step", 
                command = on_show_diagram, variable = show_diagram_for_each_step, onvalue = True, 
                offvalue = False)

solve_button = tkinter.Button(window, text = "Solve", command = solve_MTSP).grid(row = 7, columnspan = 2)

def run_program():
    window.mainloop()

if __name__ == "__main__":
    run_program()
