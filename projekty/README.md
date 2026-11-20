# Projekty na zajęcia

Dziesięć mini projektów opartych na tym środowisku: wspólny serwer CARLA, Autoware 1.9
(`carla-aw`), ręczna jazda (`carla-manual`) i własne pakiety ROS 2 w `ws/`. Kolejność
odpowiada kolejności zajęć: od najprostszych do projektów zaliczeniowych.

| # | Projekt | Poziom | Zajęcia | Wymaga wcześniej |
|---|---|---|---|---|
| 0 | [Tutorial: Licznik jazdy](00-tutorial-licznik-jazdy.md) | krok po kroku | 1 | — |
| 1 | [Panel kierowcy (HMI)](01-panel-kierowcy.md) | ★☆☆ | 2 | 0 |
| 2 | [Człowiek kontra Autoware](02-czlowiek-kontra-autoware.md) | ★☆☆ | 2–3 | — |
| 3 | [Strefy ograniczenia prędkości](03-strefy-predkosci.md) | ★★☆ | 2–3 | — |
| 4 | [Autonomiczna taksówka](04-autonomiczna-taksowka.md) | ★★☆ | 3 | — |
| 5 | [Dokładność lokalizacji](05-dokladnosc-lokalizacji.md) | ★★☆ | 2–3 | — |
| 6 | [Ocena percepcji](06-ocena-percepcji.md) | ★★☆ | 3 | 5 (prawda z CARLA) |
| 7 | [Asystent bezpieczeństwa](07-asystent-bezpieczenstwa.md) | ★★☆ | 3 | 2 (scenariusze) |
| 8 | [Kalibracja nowego pojazdu](08-kalibracja-pojazdu.md) | ★★★ | 3–4 | — |
| 9 | [Własny detektor przeszkód z lidaru](09-detektor-z-lidaru.md) | ★★★ | 3–4 | 6 (metryki) |
| 10 | [Sygnalizacja świetlna na mapie](10-sygnalizacja-na-mapie.md) | ★★★ | 3–4 | — |

Przed pierwszym projektem przejdź [README repozytorium](../README.md): instalację terminala,
`carla-manual` i uruchomienie Autoware z przejazdem do celu.

## Wspólne wskazówki

### Nowy pakiet ROS 2

Pakiety trzymaj w `ws/src/` (na hoście, np. w VS Code), buduj w kontenerze (`./scripts/aw_shell.sh`):

```bash
cd ~/ws/src
ros2 pkg create moj_pakiet --build-type ament_python --dependencies rclpy   # nazwa przed --dependencies
cd ~/ws && colcon build --symlink-install --packages-select moj_pakiet
source install/setup.bash
```

Wzorem jest [`carla_autoware_examples`](../ws/src/carla_autoware_examples): `speed_monitor`
(subskrypcja, publikacja, timer, parametr) i `drive_to_goal` (usługi Autoware AD API).
Nowy węzeł dopisz w `setup.py` w `entry_points`.

### Czas symulacji

Autoware działa w czasie symulacji (temat `/clock`), a symulacja bywa wolniejsza niż czas
rzeczywisty. Twoje węzły też muszą go używać, inaczej znaczniki czasu i timery się rozjadą:

```bash
ros2 run moj_pakiet moj_wezel --ros-args -p use_sim_time:=true
```

### Unikalne nazwy węzłów

Autoware pilnuje, żeby żadna nazwa węzła nie powtarzała się w systemie (`duplicated_node_checker`).
Dwa węzły o tej samej nazwie to dla niego błąd i **auto nie przejdzie w tryb autonomiczny**:
w RViz przycisk AUTO jest nieaktywny, a `drive_to_goal` czeka do przekroczenia czasu.
Zdarza się to łatwo, np. gdy ten sam węzeł działa w dwóch terminalach. Sprawdź:

```bash
ros2 node list | sort | uniq -d       # puste = OK
```

### Sprawdzanie tematów

Zanim napiszesz subskrypcję, sprawdź typ i częstotliwość tematu przy działającym Autoware:

```bash
ros2 topic list | grep perception
ros2 topic info -v /perception/object_recognition/objects     # typ, QoS, kto publikuje
ros2 topic hz /localization/kinematic_state
ros2 interface show autoware_perception_msgs/msg/PredictedObjects
```

Tematy stanu w AD API (`/api/...`) mają QoS *transient local*. Subskrybuj je z tym samym QoS
(przykład w `drive_to_goal.py`), inaczej nie dostaniesz ostatniej wiadomości.

### Prawda z CARLA (ground truth)

CARLA zna dokładne położenie każdego auta. W kontenerze Autoware jest pakiet `carla` dla
Pythona, więc Twój węzeł może je odczytać. Twoje auto nazywa się `ego_<nazwa komputera>`,
auta z `carla-manual` to `manual_<komputer>`, ruch uliczny to `npc`.

```python
import math
import os
import socket

import carla

client = carla.Client(os.environ.get('CARLA_HOST', 'localhost'), 2000)
client.set_timeout(5.0)
world = client.get_world()
world.wait_for_tick()    # bez tego świeży klient widzi pustą listę aktorów


def find_vehicle(role_name):
    for actor in world.get_actors().filter('vehicle.*'):
        if actor.attributes.get('role_name') == role_name:
            return actor
    return None


ego = find_vehicle(f'ego_{socket.gethostname()}')
t = ego.get_transform()
# Układ CARLA -> układ mapy Autoware: oś y i kąt yaw mają przeciwny znak.
x, y = t.location.x, -t.location.y
yaw = -math.radians(t.rotation.yaw)
speed = ego.get_velocity().length()          # m/s
```

Zasady na wspólnym serwerze:

- **Tylko odczyt.** Nie wywołuj `world.tick()`, `world.apply_settings()`, `client.load_world()`
  ani nie zmieniaj pogody: świat taktuje `carla-master` i zepsułbyś symulację wszystkim.
- `get_transform()` i `get_velocity()` czytają stan odebrany lokalnie (bez zapytania do serwera),
  więc można je wywoływać często. `world.get_actors()` to zapytanie przez sieć: listę aut
  odświeżaj raz na sekundę, nie w każdym kroku.
- Czas symulacji w ROS (`/clock`) liczy się od startu mostu, a w CARLA od startu serwera, więc
  znaczniki się różnią. Najprościej porównywać ostatnie wartości obu źródeł w chwili odebrania
  wiadomości z ROS. Przy 20 krokach/s błąd to najwyżej jeden krok (0,05 s × prędkość).

### Nagrywanie danych

```bash
ros2 bag record -o ~/ws/dane/przejazd1 /localization/kinematic_state /perception/object_recognition/objects
ros2 bag play ~/ws/dane/przejazd1 --clock     # odtworzenie z czasem symulacji
```

Wyniki (CSV, wykresy) zapisuj w `~/ws/`, czyli w katalogu `ws/` repozytorium na hoście.
