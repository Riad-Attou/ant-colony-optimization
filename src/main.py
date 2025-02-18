import sys

from PyQt5.QtWidgets import QApplication

from visualizer import Visualizer


def main():
    app = QApplication(sys.argv)
    window = Visualizer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
