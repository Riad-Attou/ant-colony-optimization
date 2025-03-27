import random
import sys

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QApplication

from pcc.city import City
from pcc.civilization import Civilization
from pcc.visualizer import Visualizer

fmt = QSurfaceFormat()
fmt.setSamples(8)
QSurfaceFormat.setDefaultFormat(fmt)


def get_small_civ_pcc():
    nb_cities = 4

    cities = [City(i) for i in range(4)]

    civ = Civilization(cities[0], cities[-1], 0.05, 0.1, 0.1, 30)

    for i in range(1, nb_cities - 1):
        civ.add_city(cities[i])

    civ.add_road(1.0, cities[0], cities[1])
    civ.add_road(2.0, cities[1], cities[2])
    civ.add_road(3.0, cities[1], cities[3])
    civ.add_road(4.0, cities[2], cities[3])
    for i in range(50):
        civ.create_ant_colony(1, random.uniform(0, 5), random.uniform(0, 5))
    return civ


def get_big_civ_pcc():
    nb_cities = 10

    cities = [City(i) for i in range(nb_cities)]

    civ = Civilization(cities[0], cities[-1], 0.05, 0.1, 0.1, 50)

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

    for i in range(50):
        civ.create_ant_colony(1, random.uniform(0, 5), random.uniform(0, 5))
    return civ


def get_really_big_civ_pcc():
    nb_cities = 20
    cities = [City(i) for i in range(nb_cities)]

    # Le nid est la première ville et la source de nourriture la dernière.
    civ = Civilization(cities[0], cities[-1], 0.05, 0.1, 0.1, 200)

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

    for i in range(80):
        civ.create_ant_colony(1, random.uniform(0, 5), random.uniform(0, 5))
    return civ


def get_empty_civ_pcc():
    nest = City(0, QPointF(500, 400))
    food_source = City(99, QPointF(1500, 400))
    civ = Civilization(nest, food_source, 0.05, 0.1, 0.1, 50)
    return civ


def main_pcc(civ: Civilization, edition_mode):
    app = QApplication(sys.argv)
    window = Visualizer(civ, edition_mode)
    window.showMaximized()

    sys.exit(app.exec_())


# if __name__ == "__main__":

#     # small_civ = get_small_civ_pcc()
#     # small_civ.step()
#     # main(small_civ, False)

#     # big_civ = get_big_civ_pcc()
#     # big_civ.step()
#     # main(big_civ, False)

#     # really_big_civ = get_really_big_civ_pcc()
#     # really_big_civ.step()
#     # main(really_big_civ, False)

#     # nest = City(0, QPointF(500, 400))
#     # food_source = City(1, QPointF(1800, 400))
#     # civ = Civilization(nest, food_source, 0.05, 1, 0.2, 0.2, 0.2)
#     # civ.add_road(1300 / 1500, nest, food_source)
#     # civ.create_ant_colony(10, 0.5, 0.5, 0.5)
#     # main(civ, True)

#     big_civ = get_big_civ_pcc()
#     big_civ.genetic_algo_application()
#     main(big_civ, True)
