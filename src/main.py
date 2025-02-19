import sys

from PyQt5.QtWidgets import QApplication

from city import City
from civilization import Civilization
from visualizer import Visualizer


def main(civ: Civilization):
    app = QApplication(sys.argv)
    window = Visualizer(civ)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    city1 = City(1)
    city2 = City(2)
    city3 = City(3)
    city4 = City(4)

    civ = Civilization(city1, city4)

    civ.add_city(city2)
    civ.add_city(city3)

    civ.add_road(5.0, city1, city2)
    civ.add_road(5.0, city2, city3)
    civ.add_road(5.0, city2, city4)
    civ.add_road(5.0, city3, city4)

    civ.create_ant_colony(20)

    civ.step()

    main(civ)
