import random

from PyQt5.QtGui import QColor


class Ant:
    def __init__(self, id: int, alpha: float, beta: float, gamma: float, start_city):
        self.__id = id
        self.__alpha = alpha
        self.__beta = beta
        self.__gamma = gamma
        self.__has_food = False
        self.__start_city = start_city
        self.__current_city = start_city
        self.__next_city = None  # Updated by Civilization.step()
        self.__speed = 1.0
        self.__color_no_food = QColor(100, random.randint(240, 255), 100)
        self.__color_with_food = QColor(
            random.randint(150, 230), random.randint(90, 120), 10
        )
        self.__explored_roads = []
        self.__cumulated_weights = 0
        self.__food_quantity = 0
        self.__explored_roads_count = {}
        self.__q0 = 0.5
        self.__visited_cities = []

    def get_id(self):
        return self.__id

    def get_color(self):
        if self.__has_food:
            return self.__color_with_food
        else:
            return self.__color_no_food

    def get_speed(self):
        return self.__speed

    def get_t(self):
        return self.__t

    def set_cumulated_weights(self, cumulated_weights: float):
        self.__cumulated_weights = cumulated_weights
        return

    def get_parameters(self):
        return self.__alpha, self.__beta, self.__gamma

    def get_food_quantity(self):
        return self.__food_quantity

    def set_id(self, id):
        self.__id = id

    def set_alpha(self, alpha):
        self.__alpha = alpha

    def set_beta(self, beta):
        self.__beta = beta

    def set_gamma(self, gamma):
        self.__gamma = gamma

    def get_current_city(self):
        return self.__current_city

    def set_current_city(self, city):
        self.__current_city = city
        return

    def get_visited_cities(self):
        return self.__visited_cities

    def add_visited_cities(self, city):
        self.__visited_cities.append(city)

    def reset_visited_cities(self):
        self.__visited_cities = []

    def reset_ant(self):
        self.__current_city = self.__start_city
        self.__next_city = None
        self.__explored_roads = []
        self.__cumulated_weights = 0
        self.__food_quantity = 0
        self.__explored_roads_count = {}
        self.__has_food = False

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

    def get_explored_roads_count(self):
        return self.__explored_roads_count

    def get_total_exploration_count(self):
        return len(self.__explored_roads_count)

    def add_explored_roads_count(self, road):
        self.__explored_roads_count[road] = 0

    def pop_explored_roads(self):
        self.__explored_roads.pop()
        return

    def reset_explored_roads(self):
        self.__explored_roads = []

    def has_food(self):
        return self.__has_food

    def set_has_food(self, has_food):
        self.__has_food = has_food
        return

    def increment_explored_roads(self, road):
        self.__explored_roads_count[road] += 1

    def set_food_quantity(self):
        self.__food_quantity += 1

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

    def weighted_choice(self, roads):
        # Récupère les poids en utilisant alpha et beta
        weights = [
            (road.get_pheromone() ** self.__alpha)
            * ((1 / road.get_weight()) ** self.__beta)
            for road in roads
        ]
        total_weights = sum(weights)
        probabilities = [w / total_weights for w in weights]
        q = random.uniform(0, 1)
        if sum(weights) == 0:
            return random.choice(roads)
        if q <= self.__q0:
            # Exploitation : sélection de la route avec le poids maximal
            best_road_index = weights.index(max(weights))
            return roads[best_road_index]
        else:
            # Exploration : sélection d'une route selon les probabilités P_k(r,s)
            return random.choices(roads, weights=probabilities, k=1)[0]

    def mutation(self):
        parameter_to_mutate = random.choice(["alpha", "beta", "gamma"])
        if parameter_to_mutate == "alpha":
            alpha_mutated = random.uniform(0, 5)
            self.set_alpha(alpha_mutated)
        elif parameter_to_mutate == "beta":
            beta_mutated = random.uniform(0, 5)
            self.set_beta(beta_mutated)
        else:
            gamma_mutated = random.uniform(0, 5)
            self.set_gamma(gamma_mutated)

    def __str__(self):
        return f"Ant {self.__id}:\n\tParameters (alpha, beta, gamma): {self.get_parameters()}\n\tHas food: {self.has_food()}\n"
