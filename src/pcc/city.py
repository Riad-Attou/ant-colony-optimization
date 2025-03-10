class City:
    def __init__(self, id: int, position=None):
        self.__id = id
        self.__outgoing_roads = []
        self.__position = position

    def get_id(self):
        return self.__id

    def get_position(self):
        return self.__position

    def set_position(self, position):
        self.__position = position
        return

    def get_roads(self):
        return self.__outgoing_roads

    def add_road(self, road):
        self.__outgoing_roads.append(road)
        return

    def get_neighbors(self):
        return [road.get_cities()[1] for road in self.__outgoing_roads]

    def __str__(self):
        return f"City {self.__id}\n\tOutgoing roads: {[self.get_roads()[i].get_id() for i in range(len(self.get_roads()))]}"
