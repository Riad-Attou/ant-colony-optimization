import math
import time

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

from city import City


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

        # # Curseur pour la vitesse des ants (overlay en haut à droite)
        # self.speed_slider = QSlider(Qt.Horizontal, self)
        # self.speed_slider.setFont(QFont("Roboto", 8))
        # self.speed_slider.setMinimum(0)
        # self.speed_slider.setMaximum(30)
        # self.speed_slider.setValue(0)
        # self.speed_slider.setTickInterval(2)
        # self.speed_slider.setTickPosition(QSlider.TicksBelow)
        # self.speed_slider.setGeometry(self.width() - 170, 20, 150, 30)
        # self.speed_slider.valueChanged.connect(self.updateAntSpeed)

        # self.speed_label = QLabel("Ant Speed: 0", self)
        # self.speed_label.setGeometry(self.width() - 170, 55, 150, 20)
        # self.speed_label.setStyleSheet("color: white;")

        # Interrupteur (CheckBox) pour afficher/masquer le texte sous les routes
        self.road_text_checkbox = QCheckBox("Show Road Text", self)
        self.road_text_checkbox.setFont(QFont("Roboto", 8))
        self.road_text_checkbox.setChecked(True)
        self.road_text_checkbox.setGeometry(self.width() - 170, 80, 150, 20)
        self.road_text_checkbox.stateChanged.connect(self.toggleRoadText)
        self.road_text_checkbox.setStyleSheet("color: white;")

        # S'assurer que ces widgets overlay restent au premier plan
        # self.speed_slider.raise_()
        # self.speed_label.raise_()
        self.road_text_checkbox.raise_()

    def resizeEvent(self, event):
        # Repositionner le canvas et les contrôles lors d'un redimensionnement
        self.canvas.setGeometry(0, 0, self.width(), self.height())
        # self.speed_slider.setGeometry(self.width() - 170, 20, 150, 30)
        # self.speed_label.setGeometry(self.width() - 170, 55, 150, 20)
        self.road_text_checkbox.setGeometry(self.width() - 170, 80, 150, 20)
        super().resizeEvent(event)

    def toggleRoadText(self, state):
        show_text = state == Qt.Checked
        self.canvas.setShowRoadText(show_text)


