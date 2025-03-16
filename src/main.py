from pcc.civilization import *
from pcc.utils import *
from pcc.visualizer import *
from tsp.civilization import *
from tsp.utils import *
from tsp.visualizer import *


def main(civ, edition_mode):
    app = QApplication(sys.argv)
    window = Visualizer(civ, edition_mode)
    window.showMaximized()

    sys.exit(app.exec_())


if __name__ == "__main__":
    big_civ = get_big_civ_pcc()
    main(big_civ, False)
