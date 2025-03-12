import math
import time

from city import City
from PyQt5.QtCore import QPointF, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QOpenGLWidget,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class Visualizer(QWidget):
    def __init__(self, civ, edition_mode: bool):
        """
        civ: une instance de la classe Civilization.
        """
        super().__init__()
        self.setWindowTitle("Ant Colony Simulation")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("assets/logo.webp"))

        # Créer un layout principal pour les contrôles overlay
        self.main_layout = QVBoxLayout(self)

        # Créer le canvas OpenGL qui affiche la simulation
        if edition_mode:
            self.canvas = SimulationCanvas(civ, parent=self)
        else:
            self.canvas = Canvas(civ, parent=self)
        self.canvas.setGeometry(0, 0, self.width(), self.height())
        self.canvas.show()

        # Interrupteur (CheckBox) pour afficher/masquer le texte sous les routes
        self.road_text_checkbox = QCheckBox("Show Road Text", self)
        self.road_text_checkbox.setFont(QFont("Roboto", 8))
        self.road_text_checkbox.setChecked(True)
        self.road_text_checkbox.setGeometry(self.width() - 170, 80, 150, 20)
        self.road_text_checkbox.stateChanged.connect(self.toggleRoadText)
        self.road_text_checkbox.setStyleSheet("color: white;")

        # S'assurer que ces widgets overlay restent au premier plan
        self.road_text_checkbox.raise_()

    def resizeEvent(self, event):
        # Repositionner le canvas et les contrôles lors d'un redimensionnement
        self.canvas.setGeometry(0, 0, self.width(), self.height())
        self.road_text_checkbox.setGeometry(self.width() - 170, 80, 150, 20)
        super().resizeEvent(event)

    def toggleRoadText(self, state):
        show_text = state == Qt.Checked
        self.canvas.setShowRoadText(show_text)


