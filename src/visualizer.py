import random
import time

import networkx as nx
import numpy as np
from PyQt5.QtCore import QPointF, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPen
from PyQt5.QtWidgets import QWidget
from sklearn.manifold import MDS

from ant import Ant


# Classe gérant la fenêtre, le rendu et l'animation
class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ant Colony Simulation")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("assets/logo.webp"))

        # --- Définition du graphe ---
        self.G = nx.Graph()
        self.G.add_nodes_from([0, 1, 2, 3])
        self.G.add_edge(0, 1, weight=7.0)
        self.G.add_edge(1, 2, weight=5.0)
        self.G.add_edge(2, 3, weight=5.0)
        self.G.add_edge(3, 0, weight=5.0)
        self.G.add_edge(1, 3, weight=5.0)

        self.scale_factor = 120  # 1 unité de poids correspond à 120 pixels
        self.nodes = list(self.G.nodes())
        self.n = len(self.nodes)
        self.node_index = {node: idx for idx, node in enumerate(self.nodes)}

        # --- Construction de la matrice de distances ---
        D = np.full((self.n, self.n), 500.0)
        np.fill_diagonal(D, 0)
        for u, v, data in self.G.edges(data=True):
            i, j = self.node_index[u], self.node_index[v]
            d = data["weight"] * self.scale_factor
            D[i, j] = d
            D[j, i] = d

        # --- Application de MDS pour obtenir les positions 2D ---
        mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
        self.positions = mds.fit_transform(D)

        # Polices utilisées pour le rendu
        self.node_font = QFont("Arial", 16)
        self.edge_font = QFont("Arial", 14)

        # Création d'un ensemble d'ants
        self.ants = [Ant(self.G, self.node_index) for _ in range(10)]

        self.last_update = time.time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.start(16)  # environ 60 FPS

    def updateAnimation(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now
        for ant in self.ants:
            ant.update(dt)
        self.update()  # déclenche paintEvent

    def calc_perp_offset(
        self, start: QPointF, end: QPointF, offset_distance=10
    ) -> QPointF:
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        mag = (dx**2 + dy**2) ** 0.5
        if mag == 0:
            return QPointF(0, 0)
        offset_x = -dy / mag * offset_distance
        offset_y = dx / mag * offset_distance
        return QPointF(offset_x, offset_y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(50, 50, 50))  # fond gris foncé
        center = self.rect().center()

        # Calculer la position des nœuds en ajoutant le centre aux positions MDS
        node_positions = {}
        for node in self.nodes:
            idx = self.node_index[node]
            pos = self.positions[idx]
            node_positions[node] = QPointF(pos[0] + center.x(), pos[1] + center.y())

        # Stylo pour les arêtes en blanc
        edge_pen = QPen(QColor(255, 255, 255))
        edge_pen.setWidth(2)
        painter.setPen(edge_pen)

        # Dessiner les arêtes et afficher les poids
        for u, v, data in self.G.edges(data=True):
            start = node_positions[u]
            end = node_positions[v]
            painter.drawLine(start, end)

            mid_point = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)
            offset_point = self.calc_perp_offset(start, end, offset_distance=10)
            text_pos = mid_point + offset_point

            painter.setFont(self.edge_font)
            painter.setPen(QPen(QColor(255, 140, 0)))  # poids en orange
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

        # Dessiner les nœuds avec un contour blanc
        radius = 15
        border_width = 2
        for node, pos in node_positions.items():
            # Contour blanc
            painter.setBrush(QBrush(QColor(139, 0, 0)))  # rouge foncé
            painter.setPen(QPen(QColor(255, 255, 255), border_width))
            painter.drawEllipse(pos, radius + border_width, radius + border_width)
            # Intérieur du nœud
            painter.setBrush(QBrush(QColor(139, 0, 0)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(pos, radius, radius)
            # Numéro du nœud en blanc
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

        # Dessiner les ants
        ant_radius = 8
        for ant in self.ants:
            u, v = ant.current_edge
            start = node_positions[u]
            end = node_positions[v]
            anim_x = (1 - ant.t) * start.x() + ant.t * end.x()
            anim_y = (1 - ant.t) * start.y() + ant.t * end.y()
            anim_pos = QPointF(anim_x, anim_y)
            painter.setBrush(QBrush(ant.color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(anim_pos, ant_radius, ant_radius)

        painter.end()
