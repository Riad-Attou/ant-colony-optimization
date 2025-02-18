import random
import sys
import time

import networkx as nx
import numpy as np
from PyQt5.QtCore import QPointF, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget
from sklearn.manifold import MDS


class Ant:
    def __init__(self, graph, node_index):
        # Choisit aléatoirement une arête de départ
        self.graph = graph
        self.node_index = node_index
        self.current_edge = None  # (u, v)
        self.t = 0.0  # paramètre d'interpolation sur l'arête
        self.speed = random.uniform(
            0.75, 1.5
        )  # fraction du chemin parcourue par seconde
        # Couleur aléatoire
        self.color = QColor(
            random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)
        )
        self.choose_random_edge(initial=True)

    def choose_random_edge(self, initial=False):
        if initial:
            # Choix initial : choisir une arête aléatoire dans le graphe
            edge = random.choice(list(self.graph.edges()))
            # Choix de la direction au hasard
            if random.random() < 0.5:
                self.current_edge = edge  # (u,v)
            else:
                self.current_edge = (edge[1], edge[0])
        else:
            # Lorsque l'ant arrive à destination (v de l'arête courante),
            # on choisit aléatoirement une nouvelle destination parmi les voisins de v
            u, v = self.current_edge
            neighbors = list(self.graph.neighbors(v))
            # Optionnel : exclure le nœud précédent pour éviter de faire demi-tour
            if u in neighbors and len(neighbors) > 1:
                neighbors.remove(u)
            new_v = random.choice(neighbors)
            self.current_edge = (v, new_v)
        self.t = 0.0

    def update(self, dt):
        self.t += self.speed * dt
        if self.t >= 1.0:
            self.choose_random_edge(initial=False)


class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ant Colony Optimization")
        self.setWindowIcon(QIcon("assets/logo.webp"))
        self.setMinimumSize(800, 600)

        # --- 1. Définir le graphe avec les poids souhaités ---
        self.G = nx.Graph()
        self.G.add_nodes_from([0, 1, 2, 3])
        self.G.add_edge(0, 1, weight=7.0)
        self.G.add_edge(1, 2, weight=5.0)
        self.G.add_edge(2, 3, weight=5.0)
        self.G.add_edge(3, 0, weight=5.0)
        self.G.add_edge(1, 3, weight=5.0)

        # Échelle pour convertir le poids en distance visuelle (en pixels)
        self.scale_factor = 120  # Une unité de poids = self.scale_factor pixels

        self.nodes = list(self.G.nodes())
        self.n = len(self.nodes)
        self.node_index = {node: idx for idx, node in enumerate(self.nodes)}

        # --- 2. Construire la matrice des distances souhaitées ---
        D = np.full((self.n, self.n), 500.0)
        np.fill_diagonal(D, 0)
        for u, v, data in self.G.edges(data=True):
            i, j = self.node_index[u], self.node_index[v]
            d = data["weight"] * self.scale_factor
            D[i, j] = d
            D[j, i] = d

        # --- 3. Appliquer MDS pour obtenir une configuration 2D ---
        mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
        self.positions = mds.fit_transform(D)

        # Configuration des polices pour afficher les numéros et les poids
        self.node_font = QFont("Arial", 16)
        self.edge_font = QFont("Arial", 14)

        # Création de plusieurs "ants" qui se déplacent dans le graphe
        self.ants = [Ant(self.G, self.node_index) for _ in range(10)]

        # Pour mesurer le temps écoulé
        self.last_update = time.time()

        # QTimer pour l'animation : intervalle de 16 ms pour ~60 FPS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.start(10)

    def updateAnimation(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now
        for ant in self.ants:
            ant.update(dt)
        self.update()  # redessiner la fenêtre

    def calc_perp_offset(
        self, start: QPointF, end: QPointF, offset_distance=10
    ) -> QPointF:
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        mag = np.hypot(dx, dy)
        if mag == 0:
            return QPointF(0, 0)
        offset_x = -dy / mag * offset_distance
        offset_y = dx / mag * offset_distance
        return QPointF(offset_x, offset_y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fond uni en gris foncé
        painter.fillRect(self.rect(), QColor(50, 50, 50))

        # Calculer le centre de la fenêtre
        center = self.rect().center()

        # Calculer les positions des nœuds en ajoutant le centre de la fenêtre
        node_positions = {}
        for node in self.nodes:
            idx = self.node_index[node]
            pos = self.positions[idx]
            node_positions[node] = QPointF(pos[0] + center.x(), pos[1] + center.y())

        # Définir le stylo pour les arêtes (blanc)
        edge_pen = QPen(QColor(255, 255, 255))
        edge_pen.setWidth(2)
        painter.setPen(edge_pen)

        # Dessiner les arêtes et afficher les poids
        for u, v, data in self.G.edges(data=True):
            start = node_positions[u]
            end = node_positions[v]
            painter.drawLine(start, end)

            # Calculer le milieu de l'arête
            mid_point = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)
            # Calculer l'offset perpendiculaire
            offset_point = self.calc_perp_offset(start, end, offset_distance=10)
            text_pos = mid_point + offset_point

            # Afficher le poids en orange
            painter.setFont(self.edge_font)
            painter.setPen(QPen(QColor(255, 140, 0)))
            weight_text = str(data["weight"])
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(weight_text)
            text_height = fm.height()
            rect = (
                text_pos.x() - text_width / 2,
                text_pos.y() - text_height / 2,
                text_width,
                text_height,
            )
            painter.drawText(
                int(rect[0]),
                int(rect[1]),
                int(rect[2]),
                int(rect[3]),
                Qt.AlignCenter,
                weight_text,
            )
            painter.setPen(edge_pen)

        # Dessiner les nœuds avec contour blanc
        radius = 15
        border_width = 2
        for node, pos in node_positions.items():
            # Dessiner le contour blanc
            painter.setBrush(QBrush(QColor(139, 0, 0)))
            painter.setPen(QPen(QColor(255, 255, 255), border_width))
            painter.drawEllipse(pos, radius + border_width, radius + border_width)
            # Dessiner le remplissage intérieur
            painter.setBrush(QBrush(QColor(139, 0, 0)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(pos, radius, radius)
            # Afficher le numéro du nœud en blanc
            painter.setFont(self.node_font)
            painter.setPen(QPen(QColor(255, 255, 255)))
            node_text = str(node)
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(node_text)
            text_height = fm.height()
            label_rect = (
                pos.x() - text_width / 2,
                pos.y() - text_height / 2,
                text_width,
                text_height,
            )
            painter.drawText(
                int(label_rect[0]),
                int(label_rect[1]),
                int(label_rect[2]),
                int(label_rect[3]),
                Qt.AlignCenter,
                node_text,
            )
            painter.setPen(edge_pen)

        # --- Animation : dessiner tous les ants ---
        ant_radius = 8
        for ant in self.ants:
            u, v = ant.current_edge
            start = node_positions[u]
            end = node_positions[v]
            # Position interpolée le long de l'arête
            anim_x = (1 - ant.t) * start.x() + ant.t * end.x()
            anim_y = (1 - ant.t) * start.y() + ant.t * end.y()
            anim_pos = QPointF(anim_x, anim_y)
            painter.setBrush(QBrush(ant.color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(anim_pos, ant_radius, ant_radius)

        painter.end()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = GraphWidget()
    widget.show()
    sys.exit(app.exec_())
