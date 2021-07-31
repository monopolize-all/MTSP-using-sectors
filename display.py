from matplotlib import pyplot

def reset_plot_colours():
    pyplot.gca().set_prop_cycle(None)

def set_axes_limits(xlim, ylim):
    pyplot.xlim(xlim)
    pyplot.ylim(ylim)

def plot_warehouse(warehouse_position):
    pyplot.plot(*warehouse_position, "ko")

def plot_villages(village_positions):
    positions_x_to_plot = [village_position[0] for village_position in village_positions]
    positions_y_to_plot = [village_position[1] for village_position in village_positions]
    pyplot.plot(positions_x_to_plot, positions_y_to_plot, "o")

def plot_route(points):
    positions_x_to_plot = [village_position[0] for village_position in points]
    positions_y_to_plot = [village_position[1] for village_position in points]
    pyplot.plot(positions_x_to_plot, positions_y_to_plot)

def show_plot():
    pyplot.show()

def show_villages(axes_limits, warehouse_position, village_positions):
    print(village_positions)

    set_axes_limits(*axes_limits)
    plot_warehouse(warehouse_position)
    plot_villages(village_positions)
    show_plot()

def show_sectors(axes_limits, warehouse_position, sectors):
    print([[list(village.position) for village in sector.villages] for sector in sectors])

    set_axes_limits(*axes_limits)
    for sector in sectors:
        village_positions = [village.position for village in sector.villages]
        plot_villages(village_positions)
    plot_warehouse(warehouse_position)
    show_plot()

def show_solution(axes_limits, solution, warehouse_position, sectors):
    set_axes_limits(*axes_limits)
    for sector in sectors:
        village_positions = [village.position for village in sector.villages]
        plot_villages(village_positions)
    reset_plot_colours()
    for sector_route in solution:
        plot_route(sector_route)
    plot_warehouse(warehouse_position)
    show_plot()
