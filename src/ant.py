import random

from PyQt5.QtGui import QColor


class Ant:
    def __init__(self, id: int, alpha: float, beta: float, gamma: float, start_city):
        self.__id = id
        self.__alpha = alpha
        self.__beta = beta
        self.__gamma = gamma
        self.__has_food = False
        self.__current_city = start_city
        self.__next_city = None  # Updated by Civilization.step()
        self.__speed = 1.0
        self.__color = QColor(100, 100, random.randint(150, 255))
        self.__explored_roads = []
        self.__cumulated_weights = 0

    def get_id(self):
        return self.__id

    def get_color(self):
        return self.__color

    def get_speed(self):
        return self.__speed

    def get_t(self):
        return self.__t

    def set_cumulated_weights(self, cumulated_weights: float):
        self.__cumulated_weights = cumulated_weights
        return

    def get_parameters(self):
        return self.__alpha, self.__beta, self.__gamma

    def get_current_city(self):
        return self.__current_city

    def set_current_city(self, city):
        self.__current_city = city
        return

    def get_next_city(self):
        return self.__next_city

    def set_next_city(self, city):
        self.__next_city = city
        return

    def add_explored_road(self, road):
        self.__explored_roads.append(road)
        return

    def get_explored_roads(self):
        return self.__explored_roads

    def pop_explored_roads(self):
        self.__explored_roads.pop()
        return

    def has_food(self):
        return self.__has_food

    def set_has_food(self, has_food):
        self.__has_food = has_food
        return

    def take_food(self):
        pass

    def leave_food(self):
        pass

    def compute_pheromone(self):
        pheromone = self.__cumulated_weights
        return 1 / (pheromone * pheromone)

    def deposit_pheromone(self, road):
        road.add_pheromone(self.compute_pheromone())
        return

    def __str__(self):
        return f"Ant {self.__id}:\n\tParameters (alpha, beta, gamma): {self.get_parameters()}\n\tHas food: {self.has_food()}\n"
