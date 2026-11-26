from dataclasses import dataclass
import math
 
from autoware_adapi_v1_msgs.msg import OperationModeState, Route, RouteState
from autoware_internal_planning_msgs.msg import VelocityLimit
from autoware_vehicle_msgs.msg import VelocityReport
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
 
# Tematy /api/... i limit prędkości publikują stan raz, przy zmianie, i zostawiają go
# dla spóźnionych subskrybentów ("transient local"). Trzeba o to poprosić tym samym QoS.
API_QOS = QoSProfile(
    depth=1,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
)
 
 
def nazwy_stalych(klasa_wiadomosci):
    """Stałe z wiadomości jako słownik liczba -> nazwa, np. {2: 'AUTONOMOUS'}."""
    return {v: k for k, v in vars(klasa_wiadomosci).items()
            if k.isupper() and isinstance(v, int)}
 
 
NAZWY_TRYBOW = nazwy_stalych(OperationModeState)
# {0: 'UNKNOWN', 1: 'STOP', 2: 'AUTONOMOUS', 3: 'LOCAL', 4: 'REMOTE'}
NAZWY_STANOW_TRASY = nazwy_stalych(RouteState)
# {0: 'UNKNOWN', 1: 'UNSET', 2: 'SET', 3: 'ARRIVED', 4: 'CHANGING'}
 
 
@dataclass
class StanPojazdu:
    predkosc_kmh: float | None = None            # None = jeszcze nic nie przyszło
    pozycja: tuple[float, float] | None = None   # (x, y) w układzie mapy
    limit_kmh: float | None = None
    tryb: int | None = None
    stan_trasy: int | None = None
    cel: tuple[float, float] | None = None       # (x, y) celu; None = brak trasy
 
    @property
    def do_celu_m(self):
        """Odległość do celu w linii prostej [m] albo None, gdy brak pozycji lub celu."""
        if self.pozycja is None or self.cel is None:
            return None
        return math.dist(self.pozycja, self.cel)
 
 
def tekst(wartosc, wzor='{:.1f}'):
    """Liczba jako tekst albo '—', gdy jeszcze jej nie ma."""
    return '—' if wartosc is None else wzor.format(wartosc)
 
 
def tekst_pozycji(pozycja):
    """Para (x, y) jako tekst albo '—', gdy jeszcze jej nie ma."""
    if pozycja is None:
        return '—'
    x, y = pozycja
    return f'({x:.1f}, {y:.1f})'
 
 
def nazwa(wartosc, nazwy):
    """Liczba jako nazwa stałej, '—' gdy brak, sama liczba gdy nieznana."""
    if wartosc is None:
        return '—'
    return nazwy.get(wartosc, str(wartosc))
 
 
class StanNode(Node):
 
    def __init__(self, nazwa='stan_pojazdu'):
        super().__init__(nazwa)
        self.stan = StanPojazdu()
 
        # Tematy publikowane regularnie (VOLATILE): zwykły QoS, kolejka 10.
        self.create_subscription(
            VelocityReport, '/vehicle/status/velocity_status', self.on_velocity, 10)
        self.create_subscription(
            Odometry, '/localization/kinematic_state', self.on_pozycja, 10)
 
        # Tematy publikowane przy zmianie (TRANSIENT_LOCAL): API_QOS.
        self.create_subscription(
            OperationModeState, '/api/operation_mode/state', self.on_tryb, API_QOS)
        self.create_subscription(
            RouteState, '/api/routing/state', self.on_stan_trasy, API_QOS)
        self.create_subscription(
            VelocityLimit, '/planning/scenario_planning/current_max_velocity',
            self.on_limit, API_QOS)
        self.create_subscription(
            Route, '/api/routing/route', self.on_route, API_QOS)
 
    def on_velocity(self, msg):
        # longitudinal_velocity jest w m/s; abs(), bo na postoju bywa -0.0
        self.stan.predkosc_kmh = abs(msg.longitudinal_velocity) * 3.6
 
    def on_pozycja(self, msg):
        p = msg.pose.pose.position   # Odometry -> PoseWithCovariance -> Pose -> Point
        self.stan.pozycja = (p.x, p.y)
 
    def on_tryb(self, msg):
        self.stan.tryb = msg.mode
 
    def on_stan_trasy(self, msg):
        self.stan.stan_trasy = msg.state
 
    def on_limit(self, msg):
        self.stan.limit_kmh = msg.max_velocity * 3.6   # m/s -> km/h
 
    def on_route(self, msg):
        if msg.data:                        # pusta lista = brak trasy
            g = msg.data[0].goal.position
            self.stan.cel = (g.x, g.y)
        else:
            self.stan.cel = None
 
    def podsumowanie(self):
        s = self.stan
        return (f'v={tekst(s.predkosc_kmh)} km/h, '
                f'limit={tekst(s.limit_kmh, "{:.0f}")} km/h, '
                f'tryb={nazwa(s.tryb, NAZWY_TRYBOW)}, '
                f'trasa={nazwa(s.stan_trasy, NAZWY_STANOW_TRASY)}, '
                f'do celu={tekst(s.do_celu_m, "{:.0f}")} m, '
                f'pozycja={tekst_pozycji(s.pozycja)}')
 
 
def main():
    rclpy.init()
    node = StanNode('stan_pojazdu')
    node.create_timer(1.0, lambda: node.get_logger().info(node.podsumowanie()))
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
 
 
if __name__ == '__main__':
    main()
 