import random
import sys

from city import City
from civilization import Civilization
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QApplication
from visualizer import Visualizer

fmt = QSurfaceFormat()
fmt.setSamples(8)
QSurfaceFormat.setDefaultFormat(fmt)


def get_small_civ():
    nb_cities = 4

    cities = [City(i) for i in range(4)]

    civ = Civilization(cities[0], 0.05, 0.1, 0.2, 0.2, 0.2)

    for i in range(1, nb_cities - 1):
        civ.add_city(cities[i])

    civ.add_road(1.0, cities[0], cities[1])
    civ.add_road(2.0, cities[1], cities[2])
    civ.add_road(3.0, cities[1], cities[3])
    civ.add_road(4.0, cities[2], cities[3])

    civ.create_ant_colony(1, 10, 0, 0.5)

    return civ


def get_big_civ():
    nb_cities = 10

    cities = [City(i) for i in range(nb_cities)]

    civ = Civilization(cities[0], 0.05, 0.1, 0.7, 0.2, 0.5)

    for i in range(1, nb_cities - 1):
        civ.add_city(cities[i])

    civ.add_road(5.0, cities[0], cities[1])
    civ.add_road(6.0, cities[0], cities[2])
    civ.add_road(4.0, cities[1], cities[2])
    civ.add_road(8.0, cities[1], cities[3])
    civ.add_road(3.0, cities[2], cities[4])
    civ.add_road(7.0, cities[3], cities[4])
    civ.add_road(4.0, cities[3], cities[5])
    civ.add_road(6.0, cities[4], cities[6])
    civ.add_road(5.0, cities[5], cities[6])
    civ.add_road(9.0, cities[5], cities[7])
    civ.add_road(4.0, cities[6], cities[7])
    civ.add_road(3.0, cities[7], cities[8])
    civ.add_road(6.0, cities[8], cities[9])
    civ.add_road(7.0, cities[0], cities[5])
    civ.add_road(8.0, cities[2], cities[7])
    civ.add_road(6.0, cities[3], cities[8])
    civ.add_road(5.0, cities[4], cities[9])
    civ.add_road(4.0, cities[1], cities[6])
    civ.add_road(5.0, cities[2], cities[8])

    civ.create_ant_colony(10, 5, 0, 0.5)
    civ.create_ant_colony(20, 1, 3, 0.5)
    civ.create_ant_colony(20, 0, 9, 0.5)
    civ.create_ant_colony(30, 0.1, 5, 0.5)
    civ.create_ant_colony(40, 7, 3, 0.5)
    civ.create_ant_colony(10, 2, 0.6, 0.5)
    civ.create_ant_colony(20, 0.5, 0.3, 0.5)
    civ.create_ant_colony(30, 4, 10, 0.5)
    civ.create_ant_colony(50, 1, 1, 0.5)

    return civ


def get_really_big_civ():
    nb_cities = 20
    cities = [City(i) for i in range(nb_cities)]

    # Le nid est la première ville et la source de nourriture la dernière.
    civ = Civilization(cities[0], 0.05, 0.1, 0.2, 0.2, 0.2)

    # Ajouter les villes intermédiaires
    for i in range(1, nb_cities - 1):
        civ.add_city(cities[i])

    civ.add_road(5.0, cities[0], cities[1])
    civ.add_road(6.0, cities[0], cities[2])
    civ.add_road(4.0, cities[1], cities[2])
    civ.add_road(8.0, cities[1], cities[3])
    civ.add_road(3.0, cities[2], cities[4])
    civ.add_road(7.0, cities[3], cities[4])
    civ.add_road(4.0, cities[3], cities[5])
    civ.add_road(6.0, cities[4], cities[6])
    civ.add_road(5.0, cities[5], cities[6])
    civ.add_road(9.0, cities[5], cities[7])
    civ.add_road(4.0, cities[6], cities[7])
    civ.add_road(3.0, cities[7], cities[8])
    civ.add_road(6.0, cities[8], cities[9])
    civ.add_road(7.0, cities[0], cities[5])
    civ.add_road(8.0, cities[2], cities[7])
    civ.add_road(6.0, cities[3], cities[8])
    civ.add_road(5.0, cities[4], cities[9])
    civ.add_road(5.0, cities[2], cities[8])
    civ.add_road(5.5, cities[9], cities[10])
    civ.add_road(4.5, cities[8], cities[10])
    civ.add_road(6.0, cities[10], cities[11])
    civ.add_road(3.5, cities[10], cities[12])
    civ.add_road(5.0, cities[11], cities[13])
    civ.add_road(4.0, cities[12], cities[14])
    civ.add_road(7.0, cities[13], cities[15])
    civ.add_road(4.5, cities[14], cities[15])
    civ.add_road(5.5, cities[15], cities[16])
    civ.add_road(6.0, cities[16], cities[17])
    civ.add_road(3.5, cities[16], cities[18])
    civ.add_road(4.0, cities[17], cities[19])
    civ.add_road(5.0, cities[18], cities[19])
    civ.add_road(4.0, cities[2], cities[11])
    civ.add_road(6.5, cities[4], cities[13])
    civ.add_road(5.0, cities[5], cities[12])
    civ.add_road(7.5, cities[7], cities[15])
    civ.add_road(4.5, cities[9], cities[14])
    civ.add_road(5.0, cities[8], cities[16])
    civ.add_road(6.0, cities[3], cities[10])

    civ.create_ant_colony(100, 0.5, 0.5, 0.5)
    return civ


def create_full_city(n: int) -> Civilization:
    nb_cities = n
    cities = [City(i) for i in range(nb_cities)]

    civ = Civilization(cities[0], 0.05, 0.1, 0.2, 0.2, 0.2)
    for i in range(1, n):
        civ.add_city(cities[i])

    for i in range(n):
        for j in range(i):
            civ.add_road(round(random.uniform(1, 5), 2), cities[i], cities[j])

    civ.create_ant_colony(20, 0.5, 0.5, 0.5)

    print(civ)

    return civ


def create_small_full_city() -> Civilization:
    cities = [City(i) for i in range(4)]

    civ = Civilization(cities[0], 0.05, 0.1, 0.2, 0.2, 0.2)
    for i in range(1, 4):
        civ.add_city(cities[i])

    for i in range(4):
        for j in range(i):
            civ.add_road(round(random.uniform(1, 5), 2), cities[i], cities[j])

    civ.create_ant_colony(20, 0.5, 0.5, 0.5)

    print(civ)

    return civ


def get_empty_civ():
    nest = City(0, QPointF(500, 400))
    civ = Civilization(nest, 0.05, 0.1, 0.2, 0.2, 0.2)
    return civ


def main(civ: Civilization, edition_mode):
    app = QApplication(sys.argv)
    window = Visualizer(civ, edition_mode)
    window.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":

    # small_civ = get_small_civ()
    # small_civ.step()
    # main(small_civ, False)

    # big_civ = get_big_civ()
    # big_civ.step()
    # main(big_civ, False)

    # really_big_civ = get_really_big_civ()
    # really_big_civ.step()
    # main(really_big_civ, False)

    # big_civ = get_big_civ()
    # big_civ.genetic_algo_application()
    # main(big_civ, False)

    # civ = create_small_full_city()
    # main(civ, False)

    civ = get_empty_civ()
    main(civ, True)
