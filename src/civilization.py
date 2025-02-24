import random

import numpy as np
from sklearn.manifold import MDS

from ant import Ant
from city import City
from road import Road


class Civilization:
    def __init__(self, nest: City, food_source: City, evaporation_rate: float):
        self.__cities = [nest, food_source]
        self.__roads = []
        self.__nest = nest
        self.__food_source = food_source
        self.__ants = []
        self.__half_pheromone_time = int(np.log(1 / 2) / np.log(1 - evaporation_rate))
        self.__evaporation_rate = evaporation_rate
        self.steps = 0

        self.__scale_factor = 120  # 1 unité de poids correspond à 120 pixels

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

    def get_ants(self):
        return self.__ants

    def get_half_pheromone_time(self):
        return self.__half_pheromone_time

    def add_city(self, city: City):
        self.__cities.append(city)
        return

    def add_road(self, weight: float, start_city: City, end_city: City):
        road = Road(weight, start_city, end_city)
        self.__roads.append(road)
        start_city = self.get_city_by_id(road.get_cities()[0].get_id())
        start_city.add_road(road)
        return

    def add_ants(self, ant: Ant):
        self.__ants.append(ant)
        return

    def set_nest(self, nest: City):
        self.__nest = nest
        return

    def set_food_source(self, food_source: City):
        self.__food_source = food_source
        return

    def halve_pheromone(self):
        for road in self.__roads:
            current_pheromone = road.get_pheromone()
            road.set_pheromone(current_pheromone / 2)

    def create_ant_colony(self, ant_number: int):
        assert ant_number > 0
        for i in range(ant_number):
            ant = Ant(i, 0.5, 0.5, 0.5, self.__nest)
            self.add_ants(ant)
        return

    def get_distance_matrix(self):
        n = len(self.__cities)
        # On utilise une valeur par défaut élevée pour les villes non connectées directement.
        D = np.full((n, n), 500.0)
        np.fill_diagonal(D, 0)
        # Pour chaque route, on met à jour la matrice.
        for road in self.__roads:
            start, end = road.get_cities()
            # On suppose que chaque ville est unique dans la liste
            i = self.__cities.index(start)
            j = self.__cities.index(end)
            distance = road.get_weight() * self.__scale_factor
            D[i, j] = distance
            D[j, i] = distance  # Supposons que les routes sont bidirectionnelles
        return D

    def compute_layout(self):
        D = self.get_distance_matrix()
        mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
        positions = mds.fit_transform(D)
        return positions

    def get_reversed_roads(self, city):
        return [
            Road(road.get_weight(), road.get_cities()[1], road.get_cities()[0])
            for road in self.__roads
            if road.get_cities()[1].get_id() == city.get_id()
        ]

    def find_reversed_road(self, reversed_road):
        for road in self.__roads:
            if road.get_id() == reversed_road.get_id()[::-1]:
                return road

    def weighted_choice(self, roads):
        # Récupère les phéromones pour chaque route
        weights = [road.get_pheromone() for road in roads]
        # Si la somme des poids est nulle, retourne une route aléatoire uniformément
        if sum(weights) == 0:
            return random.choice(roads)
        # random.choices retourne une liste, on prend le premier élément
        return random.choices(roads, weights=weights, k=1)[0]

    def step(self):
        self.steps += 1
        if self.steps == self.__half_pheromone_time:
            self.halve_pheromone()

        for road in self.__roads:
            road.evaporate_pheromone()

        for ant in self.__ants:
            if not ant.has_food():
                if ant.get_current_city().get_id() == self.get_food_source().get_id():
                    ant.set_has_food(True)
                    ant.set_cumulated_weights(
                        sum(
                            [
                                ant.get_explored_roads()[i].get_weight()
                                for i in range(len(ant.get_explored_roads()))
                            ]
                        )
                    )

                if ant.get_next_city() is None:
                    outgoing_roads = ant.get_current_city().get_roads()
                    if not outgoing_roads:
                        continue
                    next_road = self.weighted_choice(outgoing_roads)
                    ant.add_explored_road(next_road)
                    next_city = next_road.get_cities()[1]
                    ant.set_next_city(next_city)
                    continue

                else:
                    ant.set_current_city(ant.get_next_city())

                outgoing_roads = ant.get_current_city().get_roads()
                if not outgoing_roads:
                    continue
                next_road = self.weighted_choice(outgoing_roads)
                ant.add_explored_road(next_road)
                next_city = next_road.get_cities()[1]
                ant.set_next_city(next_city)

            else:
                if ant.get_current_city().get_id() == self.get_nest().get_id():
                    ant.set_has_food(False)
                    ant.set_cumulated_weights(0)

                ant.set_current_city(ant.get_next_city())
                reversed_roads = [
                    ant.get_explored_roads()[i].reverse()
                    for i in range(len(ant.get_explored_roads()))
                ]
                if not reversed_roads:
                    continue
                next_road = reversed_roads[-1]
                reversed_roads.pop()
                ant.pop_explored_roads()
                next_city = next_road.get_cities()[1]
                ant.set_next_city(next_city)

                ant.deposit_pheromone(self.find_reversed_road(next_road))

        return

    def get_best_path(self):
        """
        Retourne une liste des City qui représente le meilleur chemin
        actuel de la source (nid) vers la food_source, en suivant la route
        ayant la plus forte quantité de phéromone à chaque étape.
        """
        path = []
        current_city = self.__nest
        path.append(current_city)
        visited = {current_city}

        # Tant qu'on n'est pas arrivé à la food source
        while current_city != self.__food_source:
            outgoing_roads = current_city.get_roads()
            best_road = None
            best_pheromone = -1  # On part d'une valeur très basse

            # Parcourir les routes sortantes
            for road in outgoing_roads:
                # On suppose que road.get_cities() renvoie un tuple (start, end)
                _, dest = road.get_cities()
                # Évite de repasser par une ville déjà visitée pour limiter les cycles
                if dest in visited:
                    continue
                if road.get_pheromone() > best_pheromone:
                    best_pheromone = road.get_pheromone()
                    best_road = road

            if best_road is None:
                # Aucun chemin (sans cycle) n'a été trouvé ; on arrête la recherche.
                break

            # On choisit la destination de la route avec le maximum de phéromones.
            _, next_city = best_road.get_cities()
            path.append(next_city)
            visited.add(next_city)
            current_city = next_city

        return path

    def __str__(self):
        return f"Civilization:\n\tNest: City {self.__nest.get_id()} \n\n\tFood source: City {self.__food_source.get_id()}\
        \n\n\tCities: {[city.get_id() for city in self.__cities]}\n\n\tRoad: {[road.get_id() for road in self.__roads]}\
        \n\n\tAnts: {[([ant.get_explored_roads()[i].get_id() for i in range(len(ant.get_explored_roads()))], ant.has_food()) for ant in self.__ants]}"
