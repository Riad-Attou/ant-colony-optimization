import sys

from PyQt5.QtWidgets import QApplication

from city import City
from civilization import Civilization
from visualizer import Visualizer


def main(civ: Civilization):
    app = QApplication(sys.argv)
    window = Visualizer(civ)
    window.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":
    # nb_cities = 4

    # cities = [City(i) for i in range(4)]

    # civ = Civilization(cities[0], cities[-1])

    # for i in range(1, nb_cities - 1):
    #     civ.add_city(cities[i])

    # civ.add_road(5.0, cities[0], cities[1])
    # civ.add_road(5.0, cities[1], cities[2])
    # civ.add_road(5.0, cities[1], cities[3])
    # civ.add_road(5.0, cities[2], cities[3])

    # civ.create_ant_colony(20)

    # civ.step()
    # Nombre de villes
    nb_cities = 10

    # Création de 10 villes (identifiées de 0 à 9)
    cities = [City(i) for i in range(nb_cities)]

    # Définir le nid comme la première ville et la source de nourriture comme la dernière
    civ = Civilization(cities[0], cities[-1])

    # Ajouter les villes intermédiaires à la civilisation
    for i in range(1, nb_cities - 1):
        civ.add_city(cities[i])

    # Création d'un réseau de routes plus complexe
    # Routes principales
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

    # Routes supplémentaires pour complexifier le graphe (routes transversales)
    civ.add_road(7.0, cities[0], cities[5])
    civ.add_road(8.0, cities[2], cities[7])
    civ.add_road(6.0, cities[3], cities[8])
    civ.add_road(5.0, cities[4], cities[9])
    civ.add_road(4.0, cities[1], cities[6])
    civ.add_road(5.0, cities[2], cities[8])

    # Créer la colonie de fourmis (ici 20 fourmis)
    civ.create_ant_colony(20)

    # On effectue un premier step pour initialiser l'état (optionnel)
    civ.step()

    # Lancer l'application en passant la civilisation à la fonction main (ou à Visualizer)
    main(civ)

    main(civ)
