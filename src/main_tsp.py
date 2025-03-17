from tsp.utils import *


def main(civ, edition_mode):
    app = QApplication(sys.argv)
    window = Visualizer(civ, edition_mode)
    window.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":
    ###########################
    # TSP AVEC UNE VILLE FIXE #
    ###########################
    # civ = create_full_city_tsp(5)
    civ = create_small_full_city_tsp()
    main(civ, edition_mode=False)

    ####################################
    # TSP AVEC UNE VILLE PERSONNALISÉE #
    ####################################
    # civ = get_empty_civ_tsp()
    # civ.create_ant_colony(5, 0.5, 0.5, 0.5)
    # main(civ, edition_mode=True)