# La classe Canvas est maintenant basée sur QOpenGLWidget pour profiter de l'accélération matérielle.
class SimulationCanvas2(QOpenGLWidget):
    def __init__(self, civ, parent=None):
        super().__init__(parent)
        # Polices pour le rendu
        self.__city_font = QFont("OpenSans", 16)
        self.__road_font = QFont("Roboto", 14)
        self.__best_path_font = QFont("Roboto", 20)

        self.__civ = civ

        self.cached_layout = None  # Pour stocker le layout calculé

        # Récupérer les ants depuis la civilisation
        self.ants = self.__civ.get_ants()
        # Initialiser la progression de chaque ant à 0 (toutes partent du même point)
        self.ant_progress = {ant: 0.0 for ant in self.ants}
        # Vitesse globale par défaut (multiplicateur)
        self.ant_speed = 0.0

        self.last_update = time.time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.start(16)  # environ 60 FPS

        self.start_time = time.time()
        self.ant_launch_delta = 0.04  # délai entre lancements
        self.ant_launch_time = {
            ant: self.start_time + i * self.ant_launch_delta
            for i, ant in enumerate(self.ants)
        }

        self.best_path_text = "Current Best Path: N/A"

        # Propriété pour afficher ou masquer le texte sur les routes
        self.show_road_text = True
        self.current_road_start = None  # Pour la création d'une route
        self.has_started = False
        self.last_draw = time.time()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            # Si aucune ville n'est proche, créer une nouvelle ville
            if self.find_city_near(pos) is None:
                new_city = City(len(self.__civ.get_cities()))
                new_city.set_position(pos)
                self.__civ.add_city(new_city)
            self.cached_layout = self.__civ.compute_free_layout()
            self.update()
        elif event.button() == Qt.RightButton:
            pos = event.pos()
            clicked_city = self.find_city_near(pos)
            if clicked_city:
                if self.current_road_start is None:
                    # Première sélection
                    self.current_road_start = clicked_city
                else:
                    print(clicked_city)
                    # Si c'est une ville différente, créer une route entre la ville de départ et celle cliquée
                    if clicked_city != self.current_road_start:
                        p1 = self.current_road_start.get_position()
                        p2 = clicked_city.get_position()
                        # Calculer la distance euclidienne pour le poids
                        dist = round(
                            math.sqrt((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2),
                            2,
                        )
                        self.__civ.add_road(
                            dist / 1500, self.current_road_start, clicked_city
                        )

                        # MODIFICATION : Faire de la ville de fin le nouveau point de départ
                        self.current_road_start = clicked_city

                    self.cached_layout = self.__civ.compute_free_layout()
                    self.update()

    def find_city_near(self, pos, radius=20):
        # Recherche une ville dont la position est proche de pos
        for city in self.__civ.get_cities():
            city_pos = city.get_position()
            # On peut utiliser la distance euclidienne ou Manhattan; ici, euclidienne
            if (
                math.sqrt((city_pos.x() - pos.x()) ** 2 + (city_pos.y() - pos.y()) ** 2)
                < radius
            ):
                return city
        return None

    # Méthode de configuration OpenGL
    def initializeGL(self):
        # Par exemple, définir la couleur de fond OpenGL (mais ici, on utilise QPainter pour remplir le widget)
        pass

    def resizeGL(self, w, h):
        # Gestion du redimensionnement OpenGL si nécessaire
        pass

    def ready_to_go(self):
        return self.ant_speed > 0

    def paintGL(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(50, 50, 50))

        if self.cached_layout is None:
            self.cached_layout = self.__civ.compute_free_layout()

        cities = self.__civ.get_cities()
        node_positions = {}
        for i, city in enumerate(cities):
            pos = self.cached_layout[i]
            node_positions[city] = QPointF(pos[0], pos[1])

        edge_pen = QPen(QColor(255, 255, 255))
        edge_pen.setWidth(2)
        painter.setPen(edge_pen)
        roads = self.__civ.get_roads()
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

            road_pen = QPen(Qt.white, 2, Qt.SolidLine)
            painter.setPen(road_pen)

            # Trouver le milieu de la ligne
            middle = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)

            # Calcul de l'angle de la ligne
            dx = end.x() - start.x()
            dy = end.y() - start.y()
            angle = math.atan2(dy, dx)  # Angle en radians

            # Définition du triangle plus équilibré
            arrow_size = 30
            arrow_angle = math.radians(30)  # Angle d'ouverture

            # Calcul des points du triangle
            arrow_p1 = QPointF(
                middle.x() - arrow_size * math.cos(angle - arrow_angle),
                middle.y() - arrow_size * math.sin(angle - arrow_angle),
            )
            arrow_p2 = QPointF(
                middle.x() - arrow_size * math.cos(angle + arrow_angle),
                middle.y() - arrow_size * math.sin(angle + arrow_angle),
            )

            # Création du triangle de la flèche
            arrow_head = QPolygonF([middle, arrow_p1, arrow_p2])
            painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
            painter.setPen(QPen(road_color, 4))
            painter.drawPolygon(arrow_head)

            # Préparer le texte à dessiner, mais ne le dessinerons qu'après
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
                angle = math.degrees(
                    math.atan2(end.y() - start.y(), end.x() - start.x())
                )
                if angle > 90 or angle < -90:
                    angle += 180
                # Stocker ces infos pour dessiner le texte après
                texts_to_draw.append((text_pos, angle, text))

        if self.ready_to_go():
            if not self.has_started:
                self.has_started = True
                self.__civ.step()
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

        radius = 20
        border_width = 2
        for city, pos in node_positions.items():
            if city == self.__civ.get_nest():
                fill_color = QColor(0, 150, 0)  # Vert sombre pour le nid
            elif city == self.__civ.get_food_source():
                fill_color = QColor(200, 100, 10)  # Orange pour la source
            else:
                fill_color = QColor(139, 0, 0)  # Rouge foncé pour les autres
            painter.setBrush(QBrush(fill_color))
            painter.setPen(QPen(QColor(255, 255, 255), border_width))
            painter.drawEllipse(pos, radius + border_width, radius + border_width)
            painter.setBrush(QBrush(fill_color))
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

        painter.setFont(self.__best_path_font)
        painter.setPen(QPen(QColor(230, 230, 230)))
        margin = 10
        painter.drawText(margin, margin + 20, self.best_path_text)

        # Maintenant, dessiner tous les textes sur les routes, par-dessus tout
        painter.setFont(self.__road_font)
        painter.setPen(QPen(QColor(255, 255, 255)))
        for text_pos, angle, text in texts_to_draw:
            painter.save()
            painter.translate(text_pos)
            painter.rotate(angle)
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            painter.drawText(int(-text_width / 2), int(text_height / 2), text)
            painter.restore()

        painter.end()

    def setAntSpeed(self, speed):
        self.ant_speed = speed

    def setShowRoadText(self, flag):
        self.show_road_text = flag
        self.update()

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
            self.__civ.step()
            best_path = self.__civ.get_best_path()  # Renvoie une liste de City
            if best_path:
                self.best_path_text = "Current best Path: " + " > ".join(
                    str(city.get_id()) for city in best_path
                )
            else:
                self.best_path_text = "Current Best Path: N/A"
            for ant in self.ants:
                self.ant_progress[ant] = 0.0
            self.start_time = time.time()
            self.ant_launch_time = {
                ant: self.start_time + i * self.ant_launch_delta
                for i, ant in enumerate(self.ants)
            }

        self.update()  # Redessine la fenêtre


