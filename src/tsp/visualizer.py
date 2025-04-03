import math
import time

from PyQt5.QtCore import QPointF, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QOpenGLWidget,
    QPushButton,
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from pcc.city import City


class Visualizer(QWidget):
    def __init__(self, civ, edition_mode: bool):
        """
        civ: une instance de la classe Civilization.
        """
        super().__init__()

        self.selected_color = None
        self.setWindowTitle("Ant Colony Simulation - PCC")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon("assets/logo.webp"))

        self.main_layout = QVBoxLayout(self)

        # Créer le canvas selon le choix de mode
        if edition_mode:
            self.canvas = SimulationCanvas(civ, parent=self)
        else:
            self.canvas = Canvas(civ, parent=self)
        self.canvas.setGeometry(0, 0, self.width(), self.height())
        self.canvas.show()

        self.show_text = QGroupBox(self)
        self.show_text.setGeometry(1560, 300, 240, 85)
        self.show_text.setStyleSheet(
            """
            QGroupBox {
                background-color: #282828;
                border-radius: 20px;
                padding: 15px;
                font-family: Roboto;
                border: 5px solid rgba(255, 255, 255, 0.2);
                font-size: 26px;
            }
            """
        )
        show_text_layout = QVBoxLayout(self.show_text)

        # Interrupteur pour afficher/masquer le texte sous les routes
        self.road_text_checkbox = QCheckBox("Cacher texte", self)
        self.road_text_checkbox.setFont(QFont("Roboto", 8, 5))
        self.road_text_checkbox.setChecked(True)
        self.road_text_checkbox.stateChanged.connect(self.toggleRoadText)
        self.road_text_checkbox.setStyleSheet("color: white;font-weight: bold; ")

        self.road_text_checkbox.setStyleSheet(
            """
            QCheckBox {
                color: white;  /* Couleur du texte */
                font-weight: bold;
            }
            QCheckBox::indicator {
                background-color: white;  /* Fond de la case quand elle est décochée */
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;  /* Fond de la case quand elle est cochée */
            }
        """
        )

        self.road_text_checkbox.raise_()
        show_text_layout.addWidget(self.road_text_checkbox)

        # Création du groupe pour l'algorithme génétique
        self.genetic_group = QGroupBox("Algorithme Génétique", self)
        self.genetic_group.setGeometry(100, 600, 300, 450)
        self.genetic_group.setStyleSheet(
            """
            QGroupBox {
                background-color: #282828;
                border-radius: 20px;
                padding: 15px;
                font-family: Roboto;
                color: white;
                border: 5px solid rgba(255, 255, 255, 0.2);
                font-size: 26px;
                margin-top: 25px;
            }
            QGroupBox::title {
                font-size: 26px;
                font-weight: bold;
                color: white;
                padding: 5px;
                subcontrol-origin: margin;
                subcontrol-position: top center;
                top: 5px;
            }
            """
        )

        # Layout principal
        genetic_layout = QVBoxLayout(self.genetic_group)
        genetic_layout.addSpacing(5)

        # Bouton pour lancer l'algorithme
        self.genetic_button = QPushButton("▶ Lancer l'Algorithme")
        self.genetic_button.setMinimumHeight(45)
        self.genetic_button.clicked.connect(self.canvas.launch_genetic_algorithm)
        self.genetic_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            """
        )
        genetic_layout.addWidget(self.genetic_button)
        genetic_layout.addSpacing(5)

        # Zone de défilement pour les résultats
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)

        self.results_scroll.setStyleSheet(
            """
            QScrollArea {
                background-color: white;
                border-radius: 20px;
            }
            QScrollBar:vertical {
                width: 10px;
                background: #333333;
            }
            QScrollBar::handle:vertical {
                background: #666666;
                border-radius: 20px;
            }
            """
        )
        self.results_scroll.setMaximumHeight(200)

        # Conteneur pour le QLabel
        self.results_container = QWidget()
        self.results_container.setStyleSheet(
            """
            background-color: rgb(255,255,255,0.2); 
            padding: 10px; /* Ajoute un espace pour bien voir la différence */
            border-radius: 10px;
            """
        )
        # Layout pour contenir le QLabel
        self.results_layout = QVBoxLayout(self.results_container)

        # Label pour afficher les résultats
        self.results_area = QLabel("Les résultats apparaîtront ici...")
        self.results_area.setStyleSheet(
            """
            background-color: rgb(255,255,255,0.2);  /* Intérieur = même couleur que la bordure */
            color: #282828;
            padding: 10px;
            font-size: 20px;
            border-radius: 10px;
            """
        )
        self.results_area.setWordWrap(True)
        self.results_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Ajouter QLabel au conteneur
        self.results_layout.addWidget(self.results_area)

        # Assigner le conteneur à la QScrollArea
        self.results_scroll.setWidget(self.results_container)

        # Ajouter la zone de défilement au layout principal
        genetic_layout.addWidget(self.results_scroll)

        genetic_layout.addSpacing(5)

        # Compteur d'itérations
        self.iteration_counter = QLabel("Itérations: --")
        self.iteration_counter.setStyleSheet(
            "color: white; font-size: 20px;font-weight: bold;"
        )
        genetic_layout.addWidget(self.iteration_counter)

        # Remettre le groupe au premier plan
        self.genetic_group.raise_()

    def resizeEvent(self, event):
        self.canvas.setGeometry(0, 0, self.width(), self.height())
        self.genetic_group.setGeometry(60, 540, 395, 420)
        super().resizeEvent(event)

    def toggleRoadText(self, state):
        show_text = state == Qt.Checked
        self.canvas.setShowRoadText(show_text)


# Canvas de base
class BaseCanvas(QOpenGLWidget):
    def __init__(self, civ, edition_mode: bool, parent=None):
        super().__init__(parent)
        self.civ = civ
        self.cached_layout = None
        self.is_edition_mode = edition_mode
        self.ants = self.civ.get_ants()
        self.ant_progress = {ant: 0.0 for ant in self.ants}
        self.ant_speed = 1.0
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
        self.best_path_text = "Chemin Optimal: N/A"
        self.show_road_text = True

        self.init_input_widgets()

    def init_input_widgets(self):
        """Initialise les éléments d'interface pour configurer les paramètres des fourmis."""
        self.input_group = QGroupBox("Personnaliser la colonie", self)
        self.input_group.setStyleSheet(
            """
            QGroupBox {
                background-color: #282828;
                border-radius: 15px;
                padding: 15px;
                font-family: Roboto;
                color: white;
                border: 5px solid rgba(255, 255, 255, 0.2);
                font-size: 26px;
                margin-top: 25px;
            }
            QGroupBox::title {
                font-size: 26px;
                font-weight: bold;
                subcontrol-origin: margin;
                subcontrol-position: top center;
                color: white;
                font-family: 'Roboto';
                top : 10px;
            }
        """
        )
        # Layout principal
        main_layout = QVBoxLayout(self.input_group)

        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(50)

        self.size_input = QLineEdit()
        self.alpha_input = QLineEdit()
        self.beta_input = QLineEdit()

        # Uniformiser la taille des champs
        for line_edit in (self.size_input, self.alpha_input, self.beta_input):
            line_edit.setFixedWidth(100)
            line_edit.setStyleSheet("padding: 5px; border-radius: 5px;")

        main_layout.addSpacing(30)

        # Créer les labels
        label_nombre = QLabel("Nombre de fourmis:")
        label_nombre.setMinimumWidth(180)
        label_alpha = QLabel("Alpha:")
        label_alpha.setMinimumWidth(150)
        label_beta = QLabel("Beta:")
        label_beta.setMinimumWidth(150)

        # Ajouter les labels et champs au grid layout
        grid_layout.addWidget(label_nombre, 0, 0, Qt.AlignLeft)
        grid_layout.addWidget(self.size_input, 0, 1)

        grid_layout.addWidget(label_alpha, 1, 0, Qt.AlignLeft)
        grid_layout.addWidget(self.alpha_input, 1, 1)

        grid_layout.addWidget(label_beta, 2, 0, Qt.AlignLeft)
        grid_layout.addWidget(self.beta_input, 2, 1)

        # Ajouter le grid layout au layout principal
        main_layout.addLayout(grid_layout)

        main_layout.addSpacing(30)
        # Sélection de couleur
        color_layout = QHBoxLayout()
        self.color_button = QPushButton("Choisir une couleur")
        self.color_button.setFixedSize(160, 35)
        self.color_button.clicked.connect(self.choose_color)
        self.color_display = QLabel()
        self.color_display.setFixedSize(40, 40)
        self.color_display.setStyleSheet(
            "background-color: white; border: 1px solid black; border-radius: 20px;"
        )
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_display)
        main_layout.addLayout(color_layout)
        main_layout.addSpacing(30)

        # Slider pour la vitesse des fourmis
        speed_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_label = QLabel(
            f"Vitesse fourmis: {1 if not self.is_edition_mode else 0}", self
        )
        self.speed_slider.setValue(1 if not self.is_edition_mode else 0)
        self.speed_slider.setMinimum(0)
        self.speed_slider.setMaximum(30)
        self.speed_slider.setTickInterval(2)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.valueChanged.connect(self.updateAntSpeed)
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_slider)
        main_layout.addLayout(speed_layout)

        main_layout.addSpacing(50)

        # Boutons "Ajouter" et "Valider"
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter")
        self.add_button.setFixedSize(120, 35)
        self.add_button.clicked.connect(self.compose_colony_ants)
        self.validate_button = QPushButton("Valider")
        self.validate_button.setFixedSize(120, 35)
        self.validate_button.clicked.connect(self.start_animation_after_composition)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.validate_button)
        main_layout.addLayout(button_layout)

        self.input_group.adjustSize()  # Ajuste la taille au contenu

        x_position = 60
        y_position = 43
        self.input_group.move(x_position, y_position)

        # Le widget est directement ajouté à la fenêtre principale
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
                background-color:  #4CAF50;
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
        self.selected_color = color

    def display_best_path_window(self):
        """Affiche ou met à jour la fenêtre du meilleur chemin sans ralentir l'animation."""
        # Désactiver les mises à jour pour éviter les lags
        self.setUpdatesEnabled(False)

        # Extraire les identifiants des villes
        city_ids = self.best_path_text.replace("Chemin Optimal: ", "").split("→")

        # Vérifier si le widget existe déjà
        if hasattr(self, "path_display"):
            # Nettoyer l'ancien contenu pour éviter de recréer des widgets
            for i in reversed(range(self.path_display_layout.count())):
                self.path_display_layout.itemAt(i).widget().deleteLater()
        else:
            # Créer un QGroupBox seulement si ce n'est pas déjà fait
            self.path_display = QGroupBox("Chemin Optimal", self)
            self.path_display.setStyleSheet(
                """
                QGroupBox {
                    background-color: #282828;
                    border-radius: 15px;
                    padding: 15px;
                    font-family: Roboto;
                    color: white;
                    border: 5px solid rgba(255, 255, 255, 0.2);
                    font-size: 26px;
                    margin-top: 25px;
                }
                QGroupBox::title {
                    font-size: 26px;
                    font-weight: bold;
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    color: white;
                    font-family: 'Roboto';
                    top: 10px;  /* Move the title down a bit */
                }
                """
            )
            self.path_display_layout = QVBoxLayout(self.path_display)

        # Création d'un widget contenant le chemin
        path_widget = QWidget()
        path_widget.setStyleSheet(
            "background-color: #333333; border-radius: 10px; padding: 15px;"
        )

        path_flow = QHBoxLayout(path_widget)
        path_flow.setSpacing(15)
        path_flow.setAlignment(Qt.AlignCenter)
        path_flow.setContentsMargins(10, 10, 10, 10)

        # Ajouter chaque ville avec une flèche entre elles
        for i, city_id in enumerate(city_ids):
            city_label = QLabel(city_id)
            city_label.setFixedSize(60, 60)
            city_label.setStyleSheet(
                """
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 20px;
                font-size: 16px;
                qproperty-alignment: AlignCenter;
                """
            )
            path_flow.addWidget(city_label)

            if i < len(city_ids) - 1:
                arrow = QLabel("→")
                arrow.setStyleSheet("color: white; font-size: 24px;")
                path_flow.addWidget(arrow)

        # Ajouter le widget du chemin à la layout principale
        self.path_display_layout.addWidget(path_widget)

        # Positionner et afficher
        self.path_display.setFixedWidth(1260)
        self.path_display.move(540, 40)
        self.path_display.show()

        # Réactiver les mises à jour
        self.setUpdatesEnabled(True)

    def updateAntSpeed(self, value):
        """Met à jour le label et la vitesse des fourmis."""
        self.speed_label.setText(f"Vitesse fourmis: {value}")
        self.setAntSpeed(value)

    def compose_colony_ants(self):
        if not self.first_composition_done:
            self.civ.reset_ants()
            self.first_composition_done = True
        try:
            colony_size = int(self.size_input.text())
            alpha = float(self.alpha_input.text())
            beta = float(self.beta_input.text())
            self.civ.create_ant_colony(colony_size, alpha, beta)
            for ant in self.civ.get_ants():
                if ant.get_personalised_color() == None:
                    ant.set_color(self.selected_color)
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
        self.best_path_text = "Chemin Optimal: N/A"
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
                self.best_path_text = "Chemin Optimal: " + "→".join(
                    str(city.get_id()) for city in best_path
                )
            else:
                self.best_path_text = "Chemin Optimal: N/A"
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

        offset_x = 180
        offset_y = 130
        painter.translate(offset_x, offset_y)

        # Calcul du layout
        if self.cached_layout is None:
            self.cached_layout = self.get_layout()

        # Obtention des positions des villes
        node_positions = self.get_node_positions(self.cached_layout)
        for city in node_positions.keys():
            pos = node_positions[city]
            node_positions[city] = QPointF(pos.x() - offset_x, pos.y() - offset_y)

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
                weight_text = str(round(road.get_weight(), 2))
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

        # # Affichage du meilleur chemin
        self.display_best_path_window()

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
            node_positions[city] = QPointF(pos[0], pos[1])
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

    def launch_genetic_algorithm(self):
        """Lance l'algorithme génétique de la civilisation et affiche les résultats."""
        try:
            # Récupérer les éléments d'interface depuis le parent
            parent = self.parent()
            if hasattr(parent, "iteration_counter"):
                iteration_label = parent.iteration_counter
            else:
                iteration_label = None

            if hasattr(parent, "results_area"):
                results_area = parent.results_area
            else:
                results_area = None

            if hasattr(parent, "genetic_button"):
                genetic_button = parent.genetic_button
                genetic_button.setEnabled(False)
                genetic_button.setText("Exécution en cours...")
            else:
                genetic_button = None

            # Stopper l'animation des fourmis pendant l'exécution de l'algorithme génétique
            self.timer.stop()

            # Modifier la méthode genetic_algo_application pour mettre à jour le compteur
            original_genetic_algo = self.civ.genetic_algo_application

            def modified_genetic_algo(nb_iteration=100):
                # Stocker les valeurs de threshold_genetic_algo initiales
                threshold_initial = self.civ._Civilization__threshold_genetic_algo

                # Exécuter nb_iteration fois step()
                for _ in range(nb_iteration):
                    self.civ.step()

                # Boucle principale de l'algorithme génétique
                threshold_genetic_algo = threshold_initial
                while threshold_genetic_algo > 0:
                    # Mettre à jour le label d'itération
                    if iteration_label:
                        iteration_label.setText(
                            f"Itérations restantes: {threshold_genetic_algo}"
                        )
                        iteration_label.repaint()

                    # Exécuter l'algorithme génétique
                    self.civ.genetic_algo()

                    # Mettre à jour le dictionnaire ant_progress avec les nouvelles fourmis
                    current_ants = self.civ.get_ants()
                    self.ants = current_ants
                    # Mettre à jour le ant_progress en ajoutant les fourmis manquantes
                    for ant in current_ants:
                        if ant not in self.ant_progress:
                            self.ant_progress[ant] = 0.0

                    # Réinitialiser les fourmis
                    for ant in self.civ.get_ants():
                        ant.reset_ant()

                    # Reset les phéromones
                    for road in self.civ.get_roads():
                        road.reset_pheromone(self.civ.get_initial_pheromone())

                    # Exécuter nb_iteration fois step()
                    for _ in range(nb_iteration):
                        self.civ.step()

                    threshold_genetic_algo -= 1

                # Afficher les résultats
                self.display_results(results_area)

                # Réactiver le bouton
                if genetic_button:
                    genetic_button.setEnabled(True)
                    genetic_button.setText("Lancer Algo. Génétique")

                # Redémarrer l'animation
                self.timer.start()

            # Remplacer temporairement la méthode
            self.civ.genetic_algo_application = modified_genetic_algo

            # Lancer l'algorithme
            self.civ.genetic_algo_application((100))

            # Restaurer la méthode originale
            self.civ.genetic_algo_application = original_genetic_algo

        except Exception as e:
            print(f"Erreur lors de l'exécution de l'algorithme génétique: {e}")
            import traceback

            traceback.print_exc()
            # S'assurer que le timer est redémarré en cas d'erreur
            self.timer.start()
            if hasattr(self.parent(), "genetic_button"):
                self.parent().genetic_button.setEnabled(True)
                self.parent().genetic_button.setText("Lancer Algo. Génétique")

    def display_results(self, results_area=None):
        """Affiche les résultats de l'algorithme génétique."""
        try:
            # Obtenir le meilleur travailleur et le meilleur explorateur
            best_worker = self.civ.best_worker()
            best_explorer = self.civ.best_explorer()

            # Extraire les paramètres (alpha, beta)
            worker_ant = best_worker[0]
            explorer_ant = best_explorer[0]

            worker_params = worker_ant.get_parameters()
            explorer_params = explorer_ant.get_parameters()

            # Mettre à jour le texte du chemin optimal
            best_path = self.civ.get_best_path()
            if best_path:
                path_text = "→".join(str(city.get_id()) for city in best_path)
                self.best_path_text = "Chemin Optimal: " + path_text

            # Préparer le texte des résultats
            results_text = (
                f"<b>Configuration optimale trouvée:</b><br><br>"
                f"<b>Meilleure travailleuse</b> (ID: {worker_ant.get_id()}):<br>"
                f"• Alpha: <b>{worker_params[0]:.2f}</b><br>"
                f"• Beta: <b>{worker_params[1]:.2f}</b><br>"
                f"• Nourriture collectée: <b>{best_worker[1]}</b><br><br>"
                f"<b>Meilleure exploratrice</b> (ID: {explorer_ant.get_id()}):<br>"
                f"• Alpha: <b>{explorer_params[0]:.2f}</b><br>"
                f"• Beta: <b>{explorer_params[1]:.2f}</b><br>"
                f"• Chemins explorés: <b>{best_explorer[2]}</b><br><br>"
                f"<b>Chemin Optimal:</b><br>{path_text}"
            )

            # Afficher les résultats
            if results_area:
                results_area.setText(results_text)
                # Remonter au début du texte
                if hasattr(self.parent(), "results_scroll"):
                    self.parent().results_scroll.verticalScrollBar().setValue(0)

            parent = self.parent()
            if hasattr(parent, "iteration_counter"):
                parent.iteration_counter.setText("Algorithme terminé!")
                parent.iteration_counter.setAlignment(Qt.AlignCenter)

            # Réinitialiser l'animation
            self.start_time = time.time()
            self.last_update = time.time()

            # S'assurer que toutes les fourmis sont dans le dictionnaire ant_progress
            current_ants = self.civ.get_ants()
            self.ants = current_ants
            self.ant_progress = {ant: 0.0 for ant in current_ants}

            # Recalculer les temps de lancement
            self.ant_launch_delta = self.ant_speed * 0.04
            self.ant_launch_time = {
                ant: self.start_time + i * self.ant_launch_delta
                for i, ant in enumerate(self.ants)
            }

            # Forcer la mise à jour de l'affichage
            self.update()

        except Exception as e:
            print(f"Erreur lors de l'affichage des résultats: {e}")
            import traceback

            traceback.print_exc()


# Canvas classique statique
class Canvas(BaseCanvas):
    def __init__(self, civ, parent=None):
        super().__init__(civ, False, parent)

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


# SimulationCanvas avec placement de villes dynamique
class SimulationCanvas(BaseCanvas):
    def __init__(self, civ, parent=None):
        super().__init__(civ, True, parent)
        # Attributs spécifiques à la gestion par clic
        self.current_road_start = None
        self.has_started = False
        self.ant_speed = 0.0

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
                    # Stocker la ville de départ
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