# La classe de base qui factorise le code commun
class BaseCanvas(QOpenGLWidget):
    def __init__(self, civ, parent=None):
        super().__init__(parent)
        self.civ = civ  # Instance de la civilisation
        self.cached_layout = None
        self.ants = self.civ.get_ants()
        self.ant_progress = {ant: 0.0 for ant in self.ants}
        self.ant_speed = 1.0  # Vitesse par défaut (modifiable via le slider)
        self.last_update = time.time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.start(16)  # environ 60 FPS
        self.start_time = time.time()
        self.ant_launch_delta = self.ant_speed * 0.04
        self.ant_launch_time = {
            ant: self.start_time + i * self.ant_launch_delta
            for i, ant in enumerate(self.ants)
        }
        self.best_path_text = "Best Path: N/A"
        self.show_road_text = True

        # Initialisation commune des widgets (paramètres des fourmis)
        self.init_input_widgets()

    def init_input_widgets(self):
        """Initialise les éléments d’interface pour configurer les paramètres des fourmis."""
        self.input_group = QGroupBox("Ants parameters", self)
        self.input_group.setGeometry(100, 100, 350, 400)
        self.input_group.setStyleSheet(
            """
            QGroupBox {
                background-color: grey;
                border-radius: 10px;
                padding: 10px;
                font-family: Roboto;
                font-size: 20px;
            }
            QGroupBox::title {
                font-size: 30px;
                font-weight: bold;
                subcontrol-origin: margin;
                subcontrol-position: top center;
                color: #2c3e50;
                font-family: 'Roboto';
            }
        """
        )
        main_layout = QVBoxLayout(self.input_group)
        form_layout = QFormLayout()

        self.size_input = QLineEdit()
        self.alpha_input = QLineEdit()
        self.beta_input = QLineEdit()
        self.gamma_input = QLineEdit()

        # Fixer une taille uniforme aux QLineEdit
        for line_edit in (
            self.size_input,
            self.alpha_input,
            self.beta_input,
            self.gamma_input,
        ):
            line_edit.setFixedWidth(120)

        form_layout.addRow(QLabel("Nombre de fourmis:"), self.size_input)
        form_layout.addRow(QLabel("Alpha:"), self.alpha_input)
        form_layout.addRow(QLabel("Beta:"), self.beta_input)
        form_layout.addRow(QLabel("Gamma:"), self.gamma_input)
        main_layout.addLayout(form_layout)

        # Bouton pour choisir une couleur avec affichage du résultat
        color_layout = QHBoxLayout()
        self.color_button = QPushButton("Choisir une couleur")
        self.color_button.setFixedSize(150, 30)
        self.color_button.clicked.connect(self.choose_color)
        self.color_display = QLabel()
        self.color_display.setFixedSize(40, 40)
        self.color_display.setStyleSheet(
            "background-color: white; border: 1px solid black; border-radius: 20px;"
        )
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_display)
        main_layout.addLayout(color_layout)

        # Slider pour la vitesse des fourmis
        speed_layout = QHBoxLayout()
        self.speed_label = QLabel("Ant Speed: 1", self)
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(30)
        self.speed_slider.setValue(1)
        self.speed_slider.setTickInterval(2)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.valueChanged.connect(self.updateAntSpeed)
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_slider)
        main_layout.addLayout(speed_layout)

        # Boutons "Ajouter" et "Valider"
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter")
        self.add_button.setFixedSize(100, 30)
        self.add_button.clicked.connect(self.compose_colony_ants)
        self.validate_button = QPushButton("Valider")
        self.validate_button.setFixedSize(100, 30)
        self.validate_button.clicked.connect(self.start_animation_after_composition)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.validate_button)
        main_layout.addLayout(button_layout)

        self.first_composition_done = False

        self.apply_styles()

    def apply_styles(self):
        """Applique un style global aux widgets."""
        self.setStyleSheet(
            """
            QLabel {
                font-family: "Roboto";
                font-size: 20px;
                color: white;
            }
            QLineEdit {
                border: 2px solid gray;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
        """
        )

    def choose_color(self):
        """Ouvre une boîte de dialogue pour choisir une couleur."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_display.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid black; border-radius: 20px;"
            )

    def updateAntSpeed(self, value):
        """Met à jour le label et la vitesse des fourmis."""
        self.speed_label.setText(f"Ant Speed: {value}")
        self.setAntSpeed(value)

    def compose_colony_ants(self):
        if not self.first_composition_done:
            self.civ.reset_ants()
            self.first_composition_done = True  # Marquer comme exécuté
        try:
            colony_size = int(self.size_input.text())
            print(colony_size)
            alpha = float(self.alpha_input.text())
            gamma = float(self.gamma_input.text())
            beta = float(self.beta_input.text())
            self.civ.create_ant_colony(colony_size, alpha, gamma, beta)
        except ValueError:
            self.result_label.setText("Veuillez entrer des valeurs valides")

    def start_animation_after_composition(self):
        """Réinitialise les paramètres d'animation et démarre la simulation."""
        self.ants = self.civ.get_ants()
        colony_size = len(self.ants)
        new_initial_pheromone = colony_size / 1000
        self.civ.set_initial_pheromone(new_initial_pheromone)
        for road in self.civ.get_roads():
            road.reset_pheromone(self.civ.get_initial_pheromone())
        self.civ.steps = 0
        self.ant_progress = {ant: 0.0 for ant in self.ants}
        self.start_time = time.time()
        self.last_update = time.time()
        self.ant_launch_delta = self.ant_speed * 0.04
        self.ant_launch_time = {
            ant: self.start_time + i * self.ant_launch_delta
            for i, ant in enumerate(self.ants)
        }
        self.civ.step()
        self.best_path_text = "Best Path: N/A"
        self.cached_layout = None

        self.first_composition_done = False
        self.update()

    def updateAnimation(self):
        """Met à jour l’animation des fourmis et déclenche l’étape suivante de la simulation."""
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        all_finished = True
        for ant in self.ants:
            if now < self.ant_launch_time[ant]:
                all_finished = False
                continue
            progress = self.ant_progress[ant] + ant.get_speed() * dt * self.ant_speed
            if progress >= 1.0:
                self.ant_progress[ant] = 1.0
            else:
                self.ant_progress[ant] = progress
                all_finished = False

        if all_finished:
            self.civ.step()
            best_path = self.civ.get_best_path()  # Renvoie une liste de City
            if best_path:
                self.best_path_text = "Best Path: " + " > ".join(
                    str(city.get_id()) for city in best_path
                )
            else:
                self.best_path_text = "Best Path: N/A"
            for ant in self.ants:
                self.ant_progress[ant] = 0.0
            self.start_time = time.time()
            self.ant_launch_time = {
                ant: self.start_time + i * self.ant_launch_delta
                for i, ant in enumerate(self.ants)
            }

        self.update()  # Redessine le widget

    def paintGL(self):
        """Méthode commune de rendu (dessin des routes, villes, fourmis et textes)."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(50, 50, 50))

        # Calcul du layout (peut être redéfini par les sous-classes)
        if self.cached_layout is None:
            self.cached_layout = self.get_layout()

        # Obtention des positions des villes (redéfinissable)
        node_positions = self.get_node_positions(self.cached_layout)

        # Dessin des routes
        edge_pen = QPen(QColor(255, 255, 255))
        edge_pen.setWidth(2)
        painter.setPen(edge_pen)
        roads = self.civ.get_roads()
        max_pheromone = max((road.get_pheromone() for road in roads), default=0)
        texts_to_draw = []
        for road in roads:
            start_city, end_city = road.get_cities()
            start = node_positions[start_city]
            end = node_positions[end_city]
            ratio = road.get_pheromone() / max_pheromone if max_pheromone > 0 else 0
            thickness = 2 + ratio * 8
            r = int((1 - ratio) * 255 + ratio * 37)
            g = int((1 - ratio) * 255 + ratio * 110)
            b = int((1 - ratio) * 255 + ratio * 255)
            road_color = QColor(r, g, b)
            road_pen = QPen(road_color, thickness, Qt.SolidLine)
            painter.setPen(road_pen)
            painter.drawLine(start, end)

            # Préparation du texte (poids de la route et phéromone)
            if self.show_road_text:
                mid_point = QPointF(
                    (start.x() + end.x()) / 2, (start.y() + end.y()) / 2
                )
                offset_distance = 25
                offset_vector = self.calc_perp_offset(
                    start, end, offset_distance=offset_distance
                )
                text_pos = QPointF(
                    mid_point.x() + offset_vector.x(), mid_point.y() + offset_vector.y()
                )
                weight_text = str(road.get_weight())
                pheromone_text = str(round(road.get_pheromone(), 3))
                text = weight_text + " | " + pheromone_text
                angle_deg = math.degrees(
                    math.atan2(end.y() - start.y(), end.x() - start.x())
                )
                if angle_deg > 90 or angle_deg < -90:
                    angle_deg += 180
                texts_to_draw.append((text_pos, angle_deg, text))

        # Dessin des fourmis
        if self.ready_to_go():
            ant_radius = 8
            for ant in self.ants:
                u = ant.get_current_city()
                v = ant.get_next_city()
                if v is None:
                    continue
                start = node_positions[u]
                end = node_positions[v]
                t = self.ant_progress[ant]
                anim_x = (1 - t) * start.x() + t * end.x()
                anim_y = (1 - t) * start.y() + t * end.y()
                anim_pos = QPointF(anim_x, anim_y)
                painter.setBrush(QBrush(ant.get_color()))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(anim_pos, ant_radius, ant_radius)

        # Dessin des villes
        radius = 20
        border_width = 2
        for city, pos in node_positions.items():
            if city == self.civ.get_nest():
                fill_color = QColor(0, 150, 0)
            else:
                fill_color = QColor(139, 0, 0)
            painter.setBrush(QBrush(fill_color))
            painter.setPen(QPen(QColor(255, 255, 255), border_width))
            painter.drawEllipse(pos, radius + border_width, radius + border_width)
            painter.setBrush(QBrush(fill_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(pos, radius, radius)
            painter.setFont(QFont("Roboto", 16))
            painter.setPen(QPen(QColor(255, 255, 255)))
            city_text = str(city.get_id())
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(city_text)
            text_height = fm.height()
            painter.drawText(
                int(pos.x() - text_width / 2),
                int(pos.y() - text_height / 2),
                text_width,
                text_height,
                Qt.AlignCenter,
                city_text,
            )

        # Affichage du meilleur chemin
        painter.setFont(QFont("Roboto", 20))
        painter.setPen(QPen(QColor(230, 230, 230)))
        painter.drawText(10, 30, self.best_path_text)

        # Affichage des textes sur les routes
        painter.setFont(QFont("Roboto", 14))
        painter.setPen(QPen(QColor(255, 255, 255)))
        for text_pos, angle_deg, text in texts_to_draw:
            painter.save()
            painter.translate(text_pos)
            painter.rotate(angle_deg)
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            painter.drawText(int(-text_width / 2), int(text_height / 2), text)
            painter.restore()

        painter.end()

    def get_layout(self):
        """
        Méthode par défaut pour obtenir le layout.
        Si la civilisation dispose de 'compute_free_layout', on l'utilise,
        sinon on tente 'compute_layout'.
        """
        if hasattr(self.civ, "compute_free_layout"):
            return self.civ.compute_free_layout()
        elif hasattr(self.civ, "compute_layout"):
            return self.civ.compute_layout()
        else:
            return []

    def get_node_positions(self, layout):
        """
        Méthode par défaut pour obtenir les positions des villes.
        Ici, on ajoute un décalage pour centrer le layout.
        Cette méthode sera redéfinie dans SimulationCanvas.
        """
        center = self.rect().center()
        node_positions = {}
        cities = self.civ.get_cities()
        for i, city in enumerate(cities):
            pos = layout[i]
            node_positions[city] = QPointF(pos[0] + center.x(), pos[1] + center.y())
        return node_positions

    def ready_to_go(self):
        return self.ant_speed > 0

    def calc_perp_offset(
        self, start: QPointF, end: QPointF, offset_distance=10
    ) -> QPointF:
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        mag = math.sqrt(dx**2 + dy**2)
        if mag == 0:
            return QPointF(0, 0)
        offset_x = -dy / mag * offset_distance
        offset_y = dx / mag * offset_distance
        return QPointF(offset_x, offset_y)

    def setAntSpeed(self, speed):
        self.ant_speed = speed

    def setShowRoadText(self, flag):
        self.show_road_text = flag
        self.update()


# Canvas classique avec décalage central (utilise compute_layout)
class Canvas(BaseCanvas):
    def __init__(self, civ, parent=None):
        super().__init__(civ, parent)

    def get_layout(self):
        if hasattr(self.civ, "compute_layout"):
            return self.civ.compute_layout()
        return []

    def get_node_positions(self, layout):
        center = self.rect().center()
        node_positions = {}
        cities = self.civ.get_cities()
        for i, city in enumerate(cities):
            pos = layout[i]
            node_positions[city] = QPointF(pos[0] + center.x(), pos[1] + center.y())
        return node_positions


# SimulationCanvas qui utilise compute_free_layout et ne décale pas le layout
class SimulationCanvas(BaseCanvas):
    def __init__(self, civ, parent=None):
        super().__init__(civ, parent)
        # Attributs spécifiques à la gestion par clic
        self.current_road_start = None
        self.has_started = False

    def get_layout(self):
        if hasattr(self.civ, "compute_free_layout"):
            return self.civ.compute_free_layout()
        return []

    def get_node_positions(self, layout):
        node_positions = {}
        cities = self.civ.get_cities()
        for i, city in enumerate(cities):
            pos = layout[i]
            node_positions[city] = QPointF(pos[0], pos[1])
        return node_positions

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            # Si aucune ville n'est proche, en créer une nouvelle
            if self.find_city_near(pos) is None:
                new_city = City(len(self.civ.get_cities()))
                new_city.set_position(pos)
                self.civ.add_city(new_city)
            # Recalculer le layout avec la nouvelle ville
            self.cached_layout = self.civ.compute_free_layout()
            self.update()
        elif event.button() == Qt.RightButton:
            pos = event.pos()
            clicked_city = self.find_city_near(pos)
            if clicked_city:
                if self.current_road_start is None:
                    # Première sélection : stocker la ville de départ
                    self.current_road_start = clicked_city
                else:
                    # Si c'est une ville différente, créer une route
                    if clicked_city != self.current_road_start:
                        p1 = self.current_road_start.get_position()
                        p2 = clicked_city.get_position()
                        dist = round(
                            math.sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2),
                            2,
                        )
                        self.civ.add_road(
                            dist / 1500, self.current_road_start, clicked_city
                        )
                        self.current_road_start = None
                    self.cached_layout = self.civ.compute_free_layout()
                    self.update()

    def find_city_near(self, pos, radius=20):
        """Recherche une ville dont la position est proche de 'pos'."""
        for city in self.civ.get_cities():
            city_pos = city.get_position()
            if (
                math.sqrt((city_pos.x() - pos.x()) ** 2 + (city_pos.y() - pos.y()) ** 2)
                < radius
            ):
                return city
        return None
