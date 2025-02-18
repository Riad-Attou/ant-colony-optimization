import random

from PyQt5.QtGui import QColor


# Classe représentant une fourmi animée dans le graphe
class Ant:
    def __init__(self, graph, node_index):
        self.graph = graph
        self.node_index = node_index
        self.current_edge = None  # tuple (u, v)
        self.t = 0.0  # paramètre d'interpolation sur l'arête
        self.speed = random.uniform(0.5, 1.5)  # fraction du chemin par seconde
        # Couleur aléatoire pour cette ant
        self.color = QColor(
            random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)
        )
        self.choose_random_edge(initial=True)

    def choose_random_edge(self, initial=False):
        if initial:
            # Choisir une arête au hasard
            edge = random.choice(list(self.graph.edges()))
            # Choix aléatoire de la direction
            if random.random() < 0.5:
                self.current_edge = edge
            else:
                self.current_edge = (edge[1], edge[0])
        else:
            u, v = self.current_edge
            neighbors = list(self.graph.neighbors(v))
            if u in neighbors and len(neighbors) > 1:
                neighbors.remove(u)
            new_v = random.choice(neighbors)
            self.current_edge = (v, new_v)
        self.t = 0.0

    def update(self, dt):
        self.t += self.speed * dt
        if self.t >= 1.0:
            self.choose_random_edge(initial=False)
