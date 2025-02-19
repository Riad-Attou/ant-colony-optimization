from city import City


class Road:
    def __init__(self, weight: float, start_city: City, end_city: City):
        self.__weight = weight
        self.__pheromone = 0
        self.__start_city = start_city
        self.__end_city = end_city

    def get_id(self):
        return self.__start_city.get_id(), self.__end_city.get_id()

    def get_weight(self):
        return self.__weight

    def get_pheromone(self):
        return self.__pheromone

    def add_pheromone(self, pheromone: float):
        self.__pheromone += pheromone
        return

    def get_cities(self):
        return self.__start_city, self.__end_city

    def evaporate_pheromone(self):
        return

    def reverse(self):
        return Road(self.__weight, self.__end_city, self.__start_city)

    def __str__(self):
        return f"Road ({self.__start_city.get_id()}, {self.__end_city.get_id()}):\n\tWeight: {self.__weight}\n\tPheromone: {self.__pheromone}"
