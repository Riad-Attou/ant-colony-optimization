class Ant:
    def __init__(self, id: int, alpha: float, beta: float, gamma: float):
        self.__id = id
        self.__alpha = alpha
        self.__beta = beta
        self.__gamma = gamma
        self.__has_food = False

    def get_id(self):
        return self.__id

    def get_parameters(self):
        return self.__alpha, self.__beta, self.__gamma

    def has_food(self):
        return self.__has_food

    def take_food(self):
        pass

    def leave_food(self):
        pass

    def deposit_pheromone(self):
        pass

    def step(self):
        pass

    def __str__(self):
        return f"Ant {self.__id}:\n\tParameters (alpha, beta, gamma): {self.get_parameters()}\n\tHas food: {self.has_food()}\n"
