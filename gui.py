import tkinter
import json
import random
import MTSP
import display
  
window = tkinter.Tk()  
window.title("MTSP Solver")

village_positions_generation_mode = tkinter.StringVar()
village_positions_generation_mode.set("Automatic")

def on_village_positions_generation_mode_change():
    if village_positions_generation_mode.get() == "Automatic":
        data_label.grid_forget()
        data_entry.grid_forget()
        number_of_villages_label.grid(row = 2, column = 0)
        number_of_villages_entry.grid(row = 2, column = 1)

    elif village_positions_generation_mode.get() == "Manual":
        number_of_villages_label.grid_forget()
        number_of_villages_entry.grid_forget()
        data_label.grid(row = 2, column = 0)
        data_entry.grid(row = 2, column = 1)

tkinter.Label(window, text = "Village Positions Generation Mode: ").grid(row = 0)

tkinter.Radiobutton(window, text = "Automatic", 
                    variable = village_positions_generation_mode, 
                    value = "Automatic",
                    
                    command=on_village_positions_generation_mode_change).grid(row = 0, column = 1)

tkinter.Radiobutton(window, text = "Manual(JSON string)", 
                    variable = village_positions_generation_mode, 
                    value = "Manual", 
                    command=on_village_positions_generation_mode_change).grid(row = 1, column = 1)

number_of_villages_label = tkinter.Label(window, text = "Number of Villages: ")
number_of_villages_label.grid(row = 2, column = 0)
number_of_villages_entry = tkinter.Entry()
number_of_villages_entry.grid(row = 2, column = 1)

data_label = tkinter.Label(window, text = "JSON Data: ")
data_label.grid(row = 2, column = 0)
data_entry = tkinter.Entry()
data_entry.grid(row = 2, column = 1)

data_label.grid_forget()
data_entry.grid_forget()

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

AXES_PADDING = 20
def solve_MTSP():
    
    if village_positions_generation_mode.get() == "Automatic":
        number_of_villages = eval(number_of_villages_entry.get())
        number_of_sectors = int(number_of_sectors_entry.get())

        village_positions = generate_random_village_positions(number_of_villages)
        warehouse_position = generate_random_warehouse_position()

        data = {
            "village positions": village_positions,
            "warehouse position": warehouse_position
        }

        json_string = json.dumps(data)

        generated_json_data_entry.insert(0, json_string)

        generated_json_data_label.grid(row = 8, column = 0)
        generated_json_data_entry.grid(row = 8, column = 1)

    elif village_positions_generation_mode.get() == "Manual":
        data = json.loads(data_entry.get())
        village_positions = data["village positions"]
        warehouse_position = data["warehouse position"]
        number_of_sectors = int(number_of_sectors_entry.get())

    mtsp = MTSP.MTSP(village_positions, warehouse_position, number_of_sectors)

    axes_limits = [[mtsp.bottom_left_point[0] - AXES_PADDING, mtsp.top_right_point[0] + AXES_PADDING],
                    [mtsp.bottom_left_point[1] - AXES_PADDING, mtsp.top_right_point[1] + AXES_PADDING]]
    
    window.update()

    if show_display.get():
        display.show_villages(axes_limits, warehouse_position, village_positions)
    
    if show_display_for_each_step.get():
        def display_function(sectors):
            display.show_sectors(axes_limits, warehouse_position, sectors)
        solution = mtsp.solve_showing_each_step(display_function)

    else:
        solution = mtsp.solve_quickly()

    if show_display.get():
        display.show_solution(axes_limits, solution, warehouse_position, mtsp.sectors)

def on_show_display():
    if show_display.get():
        show_display_for_each_step_checkbutton.grid(row = 6, columnspan = 2)

    else:
        show_display_for_each_step_checkbutton.grid_forget()

show_display = tkinter.BooleanVar()
show_display_checkbutton = tkinter.Checkbutton(window, text = "Show display", command = on_show_display,
                variable = show_display, onvalue = True, offvalue = False)
show_display_checkbutton.grid(row = 5, columnspan = 2)

show_display_for_each_step = tkinter.BooleanVar()
show_display_for_each_step_checkbutton = tkinter.Checkbutton(window, text = "Show display for each step", 
                command = on_show_display, variable = show_display_for_each_step, onvalue = True, 
                offvalue = False)

solve_button = tkinter.Button(window, text = "Solve", command = solve_MTSP).grid(row = 7, columnspan = 2)

generated_json_data_label = tkinter.Label(window, text = "Generated json data: ")
generated_json_data_entry = tkinter.Entry()

def run_program():
    window.mainloop()

if __name__ == "__main__":
    run_program()
