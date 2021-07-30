from matplotlib import pyplot

def plot_warehouse(warehouse_position):
    pyplot.plot(*warehouse_position, "bo")

def plot_villages(village_positions):
    positions_x_to_plot = [village_position[0] for village_position in village_positions]
    positions_y_to_plot = [village_position[1] for village_position in village_positions]
    pyplot.plot(positions_x_to_plot, positions_y_to_plot, "ro")

def plot_route(points):
    positions_x_to_plot = [village_position[0] for village_position in points]
    positions_y_to_plot = [village_position[1] for village_position in points]
    pyplot.plot(positions_x_to_plot, positions_y_to_plot)

def show_plot():
    pyplot.show()
