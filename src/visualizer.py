import math
import time

from PyQt5.QtCore import QPointF, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPen
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
    def __init__(self, civ):
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
        self.canvas = Canvas(civ, parent=self)
        self.canvas.setGeometry(0, 0, self.width(), self.height())
        self.canvas.show()

        # Curseur pour la vitesse des ants (overlay en haut à droite)
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(30)
        self.speed_slider.setValue(1)
        self.speed_slider.setTickInterval(2)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setGeometry(self.width() - 170, 20, 150, 30)
        self.speed_slider.valueChanged.connect(self.updateAntSpeed)

        self.speed_label = QLabel("Ant Speed: 1", self)
        self.speed_label.setGeometry(self.width() - 170, 55, 150, 20)
        self.speed_label.setStyleSheet("color: white;")

        # Interrupteur (CheckBox) pour afficher/masquer le texte sous les routes
        self.road_text_checkbox = QCheckBox("Show Road Text", self)
        self.road_text_checkbox.setChecked(True)
        self.road_text_checkbox.setGeometry(self.width() - 170, 80, 150, 20)
        self.road_text_checkbox.stateChanged.connect(self.toggleRoadText)
        self.road_text_checkbox.setStyleSheet("color: white;")

        # S'assurer que ces widgets overlay restent au premier plan
        self.speed_slider.raise_()
        self.speed_label.raise_()
        self.road_text_checkbox.raise_()

    def resizeEvent(self, event):
        # Repositionner le canvas et les contrôles lors d'un redimensionnement
        self.canvas.setGeometry(0, 0, self.width(), self.height())
        self.speed_slider.setGeometry(self.width() - 170, 20, 150, 30)
        self.speed_label.setGeometry(self.width() - 170, 55, 150, 20)
        self.road_text_checkbox.setGeometry(self.width() - 170, 80, 150, 20)
        super().resizeEvent(event)

    def updateAntSpeed(self, value):
        self.speed_label.setText(f"Ant Speed: {value}")
        self.canvas.setAntSpeed(value)

    def toggleRoadText(self, state):
        show_text = state == Qt.Checked
        self.canvas.setShowRoadText(show_text)


# La classe Canvas est maintenant basée sur QOpenGLWidget pour profiter de l'accélération matérielle.
class Canvas(QOpenGLWidget):
    def __init__(self, civ, parent=None):
        super().__init__(parent)
        # Polices pour le rendu
        self.__city_font = QFont("Arial", 16)
        self.__road_font = QFont("Arial", 14)
        self.__best_path_font = QFont("Arial", 20)

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
        self.input_group = QGroupBox("Paramètres des Fourmis", self)
        self.input_group.setGeometry(
            100, 100, 350, 400
        )  # Position et taille du group box
        self.input_group.setStyleSheet(
            """
            QGroupBox {
                background-color: grey;    /* Couleur de fond */
                border-radius: 10px;
                padding: 10px;
                font-family: Arial;       /* Police par défaut pour le contenu */
                font-size: 20px;          /* Taille de police du contenu */
            }
            QGroupBox::title {
                font-size: 30px;          /* Titre plus grand */
                font-weight: bold;        /* Titre en gras */
                subcontrol-origin: margin;
                subcontrol-position: top center;  /* Centre le titre */
                color: #2c3e50;           /* Couleur du titre */
                font-family: 'Arial';     /* Police (peut être différente du contenu) */
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
        form_layout.addRow(QLabel("Gamma :"), self.gamma_input)
        form_layout.addRow(QLabel("Alpha :"), self.alpha_input)
        form_layout.addRow(QLabel("Beta :"), self.beta_input)

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
                font-family: "Arial";
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
            road_pen = QPen(road_color)
            road_pen.setWidthF(thickness)
            painter.setPen(road_pen)
            painter.drawLine(start, end)

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

        ant_radius = 8
        for ant in self.ants:
            u = ant.get_current_city()
            v = ant.get_next_city()
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
        painter.setPen(QPen(QColor(53, 209, 255)))
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
            print(f"step:{self.__civ.steps}")
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
