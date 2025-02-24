import sys

from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QApplication

from city import City
from civilization import Civilization
from visualizer import Visualizer

fmt = QSurfaceFormat()
fmt.setSamples(8)
QSurfaceFormat.setDefaultFormat(fmt)


def get_small_civ():
    nb_cities = 4

    cities = [City(i) for i in range(4)]

    civ = Civilization(cities[0], cities[-1])

    for i in range(1, nb_cities - 1):
        civ.add_city(cities[i])

    civ.add_road(5.0, cities[0], cities[1])
    civ.add_road(5.0, cities[1], cities[2])
    civ.add_road(5.0, cities[1], cities[3])
    civ.add_road(5.0, cities[2], cities[3])

    civ.create_ant_colony(20)

    return civ


def get_big_civ():
    nb_cities = 10

    cities = [City(i) for i in range(nb_cities)]

    civ = Civilization(cities[0], cities[-1])

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

    civ.create_ant_colony(100)

    return civ


def get_really_big_civ():
    nb_cities = 20
    cities = [City(i) for i in range(nb_cities)]

    # Le nid est la première ville et la source de nourriture la dernière.
    civ = Civilization(cities[0], cities[-1])

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

    civ.create_ant_colony(100)
    return civ


def main(civ: Civilization):
    app = QApplication(sys.argv)
    window = Visualizer(civ)
    window.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":

    # small_civ = get_small_civ()
    # small_civ.step()
    # main(small_civ)

    # big_civ = get_big_civ()
    # big_civ.step()
    # main(big_civ)

    really_big_civ = get_really_big_civ()
    really_big_civ.step()
    main(really_big_civ)
