import signal
import sys
import threading

from licznik_jazdy.licznik import Licznik, NAZWY_TRYBOW, tekst
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import rclpy
from rclpy.executors import SingleThreadedExecutor


class Okno(QWidget):

    def __init__(self, node):
        super().__init__()
        self.node = node
        self.setWindowTitle('Licznik jazdy')
        self.setStyleSheet('font-size: 20px')

        self.predkosc = QLabel()
        self.predkosc.setStyleSheet('font-size: 64px; font-weight: bold')
        self.tryb = QLabel()
        self.dystans = QLabel()
        self.autonomicznie = QLabel()

        uklad = QVBoxLayout(self)
        for etykieta in (self.predkosc, self.tryb, self.dystans, self.autonomicznie):
            uklad.addWidget(etykieta)

        # Co 100 ms przepisz stan z węzła do etykiet.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.odswiez)
        self.timer.start(100)

    def odswiez(self):
        s = self.node.stan
        self.predkosc.setText(f'{tekst(s.predkosc_kmh, "{:.0f}")} km/h')
        self.tryb.setText(f'Tryb: {NAZWY_TRYBOW.get(s.tryb, "—")}')
        self.dystans.setText(f'Dystans: {s.dystans_m:.0f} m')
        self.autonomicznie.setText(f'Jazda autonomiczna: {s.czas_autonomiczny_s:.0f} s')


def main():
    rclpy.init()
    node = Licznik('licznik_jazdy_okno')   # inna nazwa niż węzeł z licznik.py!

    # ROS w osobnym wątku: spin() czeka na wiadomości i nie wraca, więc w głównym wątku
    # zablokowałby okno. Własny executor, żeby na końcu móc go zatrzymać.
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    watek = threading.Thread(target=executor.spin)
    watek.start()

    app = QApplication(sys.argv)
    okno = Okno(node)
    okno.show()
    signal.signal(signal.SIGINT, lambda *_: app.quit())   # Ctrl+C zamyka okno
    app.exec_()

    # Po zamknięciu okna: zatrzymaj wątek ROS i dopiero wtedy sprzątaj.
    executor.shutdown()
    watek.join()
    node.destroy_node()
    rclpy.try_shutdown()