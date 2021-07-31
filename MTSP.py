import numpy, math

from typing import Iterable
from python_tsp.exact import solve_tsp_dynamic_programming


DEBUG = False


class Village:

    def __init__(self, position, warehouse_position):

        self.position = position
        self.warehouse_position = warehouse_position

        self.weight = numpy.linalg.norm(self.position - self.warehouse_position)

    def get_angle_to_warehouse(self):
        x, y = self.position - self.warehouse_position
        return math.atan2(y, x)

    def set_adjacent_villages(self, village_to_clockwise, village_to_anticlockwise):

        self.village_to_clockwise = village_to_clockwise
        self.village_to_anticlockwise = village_to_anticlockwise

    def get_weight(self):
        return self.weight


class Sector:

    def __init__(self, villages):
        """
        villages is an interable(list/tuple) containing Village() objects

        villages[0] is the Village() with the smallest angle.
        (i.e. most clockwise village)
        """
        self.villages = villages

        self.weight = sum(village.get_weight() for village in self.villages)

    def get_weight(self):
        return self.weight

    def get_weight_on_add_village(self, village):
        if village in self.villages:
            exception_message = f"""Unable to add village to sector as it's already in the sector.
            Villages in sector: {[village.position for village in self.villages]}
            Village trying to be added: {village.position}
            """
            raise Exception(exception_message)

        if DEBUG:
            debug_message = f"""Temporarily adding village to sector.
            Villages in sector: {[village.position for village in self.villages]}
            Village being added: {village.position}
            """
            print(debug_message)

        return self.weight + village.weight

    def get_weight_on_remove_village(self, village):
        if village not in self.villages:
            exception_message = f"""Unable to remove village from sector as it's not in the sector.
            Villages in sector: {[village.position for village in self.villages]}
            Village trying to be removed: {village.position}
            """
            raise Exception(exception_message)

        if DEBUG:
            debug_message = f"""Temporarily removing village from sector.
            Villages in sector: {[village.position for village in self.villages]}
            Village being removed: {village.position}
            """
            print(debug_message)

        return self.weight - village.weight

    def add_village(self, village):
        new_sector_weight = self.get_weight_on_add_village(village)

        # Check if the village is adjacent to the sector(angle wise)
        if village is self.villages[0].village_to_clockwise:
            self.villages.insert(0, village)

        elif village is self.villages[-1].village_to_anticlockwise:
            self.villages.append(village)

        else:
            exception_message = f"""Unable to add village as its not adjacent to the sector.
            Villages in sector: {[village.position for village in self.villages]}
            Village trying to be added: {village.position}
            """
            raise Exception(exception_message)

        self.weight = new_sector_weight

    def remove_village(self, village):
        new_sector_weight = self.get_weight_on_remove_village(village)

        # Check if the village is at one of the extremes of the sector(angle wise)
        if village is self.villages[0]:
            self.villages.pop(0)

        elif village is self.villages[-1]:
            self.villages.pop(-1)

        else:
            exception_message = f"""Unable to remove village as its not at one of the extremes of the sector.
            Villages in sector: {[village.position for village in self.villages]}
            Village trying to be removed: {village.position}
            """
            raise Exception(exception_message)

        self.weight = new_sector_weight


class TSP:

    def __init__(self, points):
        self.points = points

    def get_square_of_distance_between_points(self, p1, p2):
        return (p1[0]-p2[0]) ** 2 + (p1[1]-p2[1]) ** 2

    def get_distance_matrix_from_points(self, points):
        distance_matrix = numpy.asarray([[self.get_square_of_distance_between_points(p1, p2) for p2 in points] for p1 in points])
        return distance_matrix
        
    def solve(self):
        distance_matrix = self.get_distance_matrix_from_points(self.points)  # Note that each distance here is squared everywhere
        distance_matrix[:, 0] = 0

        permutation = solve_tsp_dynamic_programming(distance_matrix)[0]

        solution = [self.points[point_index] for point_index in permutation]

        return solution


