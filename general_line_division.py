import random, math, typing, statistics, numpy, json, os, time
from pygame_display import *

# Credits to python_tsp: https://github.com/fillipe-gsm/python-tsp
from python_tsp.exact import solve_tsp_dynamic_programming

# region constants

window_size = (800, 800)
window_constants_init()

DEBUG = False

JSON_DATA_FILE = "data.json"
IMAGE_FOLDER_PATH = "Solution images"

# endregion

# region framework

def generate_node_position(number_of_nodes):
    nodes_positions = []

    # 0 index node is the hub
    nodes_positions.append(window_center)
    number_of_nodes = number_of_nodes - 1

    for i in range(0, number_of_nodes) :
        # Resistricting locations by node_size//2 to ensure all nodes are inside the window
        nodes_positions.append((random.randint(node_size//2, window_size[0] - node_size//2), random.randint(node_size//2, window_size[1] - node_size//2)))

    return nodes_positions

class Hub(Node):
    hub_color = BLACK
    def __init__(self, hub_position):
        super().__init__(hub_position, self.hub_color)

        sprites_to_blit.add(self)

# TODO - Check if this square distance function works
# We are using square of distance to reduce computational requirements
def get_square_of_distance_between_points(point1, point2):
    return (point1[0]-point2[0]) ** 2 + (point1[1]-point2[1]) ** 2

class Place(Node):
    place_color = GREY

    def __init__(self, place_position):
        super().__init__(place_position, self.place_color)
        self.place_position = place_position
        sprites_to_blit.add(self)

        self.place_weight = None
        self.calculate_place_weight()

    def set_neighbouring_places(self, first_place_clockwise, first_place_anticlockwise):
        self.first_place_clockwise = first_place_clockwise
        self.first_place_anticlockwise = first_place_anticlockwise

    def calculate_place_weight(self):
        self.place_weight = get_square_of_distance_between_points(self.place_position, hub_position)

SECTOR_COLORS = [VIOLET, INDIGO, BLUE, GREEN, YELLOW, ORANGE, RED][::-1]

class Sector:
    
    def __init__(self, first_place: Place, last_place: Place):
        # First place -> Turn anticlockwise -> last place 
        self.first_place = first_place
        self.last_place = last_place

        self.places_in_sector = []  # From first place to last place
        self.init_places_in_sector()

        self.sector_color = SECTOR_COLORS.pop(0)
        SECTOR_COLORS.append(self.sector_color)
        self.color_places_in_sector()

        self.sector_weight = None
        self.calculate_sector_weight()

    def init_places_in_sector(self):
        next_place = self.first_place
        self.places_in_sector.append(next_place)
        while next_place != self.last_place:
            next_place = next_place.first_place_anticlockwise
            self.places_in_sector.append(next_place)

    def color_places_in_sector(self):
        for place in self.places_in_sector:
            place.change_color(self.sector_color)

    def calculate_sector_weight(self):
        # NOTE: When modifiying this function, also modify functions:
        # 1) add_place
        # 2) remove_place
        # 3) get_weight_if_place_added
        # 4) get_weight_if_place_removed
        self.sector_weight = 0

        for place in self.places_in_sector:
            self.sector_weight += place.place_weight

    def add_place(self, place: Place):
        if place in self.places_in_sector:
            raise Exception("Place being added is already in this sector.")

        place_to_clockwise = place.first_place_clockwise
        place_to_anticlockwise = place.first_place_anticlockwise

        if place_to_anticlockwise == self.places_in_sector[0]:
            self.first_place = place
            self.places_in_sector.insert(0, place)

        elif place_to_clockwise  == self.places_in_sector[-1]:
            self.last_place = place
            self.places_in_sector.insert(len(self.places_in_sector), place)

        else:
            if DEBUG:
                print("place being added, corners of sector: ", 
                        place.place_position, self.places_in_sector[0].place_position, 
                        self.places_in_sector[-1].place_position)
                print("places in sector: ", list(map(lambda x:x.place_position, self.places_in_sector)))
            raise Exception("Place being added is not neighbouring a place on either end of self.places_in_sector")

        place.change_color(self.sector_color)

        self.sector_weight += place.place_weight
    
    def remove_place(self, place: Place):
        if place not in self.places_in_sector:
            raise Exception("Place being removed is not in this sector.")

        if place == self.places_in_sector[0]:
            self.places_in_sector.pop(0)
            self.first_place = self.places_in_sector[0]

        elif place == self.places_in_sector[-1]:
            self.places_in_sector.pop(-1)
            self.last_place = self.places_in_sector[-1]

        else:
            raise Exception("Place being removed is not in either end of self.places_in_sector")

        place.change_color(Place.place_color)

        self.sector_weight -= place.place_weight

    def get_weight_if_place_added(self, place:Place):
        return self.sector_weight + place.place_weight

    def get_weight_if_place_removed(self, place:Place):
        return self.sector_weight - place.place_weight

class SortedQueue:

    def __init__(self):
        self.queue = []  # Smallest element has index 0
        self.length = 0

    def add_element(self, key, value):
        i = 0
        while i < self.length:
            if self.queue[i][1] > value:
                self.queue.insert(i, (key, value))
                break
            i += 1

        else:
            self.queue.append((key, value))
        
        self.length += 1

    def get_smallest_element(self):
        key, value = self.queue[0]
        return key, value

    def pop_smallest_element(self):
        key, value = self.queue.pop(0)
        return key, value

    def return_queue(self):
        return self.queue

    def return_keys(self):
        return list(map(lambda x: x[0], self.queue))

    def empty_queue(self):
        self.queue = []
        self.length = 0

# TODO - See if origin_position works as intended.
def get_point_angle(point, origin_position):
    x, y = point

    #x -= half_window_width
    #y = half_window_height - y
    x -= origin_position[0]
    y = origin_position[1] - y

    point_angle = math.atan2(y, x)

    return point_angle

def get_points_sorted_by_angle_from_positive_x_axis(node_positions):
    origin_position = node_positions[0]

    points_sorted_by_angle_queue = SortedQueue()

    for point in node_positions[1:]:
        angle = get_point_angle(point, origin_position)
        points_sorted_by_angle_queue.add_element(point, angle)

    points_sorted_by_angle = points_sorted_by_angle_queue.return_keys()

    points_sorted_by_angle_index = []
    for point in points_sorted_by_angle:
        points_sorted_by_angle_index.append(node_positions.index(point))

    return points_sorted_by_angle_index

def set_neighbouring_places_for_nodes(places: typing.Iterable[Place], points_sorted_by_angle):
    number_of_nodes = len(places)

    for i, point in enumerate(points_sorted_by_angle):
        first_place_clockwise = places[points_sorted_by_angle[i-1]-1]  # Excluding hub since point considers hub as well
        if i+1 < number_of_nodes:
            first_place_anticlockwise = places[points_sorted_by_angle[i+1]-1]  # Excluding hub since point considers hub as well
        else:
            first_place_anticlockwise = places[points_sorted_by_angle[0]-1]  # Excluding hub since point considers hub as well
        places[point-1].set_neighbouring_places(first_place_clockwise, first_place_anticlockwise)  # Excluding hub since point considers hub as well

def initialise_sectors(places, points_sorted_by_angle_index, number_of_sectors, number_of_nodes):
    sectors = []

    number_of_places_per_sector = number_of_nodes // number_of_sectors

    place_index = 0  # refers to points_sorted_by_angle_index which doesn't include hub

    if DEBUG:
        print(f"Points sorted by angle: {list(map(lambda x: places[x-1].place_position, points_sorted_by_angle_index))}")

    first_place_index = points_sorted_by_angle_index[place_index]
    place_index += number_of_places_per_sector
    while place_index < number_of_nodes:
        second_place_index = points_sorted_by_angle_index[place_index - 1]
        sectors.append(Sector(places[first_place_index-1], places[second_place_index-1]))
        if place_index >= number_of_nodes - 1:
            break
        first_place_index = points_sorted_by_angle_index[place_index]
        place_index += number_of_places_per_sector

    second_place_index = points_sorted_by_angle_index[-1]
    sectors.append(Sector(places[first_place_index-1], places[second_place_index-1]))

    return sectors

def move_place_between_sectors(original_sector, place_being_moved, final_sector):
    original_sector.remove_place(place_being_moved)
    final_sector.add_place(place_being_moved)

def switch_over_one_random_place():
    i = random.randint(1, number_of_sectors-1)
    move_place_between_sectors(sectors[i], sectors[i].first_place, sectors[i-1])

def get_variance_of_sector_weights(sector_weights):
    return statistics.variance(sector_weights)

# TODO - Fix bug here
def generate_possible_place_switches_sorted_on_varance_of_sector_weights(possible_place_switches):
    sector_weights_original = list(map(lambda x: x.sector_weight, sectors))
    for sector_index in range(number_of_sectors):
        # Effect of removing first place in sector
        sector_weights = list(sector_weights_original)
        sector_having_place_removed_index = sector_index
        sector_having_place_removed = sectors[sector_having_place_removed_index]
        place_being_moved = sector_having_place_removed.first_place
        sector_having_place_added_index = sector_index - 1
        sector_having_place_added = sectors[sector_having_place_added_index]
        sector_weights[sector_having_place_removed_index] = sector_having_place_removed.get_weight_if_place_removed(place_being_moved)
        sector_weights[sector_having_place_added_index] = sector_having_place_added.get_weight_if_place_added(place_being_moved)

        varance_of_sector_weights = get_variance_of_sector_weights(sector_weights)
        possible_place_switches.add_element((sector_having_place_removed, place_being_moved, sector_having_place_added), varance_of_sector_weights)

        # Effect of removing last place in sector
        sector_weights = list(sector_weights_original)
        sector_having_place_removed_index = sector_index
        sector_having_place_removed = sectors[sector_index]
        place_being_moved = sector_having_place_removed.last_place
        if sector_index + 1 < number_of_sectors:
            sector_having_place_added_index = sector_index + 1
        else:
            sector_having_place_added_index = 0
        sector_having_place_added = sectors[sector_having_place_added_index]
        sector_weights[sector_having_place_removed_index] = sector_having_place_removed.get_weight_if_place_removed(place_being_moved)
        sector_weights[sector_having_place_added_index] = sector_having_place_added.get_weight_if_place_added(place_being_moved)

        varance_of_sector_weights = get_variance_of_sector_weights(sector_weights)
        possible_place_switches.add_element((sector_having_place_removed, place_being_moved, sector_having_place_added), varance_of_sector_weights)
    
    for place_switch in possible_place_switches.return_keys():
        if place_switch:
            start, element, stop = place_switch
            print(start.sector_color, element.place_position, stop.sector_color)

def draw_lines_seperating_sectors():
    remove_lines_to_blit()
    first_point = sectors[-1].last_place.position
    for sector in sectors:
        second_point = sector.first_place.position
        median_point = (first_point[0] + second_point[0]) // 2, (first_point[1] + second_point[1]) // 2
        add_to_lines_to_blit(hub_position, median_point)
        first_point = sector.last_place.position

def get_current_sectors_weight():
    sector_weights = list(map(lambda x: x.sector_weight, sectors))
    varance_of_sector_weights = get_variance_of_sector_weights(sector_weights)
    return varance_of_sector_weights

def act_on_first_task_from_possible_place_switches():
    action, on_action_sections_coefficients = possible_place_switches.get_smallest_element()

    if action is None:
        if DEBUG:
            print("Relatively best solution found.")
        functions_to_run_every_second.pop(functions_to_run_every_second.index(act_on_first_task_from_possible_place_switches))
        solve_all_tsp()
        if input_mode == "j":
            goto_next_test_case()
        return

    possible_place_switches.pop_smallest_element()

    previous_actions_from_possible_place_switches.append(action)

    sector_having_place_removed, place_being_moved, sector_having_place_added = action
    move_place_between_sectors(sector_having_place_removed, place_being_moved, sector_having_place_added)

    draw_lines_seperating_sectors()
    possible_place_switches.empty_queue()
    possible_place_switches.add_element(None, get_current_sectors_weight())
    generate_possible_place_switches_sorted_on_varance_of_sector_weights(possible_place_switches)

    if DEBUG:
        print("Current weight variance: ", on_action_sections_coefficients)

    return False

def get_distance_matrix_from_points(points):
    distance_matrix = numpy.asarray([[get_square_of_distance_between_points(p1, p2) for p2 in points] for p1 in points])
    return distance_matrix

def solve_by_tsp(points):
    distance_matrix = get_distance_matrix_from_points(points)  # Note that each distance here is squared everywhere
    distance_matrix[:, 0] = 0
    permutation = solve_tsp_dynamic_programming(distance_matrix) [0]
    return permutation

def solve_all_tsp():
    for sector in sectors:
        points_in_sector = list(map(lambda x: x.place_position, sector.places_in_sector))
        points_in_sector.insert(0, hub_position)

        solution = solve_by_tsp(points_in_sector)

        solution_by_points_index = list(map(lambda x: node_positions.index(points_in_sector[x]), solution))

        sector_color = sector.sector_color

        first_point = node_positions[solution_by_points_index[0]]
        for solution_point_index in solution_by_points_index[1:]:
            second_point = node_positions[solution_point_index]
            add_to_lines_to_blit(first_point, second_point, sector_color)
            first_point = second_point

def initialise(number_of_nodes, number_of_sectors, node_positions):
    global hub_position, hub, places, sectors, possible_place_switches, previous_actions_from_possible_place_switches

    # 0 index node is the hub. This fact is also used in function get_points_sorted_by_angle_from_positive_x_axis
    hub_position = node_positions[0]
    hub = Hub(hub_position)

    places = []
    for place_position in node_positions[1:]:
        places.append(Place(place_position))

    points_sorted_by_angle_index = get_points_sorted_by_angle_from_positive_x_axis(node_positions)

    set_neighbouring_places_for_nodes(places, points_sorted_by_angle_index)

    sectors = initialise_sectors(places, points_sorted_by_angle_index, number_of_sectors, number_of_nodes)

    # Triggering function switch_over_one_random_place whenever return key is pressed
    # This function will move a random place on either end of a sector into the neighbouring sector
    custom_events_by_key_press[pygame.K_RETURN] = switch_over_one_random_place
    custom_events_by_key_press[pygame.K_l] = draw_lines_seperating_sectors
    custom_events_by_key_press[pygame.K_i] = act_on_first_task_from_possible_place_switches

    possible_place_switches = SortedQueue()
    previous_actions_from_possible_place_switches = []
    possible_place_switches.add_element(None, get_current_sectors_weight())

    generate_possible_place_switches_sorted_on_varance_of_sector_weights(possible_place_switches)

    draw_lines_seperating_sectors()
    if not DEBUG:
        functions_to_run_every_second.append(act_on_first_task_from_possible_place_switches)

def goto_next_test_case():
    time.sleep(1)
    global program_finished
    program_finished = True

def run_mtsp(number_of_nodes, number_of_sectors, node_positions):
    
    global program_finished
    program_finished = False

    initialise(number_of_nodes, number_of_sectors, node_positions)

    custom_events_by_key_press[pygame.K_n] = goto_next_test_case

    while not program_finished:
        window_loop_iteration()

        #print(program_finished)

# endregion

# region mainloop

if __name__ == "__main__":

    if DEBUG:
        node_positions = [[320, 480], [448, 400], [304, 528], [64, 96], [496, 528], [256, 736], [288, 784], [80, 272], [400, 144], [448, 96], [352, 752], [144, 400], [624, 608], [64, 464], [384, 608], [432, 160], [48, 752], [688, 640], [80, 96]]
        number_of_nodes = len(node_positions)
        number_of_sectors = 5

        window_surface = pygame_init()

        run_mtsp(number_of_nodes, number_of_sectors, node_positions)

        quit()

    input_mode =  input(f"How to accept input? (m: manual, a: automatic, j: from {JSON_DATA_FILE}): ")
    if input_mode == "m":
        node_positions = eval(input("Enter node positions as a list of tuple positions: "))
        number_of_nodes = len(node_positions)
        number_of_sectors = int(input("Enter number of lines to draw: "))

        window_surface = pygame_init()

        run_mtsp(number_of_nodes, number_of_sectors, node_positions)

    elif input_mode == "a":
        if DEBUG:
            number_of_nodes = 50
            number_of_sectors = 5
        else:
            number_of_nodes = int(input("Enter number of nodes to generate: "))
            number_of_sectors = int(input("Enter number of lines to draw: "))

        node_positions = generate_node_position(number_of_nodes)

        print("Node positions:", node_positions)

        window_surface = pygame_init()

        run_mtsp(number_of_nodes, number_of_sectors, node_positions)

    elif input_mode == "j":
        with open(JSON_DATA_FILE, "r") as json_file_read:
            data = json.load(json_file_read)

        window_surface = pygame_init()

        for test_case in data:
            node_positions = test_case["node_positions"]
            number_of_nodes = len(node_positions)
            
            node_position_multiplier = test_case["node_position_multiplier"]
            for i in range(number_of_nodes):
                # Scaling the positions to fit the entire window
                node_positions[i][0] *= node_position_multiplier
                node_positions[i][1] *= node_position_multiplier

                # Modifying positions since origin is at top left corner.
                node_positions[i][1] = window_height - node_positions[i][1]

            for number_of_sectors in test_case["sectors"]:
                try:
                    run_mtsp(number_of_nodes, number_of_sectors, node_positions)

                    if "file_name" in test_case:
                        png_file_name = test_case["file_name"] + "_sectors_" + str(number_of_sectors) + ".png"
                        png_file_path = os.path.join(IMAGE_FOLDER_PATH, png_file_name)
                        pygame.image.save(window_surface, png_file_path)

                    sprites_to_blit.empty()

                except BaseException as exp:
                    print(exp)
                    print(f"Unable to find solution with {number_of_sectors} sectors for: \n{node_positions}\n")

    else:
        print("Input mode not identified.")
        quit()

# endregion
