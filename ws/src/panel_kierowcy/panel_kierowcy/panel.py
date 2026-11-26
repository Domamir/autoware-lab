import signal
import sys
import threading
import time
 
from autoware_adapi_v1_msgs.msg import OperationModeState, RouteState
from panel_kierowcy.stan import (
    NAZWY_STANOW_TRASY, NAZWY_TRYBOW, StanNode, nazwa, tekst)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QVBoxLayout, QWidget
import rclpy
from rclpy.executors import SingleThreadedExecutor
 
# Style etykiet. setStyleSheet() zastępuje cały styl, więc czcionka jest w każdym z nich.
STYL_PREDKOSCI = 'font-size: 72px; font-weight: bold; color: {kolor}'
STYL_TRYBU = ('font-size: 24px; font-weight: bold; padding: 6px; '
              'background: {kolor}; color: white')
STYL_ALARMU = ('font-size: 26px; font-weight: bold; padding: 8px; '
               'background: #c62828; color: white')
 
KOLORY_TRYBOW = {
    OperationModeState.AUTONOMOUS: '#2e7d32',   # zielony
    OperationModeState.STOP: '#c62828',         # czerwony
    OperationModeState.LOCAL: '#ef6c00',        # pomarańczowy
    OperationModeState.REMOTE: '#ef6c00',
}
KOLOR_NIEZNANY = '#757575'                      # szary
KOLOR_NORMALNY = 'black'
KOLOR_ZA_SZYBKO = '#d50000'
 
TOLERANCJA_KMH = 2.0     # czerwony licznik dopiero powyżej limit + 2 km/h
CZAS_ALARMU_S = 5.0      # jak długo widać "Przejmij sterowanie"
 
 
class Panel(QWidget):
 
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.setWindowTitle('Panel kierowcy')
        self.setStyleSheet('font-size: 20px')
        self.setMinimumWidth(320)
 
        # Duży licznik prędkości z jednostką pod spodem.
        self.predkosc = QLabel()
        self.predkosc.setAlignment(Qt.AlignCenter)
        self.predkosc.setStyleSheet(STYL_PREDKOSCI.format(kolor=KOLOR_NORMALNY))
        jednostka = QLabel('km/h')
        jednostka.setAlignment(Qt.AlignCenter)
 
        # Tryb pracy.
        self.tryb = QLabel()
        self.tryb.setAlignment(Qt.AlignCenter)
        self.tryb.setStyleSheet(STYL_TRYBU.format(kolor=KOLOR_NIEZNANY))
 
        # Komunikat "Przejmij sterowanie": domyślnie ukryty.
        self.alarm = QLabel('Przejmij sterowanie')
        self.alarm.setAlignment(Qt.AlignCenter)
        self.alarm.setStyleSheet(STYL_ALARMU)
        self.alarm.hide()
        self.poprzedni_tryb = None   # tryb z poprzedniego odświeżenia
        self.alarm_do = 0.0          # do kiedy (time.monotonic()) pokazywać alarm
 
        # Trzy wiersze: nazwa w kolumnie 0, wartość w kolumnie 1.
        self.limit = QLabel()
        self.trasa = QLabel()
        self.do_celu = QLabel()
        siatka = QGridLayout()
        for wiersz, (opis, wartosc) in enumerate((
                ('Limit', self.limit),
                ('Trasa', self.trasa),
                ('Do celu', self.do_celu))):
            wartosc.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            siatka.addWidget(QLabel(opis), wiersz, 0)
            siatka.addWidget(wartosc, wiersz, 1)
 
        uklad = QVBoxLayout(self)
        uklad.addWidget(self.predkosc)
        uklad.addWidget(jednostka)
        uklad.addWidget(self.tryb)
        uklad.addWidget(self.alarm)
        uklad.addLayout(siatka)
 
        # Co 100 ms przepisz stan z węzła do etykiet.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.odswiez)
        self.timer.start(100)
 
    def odswiez(self):
        s = self.node.stan
        if s.predkosc_kmh is None:
            self.predkosc.setText('—')
        else:
            # round(abs()) -> int: bez miejsc po przecinku i bez "-0"
            self.predkosc.setText(str(round(abs(s.predkosc_kmh))))
        self.tryb.setText(nazwa(s.tryb, NAZWY_TRYBOW))
        self.limit.setText(f'{tekst(s.limit_kmh, "{:.0f}")} km/h')
        self.trasa.setText(nazwa(s.stan_trasy, NAZWY_STANOW_TRASY))
        self.do_celu.setText(f'{tekst(s.do_celu_m, "{:.0f}")} m')
 
        # 1. Kolor trybu.
        kolor = KOLORY_TRYBOW.get(s.tryb, KOLOR_NIEZNANY)
        self.tryb.setStyleSheet(STYL_TRYBU.format(kolor=kolor))
 
        # 2. Czerwony licznik po przekroczeniu limitu o więcej niż 2 km/h.
        za_szybko = (s.predkosc_kmh is not None and s.limit_kmh is not None
                     and s.predkosc_kmh > s.limit_kmh + TOLERANCJA_KMH)
        kolor = KOLOR_ZA_SZYBKO if za_szybko else KOLOR_NORMALNY
        self.predkosc.setStyleSheet(STYL_PREDKOSCI.format(kolor=kolor))
 
        # 3. "Przejmij sterowanie" po wyjściu z AUTONOMOUS (ale nie po dojeździe do celu).
        teraz = time.monotonic()
        dojechal = s.stan_trasy == RouteState.ARRIVED
        if (self.poprzedni_tryb == OperationModeState.AUTONOMOUS
                and s.tryb != OperationModeState.AUTONOMOUS
                and not dojechal):
            self.alarm_do = teraz + CZAS_ALARMU_S
        if dojechal:
            # Gdyby STOP przyszło o odświeżenie wcześniej niż ARRIVED, gasimy alarm.
            self.alarm_do = 0.0
        self.poprzedni_tryb = s.tryb
        self.alarm.setVisible(teraz < self.alarm_do)
 
 
def main():
    rclpy.init()
    node = StanNode('panel_kierowcy')   # inna nazwa niż węzeł z stan.py!
 
    # ROS w osobnym wątku: spin() nie wraca, więc w głównym wątku zablokowałby okno.
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    watek = threading.Thread(target=executor.spin)
    watek.start()
 
    app = QApplication(sys.argv)
    panel = Panel(node)
    panel.show()
    signal.signal(signal.SIGINT, lambda *_: app.quit())   # Ctrl+C zamyka okno
    app.exec_()
 
    # Po zamknięciu okna: najpierw zatrzymaj wątek ROS, dopiero potem sprzątaj.
    executor.shutdown()
    watek.join()
    node.destroy_node()
    rclpy.try_shutdown()
 
 
if __name__ == '__main__':
    main()
 