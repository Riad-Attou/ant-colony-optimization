import sys

from PyQt5.QtWidgets import QApplication

from ant import Ant
from city import City
from civilization import Civilization
from visualizer import Visualizer


def main():
    app = QApplication(sys.argv)
    window = Visualizer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # main()
    city1 = City(1)
    city2 = City(2)

    civ = Civilization(city1, city2)

    civ.add_road(5.0, city1, city2)

    ant = Ant(1, 0.5, 1, 1)

    print(ant)
    print(civ)
