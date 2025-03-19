import random

from PyQt5.QtGui import QColor


class Ant:
    def __init__(self, id: int, alpha: float, beta: float, start_city):
        self.__id = id
        self.__alpha = alpha
        self.__beta = beta
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
        self.__exploration_weight = 1  # favorise le nombre d’arêtes explorées
        self.__rarity_bonus = 0  # favorise les arêtes rares
        self.__redundancy_penalty = (
            0  # pénalise le fait de repasser sur les mêmes arêtes
        )
        self.__exploration_fitness = 0
        self.__color = None

    def get_id(self):
        return self.__id

    def get_color(self):
        if self.__has_food:
            return self.__color_with_food
        else:
            return self.__color_no_food

    def get_personalised_color(self):
        return self.__color

    def set_color(self, color):
        self.__color_no_food = color
        self.__color = color

    def get_speed(self):
        return self.__speed

    def get_t(self):
        return self.__t

    def set_cumulated_weights(self, cumulated_weights: float):
        self.__cumulated_weights = cumulated_weights
        return

    def get_parameters(self):
        return self.__alpha, self.__beta

    def get_food_quantity(self):
        return self.__food_quantity

    def set_id(self, id):
        self.__id = id

    def set_alpha(self, alpha):
        self.__alpha = alpha

    def set_beta(self, beta):
        self.__beta = beta

    def get_current_city(self):
        return self.__current_city

    def set_current_city(self, city):
        self.__current_city = city
        return

    def get_exploration_fitness(self):
        return len(self.__explored_roads_count)

    # def set_exploration_fitness(self, population):
    #     explored_roads_count = self.__explored_roads_count
    #     self_edges = set(explored_roads_count.keys())  # Arêtes explorées par self
    #     if len(population) <= 1:  # Si la population est vide ou ne contient que self
    #         unique_roads_count = len(
    #             self_edges
    #         )  # Toutes les routes explorées sont uniques
    #         unique_roads = list(self_edges)
    #     else:
    #         unique_roads_count = 0
    #         unique_roads = []
    #         for ant in population:
    #             if ant is self:
    #                 continue  # Ne pas comparer la fourmi avec elle-même

    #             other_edges = set(ant.get_explored_roads_count().keys())
    #             for road in self_edges - other_edges:
    #                 if road not in unique_roads:
    #                     unique_roads.append(road)
    #                     unique_roads_count += 1

    #     # Compter combien de fois chaque arête est empruntée dans la population
    #     fitness = (
    #         self.__exploration_weight * unique_roads_count
    #         + self.__rarity_bonus
    #         * sum(1 / (1 + road.get_usage_count(population)) for road in unique_roads)
    #         - self.__redundancy_penalty
    #         * sum(
    #             road.get_usage_count(population) / len(explored_roads_count)
    #             for road in self_edges
    #         )
    #     )
    #     self.__exploration_fitness = fitness

    # def set_exploration_fitness(self):
    #     explored_roads_count = self.__explored_roads_count
    #     self.__exploration_fitness = len(explored_roads_count) / sum(
    #         explored_roads_count.values()
    #     )

    def reset_ant(self):
        self.__current_city = self.__start_city
        self.__next_city = None
        self.__explored_roads = []
        self.__cumulated_weights = 0
        self.__food_quantity = 0
        self.__explored_roads_count = {}
        self.__has_food = False
        self.__exploration_fitness = 0

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

    def add_explored_roads_count(self, road):
        self.__explored_roads_count[road] = 0

    def pop_explored_roads(self):
        self.__explored_roads.pop()
        return

    def has_food(self):
        return self.__has_food

    def set_has_food(self, has_food):
        self.__has_food = has_food
        return

    def increment_explored_roads(self, key):
        self.__explored_roads_count[key] += 1

    def set_food_quatity(self):
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
        parameter_to_mutate = random.choice(["alpha", "beta"])
        if parameter_to_mutate == "alpha":
            alpha_mutated = random.uniform(0, 5)
            self.set_alpha(alpha_mutated)
        elif parameter_to_mutate == "beta":
            beta_mutated = random.uniform(0, 5)
            self.set_beta(beta_mutated)

    def __str__(self):
        return f"Ant {self.__id}:\n\tParameters (alpha, beta): {self.get_parameters()}\n\tHas food: {self.has_food()}\n"
