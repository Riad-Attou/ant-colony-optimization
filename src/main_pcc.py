from pcc.utils import *


def main(civ, edition_mode):
    app = QApplication(sys.argv)
    window = Visualizer(civ, edition_mode)
    window.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":
    ###########################
    # PCC AVEC UNE VILLE FIXE #
    ###########################
    # civ = get_small_civ_pcc()
    # civ = get_really_big_civ_pcc()
    civ = get_big_civ_pcc()
    main(civ, edition_mode=False)

    ####################################
    # PCC AVEC UNE VILLE PERSONNALISÉE #
    ####################################
    # civ = get_empty_civ_pcc()
    # civ.create_ant_colony(5, 0.5, 0.5)
    # main(civ, edition_mode=True)
