from pcc.ant import Ant
from pcc.city import City


class Road:
    def __init__(
        self, weight: float, start_city: City, end_city: City, initial_pheromone: float
    ):
        self.__weight = weight
        self.__pheromone = initial_pheromone
        self.__start_city = start_city
        self.__end_city = end_city

    def get_id(self):
        return self.__start_city.get_id(), self.__end_city.get_id()

    def get_weight(self):
        return self.__weight

    def get_pheromone(self):
        return self.__pheromone

    def get_initial_pheromone(self):
        return self.__initial_pheromone

    def add_pheromone(self, pheromone: float):
        self.__pheromone += pheromone
        return

    def get_cities(self):
        return self.__start_city, self.__end_city

    def set_pheromone(self, pheromone: float):
        self.__pheromone = pheromone

    def reset_pheromone(self, initial_value):
        self.__pheromone = initial_value

    def evaporate_pheromone(self):
        """rho à paramétrer"""
        rho = 0.05
        self.__pheromone *= 1 - rho
        return

    def get_usage_count(self, population):
        """Calcule le nombre total de passages sur cette route par toutes les fourmis."""
        usage_count = 0
        for ant in population:
            explored_roads_count = ant.get_explored_roads_count()
            if (
                self in explored_roads_count.keys()
            ):  # Vérifie si la route a été explorée par la fourmi
                usage_count += explored_roads_count[
                    self
                ]  # Ajoute le nombre de passages
        return usage_count

    def reverse(self):
        return Road(self.__weight, self.__end_city, self.__start_city, self.__pheromone)

    def __str__(self):
        return f"Road ({self.__start_city.get_id()}, {self.__end_city.get_id()}):\n\tWeight: {self.__weight}\n\tPheromone: {self.__pheromone}"
