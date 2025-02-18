from city import City
from road import Road


class Civilization:
    def __init__(self, nest: City, food_source: City):
        self.__cities = [nest, food_source]
        self.__roads = []
        self.__nest = nest
        self.__food_source = food_source

    def get_cities(self):
        return self.__cities

    def get_city_by_id(self, id: int):
        for city in self.__cities:
            if city.get_id() == id:
                return city
        return None

    def get_roads(self):
        return self.__roads

    def get_nest(self):
        return self.__nest

    def get_food_source(self):
        return self.__food_source

    def add_city(self, city: City):
        self.__cities.append(city)
        return

    def add_road(self, weight: float, start_city: City, end_city: City):
        road = Road(weight, start_city, end_city)
        self.__roads.append(road)
        start_city = self.get_city_by_id(road.get_cities()[0].get_id())
        start_city.add_road(road)
        return

    def set_nest(self, nest: City):
        self.__nest = nest
        return

    def set_food_source(self, food_source: City):
        self.__food_source = food_source
        return

    def __str__(self):
        return f"Civilization:\n\tNest: City {self.__nest.get_id()} \n\n\tFood source: City {self.__food_source.get_id()}\
        \n\n\tCities: {[city.get_id() for city in self.__cities]}\n\n\tRoad: {[road.get_id() for road in self.__roads]}"