class MTSP:

    def __init__(self, village_positions: Iterable, warehouse_position, number_of_sectors):
        """
        village_positions is an iterable(list/tuple) of positions of all the villages.
        """

        self.warehouse_position = warehouse_position

        self.village_positions = village_positions
        self.number_of_villages = len(self.village_positions)
        self.get_fixed_village_positions()

        self.villages = list(map(lambda position: Village(position, warehouse_position), self.fixed_village_positions))
        self.sort_villages_by_angle()

        self.set_adjacent_villages_for_each_village()

        self.number_of_sectors = number_of_sectors
        self.initialise_sectors()

    def get_fixed_village_positions(self):
        self.fixed_village_positions = []
        # Convert the positions from a normal iterable to a numpy array.

        for index in range(self.number_of_villages):
            self.fixed_village_positions.append(numpy.array(self.village_positions[index]))

        # Find the bounding rectangle for the village_positions
        self.bottom_left_point = numpy.amin(self.village_positions, axis = 0)
        self.top_right_point = numpy.amax(self.village_positions, axis = 0)

        # Subtract bottom_left_point from all village_positions
        self.fixed_village_positions -= self.bottom_left_point

        return self.fixed_village_positions

    def sort_villages_by_angle(self):
        """
        self.villages[0] will be the Village() with the smallest angle.
        (i.e. most clockwise village)
        """
        self.villages.sort(key = lambda village: village.get_angle_to_warehouse())

    def set_adjacent_villages_for_each_village(self):
        for index in range(self.number_of_villages - 1):
            village_to_clockwise = self.villages[index - 1]
            village_to_anticlockwise = self.villages[index + 1]
            self.villages[index].set_adjacent_villages(village_to_clockwise, village_to_anticlockwise)

        self.villages[0].set_adjacent_villages(self.villages[-1], self.villages[1])
        self.villages[-1].set_adjacent_villages(self.villages[-2], self.villages[0])

    def initialise_sectors(self):
        self.sectors = []

        self.villages_per_sector = self.number_of_villages // self.number_of_sectors

        current_village_index = 0
        while current_village_index < self.number_of_villages:
            current_village_index_limit = current_village_index + self.villages_per_sector

            if current_village_index_limit > self.number_of_villages:
                current_village_index_limit = self.number_of_villages

            villages_in_sector = self.villages[current_village_index:current_village_index_limit]

            current_village_index = current_village_index_limit

            self.sectors.append(Sector(villages_in_sector))

    def get_variance_in_sector_weights(self, sector_weights):
        return numpy.var(sector_weights)

    def compare_village_switches(self):
        """
        Finds which village must be moved from one sector to another to reduce the variance in sector weights the most.
        """
        sector_weights = [sector.get_weight() for sector in self.sectors]

        self.minimum_sector_weights_variance = self.get_variance_in_sector_weights(sector_weights)
        self.village_shifted_for_minimum_variance = None
        self.sector_village_shifted_from_for_minimum_variance = None
        self.sector_village_shifted_to_for_minimum_variance = None

        # NOTE: CHECK IF BELOW CODE WORKS!!!

        for sector_index in range(self.number_of_sectors):
            village_shifted: Village = self.sectors[sector_index - 1].villages[-1]
            sector_village_shifted_from: Sector = self.sectors[sector_index - 1]
            sector_village_shifted_to: Sector = self.sectors[sector_index]
            old_sector_weights = sector_weights[sector_index - 1], sector_weights[sector_index]
            sector_weights[sector_index - 1] = sector_village_shifted_from.get_weight_on_remove_village(village_shifted)
            sector_weights[sector_index] = sector_village_shifted_to.get_weight_on_add_village(village_shifted)

            sector_weights_variance = self.get_variance_in_sector_weights(sector_weights)
            if sector_weights_variance < self.minimum_sector_weights_variance:
                self.minimum_sector_weights_variance = sector_weights_variance
                self.village_shifted_for_minimum_variance = village_shifted
                self.sector_village_shifted_from_for_minimum_variance = sector_village_shifted_from
                self.sector_village_shifted_to_for_minimum_variance = sector_village_shifted_to

                sector_weights[-1], sector_weights[0] = old_sector_weights

    def shift_village_giving_smallest_sector_weight_variance(self):
        """
        Returns True if village_is_shifted.
        
        Returns False if no village can be shifted for lower sector weigth variance.
        """
        self.compare_village_switches()
        if self.village_shifted_for_minimum_variance:
            self.sector_village_shifted_from_for_minimum_variance.remove_village(self.village_shifted_for_minimum_variance)
            self.sector_village_shifted_to_for_minimum_variance.add_village(self.village_shifted_for_minimum_variance)
            return True

        else:
            return False

    def do_tsp_for_each_sector(self):

        solution = []

        for sector in self.sectors:
            sector_village_positions = [village.position for village in sector.villages]

            print(sector_village_positions)

            sector_village_positions.insert(0, self.warehouse_position)

            solution.append(TSP(sector_village_positions).solve())

        return solution

    def solve_quickly(self):
        while self.shift_village_giving_smallest_sector_weight_variance():
            pass

        return self.do_tsp_for_each_sector()

    def solve_showing_each_step(self, display_function):
        display_function(self.sectors)

        while self.shift_village_giving_smallest_sector_weight_variance():
            display_function(self.sectors)

        return self.do_tsp_for_each_sector()
