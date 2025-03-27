import random

import numpy as np
from sklearn.manifold import MDS

from tsp.ant import Ant
from tsp.city import City
from tsp.road import Road


class Civilization:
    def __init__(
        self,
        nest: City,
        evaporation_rate: float,
        initial_pheromone: float,
        mutation_factor: float,
        steps_genetic_algo: int,
    ):
        self.__cities = [nest]
        self.__roads = []
        self.__nest = nest
        self.__ants = []
        self.__half_pheromone_time = int(np.log(1 / 2) / np.log(1 - evaporation_rate))
        self.__evaporation_rate = evaporation_rate
        self.steps = 0
        self.__initial_pheromone = initial_pheromone
        self.__scale_factor = 120  # 1 unité de poids correspond à 120 pixels
        self.__mutation_factor = mutation_factor
        self.__threshold_genetic_algo = 300
        self.__steps_genetic_algo = steps_genetic_algo

    def get_cities(self):
        return self.__cities

    def get_city_by_id(self, id: int):
        for city in self.__cities:
            if city.get_id() == id:
                return city
        return None

    def get_road_by_cities(self, start_city, end_city):
        for road in self.__roads:
            if road.get_id() == (start_city.get_id(), end_city.get_id()):
                return road
        return None

    def get_roads(self):
        return self.__roads

    def get_nest(self):
        return self.__nest

    def get_ants(self):
        return self.__ants

    def get_half_pheromone_time(self):
        return self.__half_pheromone_time

    def get_initial_pheromone(self):
        return self.__initial_pheromone

    def get_mutation_factor(self):
        return self.__mutation_factor

    def add_city(self, city: City):
        self.__cities.append(city)
        return

    def set_ants(self, ants):
        self.__ants = ants

    def add_road(
        self,
        weight: float,
        start_city: City,
        end_city: City,
    ):
        if start_city.get_id() < end_city.get_id():
            road = Road(weight, start_city, end_city, self.__initial_pheromone)
        else:
            road = Road(weight, end_city, start_city, self.__initial_pheromone)
        self.__roads.append(road)
        start_city.add_road(road)
        end_city.add_road(road)
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

    def set_initial_pheromone(self, new_initial_pheronome: float):
        self.__initial_pheromone = new_initial_pheronome

    def halve_pheromone(self):
        for road in self.__roads:
            current_pheromone = road.get_pheromone()
            road.set_pheromone(current_pheromone / 2)

    def create_ant_colony(self, ant_number: int, alpha: float, beta: float):
        assert ant_number > 0
        for i in range(ant_number):
            ant = Ant(len(self.get_ants()), alpha, beta, self.__nest)
            self.add_ants(ant)
        return

    def reset_ants(self):
        # Vider la liste des fourmis
        self.__ants = []
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

    def compute_free_layout(self):
        # Retourne un tableau numpy des positions définies pour chaque ville
        return np.array(
            [
                [city.get_position().x(), city.get_position().y()]
                for city in self.get_cities()
            ]
        )

    def compute_layout(self):
        D = self.get_distance_matrix()
        mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
        positions = mds.fit_transform(D)
        return positions

    def migration(self):
        alpha = random.uniform(0, 5)
        beta = random.uniform(0, 5)
        self.create_ant_colony(1, alpha, beta)

    def crossover(self, ant_mum, ant_dad):
        parameters = [random.choice([0, 1]) for _ in range(3)]
        # Héritage des paramètres
        alpha = (
            ant_mum.get_parameters()[0]
            if parameters[0] == 0
            else ant_dad.get_parameters()[0]
        )
        beta = (
            ant_mum.get_parameters()[1]
            if parameters[1] == 0
            else ant_dad.get_parameters()[1]
        )
        self.create_ant_colony(1, alpha, beta)

    def selection(self):
        ants_data = [
            (ant, ant.get_food_quantity(), ant.get_exploration_fitness())
            for ant in self.__ants
        ]
        # Trier selon la nourriture récoltée (meilleurs travailleurs)
        best_workers = sorted(ants_data, key=lambda x: x[1], reverse=True)
        best_two_workers = (best_workers[0][0], best_workers[1][0])
        worst_worker = best_workers[-1][0]
        # Trier selon le nombre de routes explorées (meilleurs explorateurs)
        best_explorers = sorted(ants_data, key=lambda x: x[2], reverse=True)
        best_two_explorers = (best_explorers[0][0], best_explorers[1][0])
        worst_explorer = best_explorers[-1][0]
        self.__ants.remove(worst_worker)
        if worst_explorer in self.__ants:
            self.__ants.remove(worst_explorer)
        for new_id, ant in enumerate(self.__ants):
            ant.set_id(new_id)
        return best_two_workers, best_two_explorers

    def genetic_algo(self):
        best_two_workers, best_two_explorers = self.selection()
        self.crossover(best_two_workers[0], best_two_workers[1])
        self.crossover(best_two_explorers[0], best_two_explorers[1])
        ants_to_mutate = np.random.choice(
            self.__ants, int((len(self.__ants) * self.get_mutation_factor()))
        )
        for ant in ants_to_mutate:
            ant.mutation()
        self.migration()

    def step(self):
        self.steps += 1
        if self.steps == self.__half_pheromone_time:
            self.halve_pheromone()

        # Évaporation des phéromones
        for road in self.__roads:
            road.evaporate_pheromone()
        for ant in self.__ants:
            # Si la fourmi a finit son cycle
            if (
                ant.get_current_city().get_id() == self.get_nest().get_id()
                and self.steps > 1
            ):
                ant.set_food_quantity()
                if ant.get_explored_roads():
                    new_road = tuple(
                        [road.get_id() for road in ant.get_explored_roads()]
                    )

                    def compare_keys(tuple1, tuple2):
                        for i in range(len(tuple1)):
                            if (
                                tuple1[i][0] != tuple2[i][0]
                                or tuple1[i][1] != tuple2[i][1]
                            ):
                                return False
                        return True

                    if any(
                        compare_keys(new_road, key)
                        for key in ant.get_explored_roads_count().keys()
                    ):
                        ant.increment_explored_roads(new_road)
                    else:
                        ant.add_explored_roads_count(new_road)
                        ant.increment_explored_roads(new_road)
                ant.set_cumulated_weights(0)
                ant.reset_explored_roads()

            # Si la fourmi a une destination, elle s'y déplace
            if ant.get_next_city() is not None:
                ant.set_current_city(ant.get_next_city())
                # Si toutes les villes ont été visitées, on force le retour au nid
                if len(ant.get_visited_cities()) == len(self.__cities) - 1:
                    next_city = self.get_nest()
                    next_road = self.get_road_by_cities(
                        self.get_nest(), ant.get_current_city()
                    )
                    ant.set_next_city(next_city)
                    ant.add_explored_road(next_road)
                    ant.set_cumulated_weights(
                        sum([road.get_weight() for road in ant.get_explored_roads()])
                    )
                    for road in ant.get_explored_roads():
                        ant.deposit_pheromone(road)
                    ant.reset_visited_cities()
                else:
                    ant.set_next_city(None)  # Réinitialiser pour le prochain choix

            else:
                unvisited_cities = [
                    city
                    for city in self.__cities
                    if city not in ant.get_visited_cities() and city != self.get_nest()
                ]
                outgoing_roads = []
                for road in ant.get_current_city().get_roads():
                    if road.get_cities()[0] != ant.get_current_city():
                        if road.get_cities()[0] in unvisited_cities:
                            outgoing_roads.append(road)

                    elif road.get_cities()[1] != ant.get_current_city():
                        if road.get_cities()[1] in unvisited_cities:
                            outgoing_roads.append(road)

                next_road = ant.weighted_choice(outgoing_roads)
                ant.add_explored_road(next_road)
                if next_road.get_cities()[1] != ant.get_current_city():
                    next_city = next_road.get_cities()[1]
                else:
                    next_city = next_road.get_cities()[0]
                ant.set_next_city(next_city)
                ant.add_visited_cities(next_city)

    def get_best_path(self):
        """
        Retourne une liste d'objets City représentant le circuit basé sur
        les niveaux actuels de phéromones. Le circuit démarre d'une ville
        de départ, visite chaque ville une seule fois, puis retourne à cette ville.
        """
        path = []
        # Choisissez la ville de départ (par exemple, self.__start_city)
        current_city = self.__nest
        path.append(current_city)
        visited = {current_city}

        # Tant que toutes les villes n'ont pas été visitées
        while len(visited) < len(self.__cities):
            outgoing_roads = current_city.get_roads()
            best_road = None
            best_pheromone = -1

            # Sélectionner la route menant à une ville non visitée ayant la plus forte phéromone
            for road in outgoing_roads:
                start, dest = road.get_cities()
                next_city = dest if start == current_city else start
                if next_city in visited:
                    continue
                if road.get_pheromone() > best_pheromone:
                    best_road = road
                    best_pheromone = road.get_pheromone()

            # Sécurité (inutile dans un graphe complet a priori)
            if best_road is None:
                break

            # Récupérer la ville suivante depuis la route sélectionnée
            start, dest = best_road.get_cities()
            next_city = dest if start == current_city else start

            path.append(next_city)
            visited.add(next_city)
            current_city = next_city

        # Fermer le circuit en revenant à la ville de départ
        path.append(path[0])
        return path

    def genetic_algo_application(self):
        for i in range(self.__steps_genetic_algo):
            self.step()
        threshold_genetic_algo = self.__threshold_genetic_algo
        while threshold_genetic_algo > 0:
            self.genetic_algo()
            for ant in self.__ants:
                ant.reset_ant()
            for i in range(self.__steps_genetic_algo):
                self.step()
            threshold_genetic_algo -= 1

    def best_worker(self):
        ants_data = [
            (ant, ant.get_food_quantity(), ant.get_exploration_fitness())
            for ant in self.__ants
        ]
        # Trier selon la nourriture récoltée (meilleurs travailleurs)
        best_workers = sorted(ants_data, key=lambda x: x[1], reverse=True)
        return best_workers[0]

    def best_explorer(self):
        ants_data = [
            (ant, ant.get_food_quantity(), ant.get_exploration_fitness())
            for ant in self.__ants
        ]
        best_explorers = sorted(ants_data, key=lambda x: x[2], reverse=True)
        return best_explorers[0]

    def __str__(self):
        return f"Civilization:\n\tNest: City {self.__nest.get_id()}\
        \n\n\tCities: {[city.get_id() for city in self.__cities]}\n\n\tRoad: {[road.get_id() for road in self.__roads]}\
        \n\n\tAnts: {[([ant.get_explored_roads()[i].get_id() for i in range(len(ant.get_explored_roads()))], ant.has_food()) for ant in self.__ants]}"
