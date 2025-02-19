import time

from PyQt5.QtCore import QPointF, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPen
from PyQt5.QtWidgets import QWidget
from sklearn.manifold import MDS


class Visualizer(QWidget):
    def __init__(self, civ):
        """
        civ: une instance de la classe Civilization.
        """
        super().__init__()
        self.setWindowTitle("Ant Colony Simulation")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("assets/logo.webp"))

        # Polices utilisées pour le rendu
        self.__city_font = QFont("Arial", 16)
        self.__road_font = QFont("Arial", 14)
        self.__best_path_font = QFont("Arial", 20)

        self.__civ = civ

        # Récupérer la liste des ants depuis la civilisation
        self.ants = self.__civ.get_ants()

        self.ant_progress = {ant: 0 for ant in self.ants}
        # Vitesse globale par défaut (si vous souhaitez l'utiliser)
        self.ant_speed = 1.0

        # Timer pour l'animation (environ 60 FPS)
        self.last_update = time.time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.start(16)

        self.start_time = time.time()
        self.ant_launch_delta = 0.05  # délai en secondes entre chaque lancement
        self.ant_launch_time = {
            ant: self.start_time + i * self.ant_launch_delta
            for i, ant in enumerate(self.ants)
        }

        self.best_path_text = "Best Path: N/A"

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

    def updateAnimation(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        all_finished = True
        for ant in self.ants:
            # Si le temps actuel n'a pas encore atteint le temps de lancement de cette ant,
            # on ne met pas à jour sa progression (elle reste à 0).
            if now < self.ant_launch_time[ant]:
                all_finished = False
                continue

            # Sinon, on met à jour la progression de l'ant avec sa vitesse propre.
            progress = self.ant_progress[ant] + ant.get_speed() * dt
            if progress >= 1.0:
                self.ant_progress[ant] = 1.0
            else:
                self.ant_progress[ant] = progress
                all_finished = False

        if all_finished:
            # Quand toutes les fourmis ont terminé leur déplacement,
            # faire évoluer la civilisation d'un step complet.
            self.__civ.step()

            best_path = self.__civ.get_best_path()  # Supposé renvoyer une liste de City
            if best_path:
                # Par exemple, on affiche les identifiants séparés par des flèches
                self.best_path_text = "Current Best Path: " + " > ".join(
                    str(city.get_id()) for city in best_path
                )
            else:
                self.best_path_text = "Best Path: N/A"

            # Réinitialiser la progression pour toutes les fourmis
            for ant in self.ants:
                self.ant_progress[ant] = 0.0
            # Recalcule les temps de lancement pour le prochain cycle :
            self.start_time = time.time()
            self.ant_launch_time = {
                ant: self.start_time + i * self.ant_launch_delta
                for i, ant in enumerate(self.ants)
            }

        self.update()  # Redessine la fenêtre.

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(50, 50, 50))  # Fond gris foncé

        center = self.rect().center()
        # Obtenir la liste des villes et calculer les positions via MDS
        cities = self.__civ.get_cities()  # Liste d'objets City
        layout = self.__civ.compute_layout()  # Tableau NumPy de forme (n,2)

        # Construire un dictionnaire associant chaque City à une position QPointF décalée par le centre
        node_positions = {}
        for i, city in enumerate(cities):
            pos = layout[i]
            node_positions[city] = QPointF(pos[0] + center.x(), pos[1] + center.y())

        # Dessiner les routes (arêtes)
        # Dessiner les routes (arêtes)
        edge_pen = QPen(QColor(255, 255, 255))
        edge_pen.setWidth(2)
        painter.setPen(edge_pen)

        import math

        # ... dans ta méthode paintEvent, dans la boucle sur les routes :

        roads = self.__civ.get_roads()  # Liste d'objets Road
        # Calcul du maximum de phéromone parmi toutes les routes
        max_pheromone = max((road.get_pheromone() for road in roads), default=0)

        for road in roads:
            start_city, end_city = road.get_cities()
            start = node_positions[start_city]
            end = node_positions[end_city]

            # Normaliser la phéromone
            ratio = road.get_pheromone() / max_pheromone if max_pheromone > 0 else 0

            # Ajuster l'épaisseur de la route (par exemple, entre 2 et 8 pixels)
            thickness = 2 + ratio * 6

            # Pour ratio=0, couleur blanche (255,255,255)
            # Pour ratio=1, couleur cible #124559 (18, 69, 89)
            r = int((1 - ratio) * 255 + ratio * 37)
            g = int((1 - ratio) * 255 + ratio * 110)
            b = int((1 - ratio) * 255 + ratio * 255)
            road_color = QColor(r, g, b)

            road_pen = QPen(road_color)
            road_pen.setWidthF(thickness)
            painter.setPen(road_pen)
            painter.drawLine(start, end)

            # Calcul du point médian de l'arête
            import math

            # ... Dans votre boucle de dessin des routes, après avoir calculé le point d'affichage du texte :
            # Calcul du point médian de l'arête
            mid_point = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)
            # On utilise calc_perp_offset avec un offset légèrement plus grand pour placer le texte "juste au-dessus"
            offset_distance = 25
            offset_vector = self.calc_perp_offset(
                start, end, offset_distance=offset_distance
            )
            text_pos = QPointF(
                mid_point.x() + offset_vector.x(), mid_point.y() + offset_vector.y()
            )

            # Préparation du texte
            weight_text = str(road.get_weight())
            pheromone_text = str(round(road.get_pheromone(), 3))
            text = weight_text + " | " + pheromone_text

            # Calculer l'angle de l'arête en degrés
            angle = math.degrees(math.atan2(end.y() - start.y(), end.x() - start.x()))

            # Ajuster l'angle pour éviter que le texte soit à l'envers :
            if angle > 90 or angle < -90:
                angle += 180

            # Sauvegarder l'état du painter pour appliquer la transformation localement
            painter.save()
            # Déplacer l'origine au point où le texte doit être dessiné
            painter.translate(text_pos)
            # Faire pivoter le painter de l'angle ajusté
            painter.rotate(angle)
            # Définir la couleur du texte (ici, gris clair)
            painter.setPen(QPen(QColor(230, 230, 230)))
            painter.setFont(self.__road_font)
            # Centrer le texte sur l'origine
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            # Convertir les valeurs en entiers
            painter.drawText(int(-text_width / 2), int(text_height / 2), text)
            # Restaurer l'état du painter
            painter.restore()

            # Remettre le stylo par défaut pour les arêtes
            painter.setPen(edge_pen)

        # Dessiner les ants (fourmis)
        ant_radius = 10
        for ant in self.ants:
            u = ant.get_current_city()  # Ville de départ (objet City)
            v = ant.get_next_city()  # Ville d'arrivée (objet City)
            start = node_positions[u]
            end = node_positions[v]
            t = self.ant_progress[ant]
            anim_x = (1 - t) * start.x() + t * end.x()
            anim_y = (1 - t) * start.y() + t * end.y()
            anim_pos = QPointF(anim_x, anim_y)
            painter.setBrush(QBrush(ant.get_color()))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(anim_pos, ant_radius, ant_radius)

        # Dessiner les villes avec un contour blanc et afficher leur identifiant
        radius = 20
        border_width = 2
        for city, pos in node_positions.items():
            painter.setBrush(QBrush(QColor(139, 0, 0)))  # Rouge foncé
            painter.setPen(QPen(QColor(255, 255, 255), border_width))
            painter.drawEllipse(pos, radius + border_width, radius + border_width)
            painter.setBrush(QBrush(QColor(139, 0, 0)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(pos, radius, radius)
            painter.setFont(self.__city_font)
            painter.setPen(QPen(QColor(255, 255, 255)))
            city_text = str(city.get_id())
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(city_text)
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
                city_text,
            )
            painter.setPen(edge_pen)

        # Dessiner le meilleur chemin en haut à gauche
        painter.setFont(self.__best_path_font)
        painter.setPen(QPen(QColor(230, 230, 230)))
        margin = 10
        painter.drawText(margin, margin + 20, self.best_path_text)

        painter.end()