# La classe Canvas est maintenant basée sur QOpenGLWidget pour profiter de l'accélération matérielle.
class Canvas2(QOpenGLWidget):
    def __init__(self, civ, parent=None):
        super().__init__(parent)
        # Polices pour le rendu
        self.__city_font = QFont("Roboto", 16)
        self.__road_font = QFont("Roboto", 14)
        self.__best_path_font = QFont("Roboto", 20)

        self.__civ = civ

        self.cached_layout = None  # Pour stocker le layout calculé

        # Récupérer les ants depuis la civilisation
        self.ants = self.__civ.get_ants()
        # Initialiser la progression de chaque ant à 0 (toutes partent du même point)
        self.ant_progress = {ant: 0.0 for ant in self.ants}
        # Vitesse globale par défaut (multiplicateur)
        self.ant_speed = 1.0

        self.last_update = time.time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.start(16)  # environ 60 FPS
        self.start_time = time.time()
        self.ant_launch_delta = self.ant_speed * 0.04  # délai entre lancements

        self.ant_launch_time = {
            ant: self.start_time + i * self.ant_launch_delta
            for i, ant in enumerate(self.ants)
        }

        self.best_path_text = "Best Path: N/A"

        # Propriété pour afficher ou masquer le texte sur les routes
        self.show_road_text = True

        self.first_composition_done = False
        # Initialisation des widgets d'entrée
        self.init_input_widgets()

    def init_input_widgets(self):
        """Initialise les widgets pour la saisie des paramètres de fourmis"""

        # --- 1) Création du QGroupBox pour tout regrouper ---
        self.input_group = QGroupBox("Ants parameters\n", self)
        self.input_group.setGeometry(
            100, 100, 350, 400
        )  # Position et taille du group box
        self.input_group.setStyleSheet(
            """
            QGroupBox {
                background-color: grey;    /* Couleur de fond */
                border-radius: 10px;
                padding: 10px;
                font-family: Roboto;       /* Police par défaut pour le contenu */
                font-size: 20px;          /* Taille de police du contenu */
            }
            QGroupBox::title {
                font-size: 30px;          /* Titre plus grand */
                font-weight: bold;        /* Titre en gras */
                subcontrol-origin: margin;
                subcontrol-position: top center;  /* Centre le titre */
                color: #2c3e50;           /* Couleur du titre */
                font-family: 'Roboto';     /* Police (peut être différente du contenu) */
            }
            """
        )

        # Layout principal vertical du group box
        main_layout = QVBoxLayout(self.input_group)

        # --- 2) Champs de saisie avec QFormLayout pour un alignement vertical ---
        form_layout = QFormLayout()

        self.size_input = QLineEdit()
        self.gamma_input = QLineEdit()
        self.alpha_input = QLineEdit()
        self.beta_input = QLineEdit()

        # Fixe la même taille pour tous les QLineEdit
        for line_edit in (
            self.size_input,
            self.gamma_input,
            self.alpha_input,
            self.beta_input,
        ):
            line_edit.setFixedWidth(120)

        # Ajoute chaque champ (label + input) dans le FormLayout
        form_layout.addRow(QLabel("Nombre de fourmis :"), self.size_input)
        form_layout.addRow(QLabel("Alpha :"), self.alpha_input)
        form_layout.addRow(QLabel("Beta :"), self.beta_input)
        form_layout.addRow(QLabel("Gamma :"), self.gamma_input)

        main_layout.addLayout(form_layout)

        # --- 3) Bouton "Choisir une couleur" et affichage circulaire de la couleur ---
        color_layout = QHBoxLayout()

        self.color_button = QPushButton("Choisir une couleur")
        self.color_button.setFixedSize(150, 30)
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button, alignment=Qt.AlignLeft)

        # Cercle pour afficher la couleur choisie
        self.color_display = QLabel()
        self.color_display.setFixedSize(40, 40)
        # Pour un cercle parfait, la valeur de border-radius doit être la moitié de la taille
        self.color_display.setStyleSheet(
            "background-color: white; border: 1px solid black; border-radius: 20px;"
        )

        # Ajoute le bouton et le cercle dans un layout horizontal (sous les champs)
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_display)
        main_layout.addLayout(color_layout)

        # --- 1) Layout horizontal pour la vitesse des fourmis (slider + label) ---
        speed_layout = QHBoxLayout()

        self.speed_label = QLabel("Ant Speed: 1", self)
        self.speed_label.setStyleSheet("color: white;")

        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(30)
        self.speed_slider.setValue(1)
        self.speed_slider.setTickInterval(2)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.valueChanged.connect(self.updateAntSpeed)

        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.setAlignment(Qt.AlignCenter)  # Aligner à droite
        main_layout.addLayout(speed_layout)

        button_layout = QHBoxLayout()
        # Bouton "Ajouter"
        self.add_button = QPushButton("Ajouter")
        self.add_button.setFixedSize(100, 30)
        button_layout.addWidget(self.add_button, alignment=Qt.AlignLeft)
        self.add_button.clicked.connect(self.compose_colont_ants)

        # Bouton "Valider"
        self.validate_button = QPushButton("Valider")
        self.validate_button.setFixedSize(100, 30)
        button_layout.addWidget(self.validate_button, alignment=Qt.AlignRight)
        self.validate_button.clicked.connect(self.start_animation_after_composition)

        # Ajouter le layout horizontal au layout principal
        main_layout.addLayout(button_layout)

        # --- 5) Application des styles généraux éventuels ---
        self.apply_styles()

    def updateAntSpeed(self, value):
        """Met à jour le texte du label et la vitesse des fourmis"""
        self.speed_label.setText(f"Ant Speed: {value}")
        self.setAntSpeed(value)

    def create_input(self, label_text, x, y):
        """
        Si vous souhaitez conserver cette méthode pour créer des champs,
        vous pouvez l'adapter pour ne plus utiliser setGeometry(),
        et retourner simplement un widget (label + lineedit) dans un layout.
        """
        label = QLabel(label_text, self)
        input_field = QLineEdit(self)
        input_field.setFixedWidth(120)

        # Layout horizontal (label + champ)
        row_layout = QHBoxLayout()
        row_layout.addWidget(label)
        row_layout.addWidget(input_field)

        # Container
        container = QWidget(self)
        container.setLayout(row_layout)

        return container

    def choose_color(self):
        """Ouvre un color picker et applique la couleur sélectionnée"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_display.setStyleSheet(
                f"background-color: {color.name()}; "
                "border: 1px solid black; "
                "border-radius: 15px;"
            )

    def apply_styles(self):
        """Applique un style global aux widgets (si nécessaire)"""
        self.setStyleSheet(
            """
            QLabel {
                font-family: "Roboto";
                font-size: 20px;
                color: white;  /* Exemple : texte blanc */
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

    # Méthode de configuration OpenGL
    def initializeGL(self):
        # Par exemple, définir la couleur de fond OpenGL (mais ici, on utilise QPainter pour remplir le widget)
        pass

    def resizeGL(self, w, h):
        # Gestion du redimensionnement OpenGL si nécessaire
        pass

    def paintGL(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        center = self.rect().center()

        if self.cached_layout is None:
            self.cached_layout = self.__civ.compute_layout()

        cities = self.__civ.get_cities()
        node_positions = {}
        for i, city in enumerate(cities):
            pos = self.cached_layout[i]
            node_positions[city] = QPointF(pos[0] + center.x(), pos[1] + center.y())

        edge_pen = QPen(QColor(255, 255, 255))
        edge_pen.setWidth(2)
        painter.setPen(edge_pen)
        roads = self.__civ.get_roads()
        max_pheromone = max((road.get_pheromone() for road in roads), default=0)
        texts_to_draw = []
        for road in roads:
            start_city, end_city = road.get_cities()
            start = node_positions[start_city]
            end = node_positions[end_city]
            ratio = max(
                (
                    (
                        road.get_pheromone()
                        - min(road.get_pheromone(), self.__civ.get_initial_pheromone())
                    )
                    / (max_pheromone - self.__civ.get_initial_pheromone())
                    if max_pheromone > 0
                    else 0
                ),
                0,
            )
            thickness = 2 + ratio * 10
            r = int((1 - ratio) * 255 + ratio * 37)
            g = int((1 - ratio) * 255 + ratio * 110)
            b = int((1 - ratio) * 255 + ratio * 255)
            road_color = QColor(r, g, b)
            road_pen = QPen(road_color, thickness, Qt.SolidLine)
            painter.setPen(road_pen)
            painter.drawLine(start, end)

            road_pen = QPen(Qt.white, 2, Qt.SolidLine)
            painter.setPen(road_pen)

            # Trouver le milieu de la ligne
            middle = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)

            # Calcul de l'angle de la ligne
            dx = end.x() - start.x()
            dy = end.y() - start.y()
            angle = math.atan2(dy, dx)  # Angle en radians

            # Définition du triangle plus équilibré
            arrow_size = 30
            arrow_angle = math.radians(30)  # Angle d'ouverture

            # Calcul des points du triangle
            arrow_p1 = QPointF(
                middle.x() - arrow_size * math.cos(angle - arrow_angle),
                middle.y() - arrow_size * math.sin(angle - arrow_angle),
            )
            arrow_p2 = QPointF(
                middle.x() - arrow_size * math.cos(angle + arrow_angle),
                middle.y() - arrow_size * math.sin(angle + arrow_angle),
            )

            # Création du triangle de la flèche
            arrow_head = QPolygonF([middle, arrow_p1, arrow_p2])
            painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
            painter.setPen(QPen(road_color, 4))
            painter.drawPolygon(arrow_head)

            # Préparer le texte à dessiner, mais ne le dessinerons qu'après
            if self.show_road_text:
                mid_point = QPointF(
                    (start.x() + end.x()) / 2, (start.y() + end.y()) / 2
                )
                offset_distance = 35
                offset_vector = self.calc_perp_offset(
                    start, end, offset_distance=offset_distance
                )
                text_pos = QPointF(
                    mid_point.x() + offset_vector.x(), mid_point.y() + offset_vector.y()
                )

                weight_text = str(road.get_weight())
                pheromone_text = str(round(road.get_pheromone(), 3))
                text = weight_text + " | " + pheromone_text
                angle = math.degrees(
                    math.atan2(end.y() - start.y(), end.x() - start.x())
                )
                if angle > 90 or angle < -90:
                    angle += 180
                # Stocker ces infos pour dessiner le texte après
                texts_to_draw.append((text_pos, angle, text))

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

        radius = 20
        border_width = 2
        for city, pos in node_positions.items():
            if city == self.__civ.get_nest():
                fill_color = QColor(0, 150, 0)  # Vert sombre pour le nid
            elif city == self.__civ.get_food_source():
                fill_color = QColor(200, 100, 10)  # Orange pour la source
            else:
                fill_color = QColor(139, 0, 0)  # Rouge foncé pour les autres
            painter.setBrush(QBrush(fill_color))
            painter.setPen(QPen(QColor(255, 255, 255), border_width))
            painter.drawEllipse(pos, radius + border_width, radius + border_width)
            painter.setBrush(QBrush(fill_color))
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

        painter.setFont(self.__best_path_font)
        painter.setPen(QPen(QColor(230, 230, 230)))
        margin = 10
        painter.drawText(margin, margin + 20, self.best_path_text)

        # Maintenant, dessiner tous les textes sur les routes, par-dessus tout
        painter.setFont(self.__road_font)
        painter.setPen(QPen(QColor(255, 255, 255)))
        for text_pos, angle, text in texts_to_draw:
            painter.save()
            painter.translate(text_pos)
            painter.rotate(angle)
            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            painter.drawText(int(-text_width / 2), int(text_height / 2), text)
            painter.restore()

        painter.end()

    def setAntSpeed(self, speed):
        self.ant_speed = speed

    def setShowRoadText(self, flag):
        self.show_road_text = flag
        self.update()

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
            self.__civ.step()
            # print(f"step:{self.__civ.steps}")
            best_path = self.__civ.get_best_path()  # Renvoie une liste de City
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

        self.update()  # Redessine la fenêtre

    def compose_colont_ants(self):
        if not self.first_composition_done:
            self.__civ.reset_ants()
            self.first_composition_done = True  # Marquer comme exécuté
        try:
            colony_size = int(self.size_input.text())
            print(colony_size)
            alpha = float(self.alpha_input.text())
            gamma = float(self.gamma_input.text())
            beta = float(self.beta_input.text())
            self.__civ.create_ant_colony(colony_size, alpha, gamma, beta)
        except ValueError:
            self.result_label.setText("Veuillez entrer des valeurs valides")

    def start_animation_after_composition(self):
        self.ants = self.__civ.get_ants()
        colony_size = len(self.ants)
        new_initial_pheromone = colony_size / 1000
        # Réinitialiser les pheromones
        self.__civ.set_initial_pheromone(new_initial_pheromone)
        for road in self.__civ.get_roads():
            road.reset_pheromone(self.__civ.get_initial_pheromone())
        # Réinitialiser le compteur d'étapes de la civilisation
        self.__civ.steps = 0

        # Mise à jour des structures d'animation
        self.ant_progress = {ant: 0.0 for ant in self.ants}

        # Réinitialiser les variables de temps
        self.start_time = time.time()
        self.last_update = time.time()

        # Recalculer les temps de lancement
        self.ant_launch_delta = self.ant_speed * 0.04
        self.ant_launch_time = {
            ant: self.start_time + i * self.ant_launch_delta
            for i, ant in enumerate(self.ants)
        }

        # Forcer le recalcul du meilleur chemin
        self.__civ.step()
        self.best_path_text = "Best Path: N/A"

        # Forcer la mise à jour de l'interface
        self.cached_layout = None  # Recalcul du layout si nécessaire

        self.first_composition_done = False
        for ant in self.ants:
            print(ant)
        print(self.ant_launch_time)
        self.update()


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

            # Dessin de la flèche indiquant le sens de la route
            road_pen = QPen(Qt.white, 2, Qt.SolidLine)
            painter.setPen(road_pen)
            middle = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)
            dx = end.x() - start.x()
            dy = end.y() - start.y()
            angle = math.atan2(dy, dx)
            arrow_size = 30
            arrow_angle = math.radians(30)
            arrow_p1 = QPointF(
                middle.x() - arrow_size * math.cos(angle - arrow_angle),
                middle.y() - arrow_size * math.sin(angle - arrow_angle),
            )
            arrow_p2 = QPointF(
                middle.x() - arrow_size * math.cos(angle + arrow_angle),
                middle.y() - arrow_size * math.sin(angle + arrow_angle),
            )
            arrow_head = QPolygonF([middle, arrow_p1, arrow_p2])
            painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
            painter.setPen(QPen(road_color, 4))
            painter.drawPolygon(arrow_head)

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
            elif city == self.civ.get_food_source():
                fill_color = QColor(200, 100, 10)
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
