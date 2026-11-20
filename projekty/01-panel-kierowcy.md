# Projekt 1: Panel kierowcy (HMI)

**Poziom:** ★☆☆ · **Czas:** 2 zajęcia · **Zespół:** 1–2 osoby

## Cel

Napisz okno, które pokazuje, co „myśli” autonomiczne auto: prędkość, obowiązujący limit,
tryb pracy, stan trasy i odległość do celu. Takie panele są w każdym aucie z systemami
wspomagania kierowcy, a tutaj poznasz przy okazji najważniejsze tematy Autoware.

## Czego się nauczysz

- subskrypcji wielu tematów ROS 2 w jednym węźle,
- tematów stanu Autoware AD API i ich QoS (*transient local*),
- łączenia ROS 2 z interfejsem graficznym (PyQt5 albo pygame).

## Przygotowanie

Jeśli to Twój pierwszy kontakt z ROS 2, najpierw przerób
[tutorial „Licznik jazdy”](00-tutorial-licznik-jazdy.md).

1. Uruchom Autoware (`carla-aw`) i przejedź do dowolnego celu, jak w README.
2. W drugim terminalu (`./scripts/aw_shell.sh`) obejrzyj tematy z tabeli poniżej:
   `ros2 topic echo`, `ros2 topic info -v`.
3. Utwórz pakiet `panel_kierowcy` ([wspólne wskazówki](README.md#nowy-pakiet-ros-2)).

| Informacja | Temat | Typ |
|---|---|---|
| prędkość | `/vehicle/status/velocity_status` | `autoware_vehicle_msgs/msg/VelocityReport` |
| pozycja | `/localization/kinematic_state` | `nav_msgs/msg/Odometry` |
| tryb pracy (stop / autonomous / …) | `/api/operation_mode/state` | `autoware_adapi_v1_msgs/msg/OperationModeState` |
| stan trasy | `/api/routing/state` | `autoware_adapi_v1_msgs/msg/RouteState` |
| cel trasy | `/api/routing/route` | `autoware_adapi_v1_msgs/msg/Route` |
| obowiązujący limit prędkości | `/planning/scenario_planning/current_max_velocity` | sprawdź `ros2 topic info` |

## Zadania

1. **Węzeł danych.** Napisz węzeł, który subskrybuje wszystkie tematy z tabeli i trzyma ostatnie
   wartości w jednym obiekcie stanu. Wypisuj go w logu co sekundę (jak `speed_monitor`).
   Tematy `/api/...` subskrybuj z QoS *transient local* (patrz `drive_to_goal.py`).
2. **Okno.** Wyświetl stan w oknie: duży licznik prędkości w km/h, limit, tryb pracy jako
   kolorowa etykieta (np. zielona dla AUTONOMOUS), stan trasy, odległość do celu w linii prostej.
    ROS odbiera wiadomości w osobnym wątku, a okno tylko czyta obiekt stanu. Wzór (wątek,
    executor i poprawne zamykanie) jest w kroku 6 [tutorialu](00-tutorial-licznik-jazdy.md).
    Okno otwiera się z kontenera tak samo jak RViz (wymaga `xhost +local:docker` na hoście).

    - PyQt5: `QTimer` co 100 ms odświeża etykiety.
    - pygame: w pętli gry rysujesz aktualny stan.

3. **Ostrzeżenia.** Licznik zmienia kolor na czerwony, gdy prędkość przekracza limit o więcej
   niż 2 km/h. Gdy tryb pracy zmienia się z AUTONOMOUS na inny, panel pokazuje komunikat
   „Przejmij sterowanie”, ale nie po zwykłym dojeździe do celu (wtedy Autoware samo przechodzi
   w STOP, a stan trasy to ARRIVED).
4. **Test.** Przejedź trasę w trybie autonomicznym, zmieniając limit suwakiem *Set Velocity
   Limit* w RViz. Sprawdź, czy panel nadąża i pokazuje poprawne wartości. W tej konfiguracji
   Autoware jedzie najwyżej 15 km/h, więc suwakiem limit da się tylko obniżyć.

## Wskazówki

- `OperationModeState.mode` to liczba. Stałe z nazwami (`AUTONOMOUS`, `STOP`, …) są w samej
  wiadomości: `ros2 interface show autoware_adapi_v1_msgs/msg/OperationModeState`.
- Cel jest w `Route.data[0].goal`. Lista `data` jest pusta, dopóki trasa nie jest ustawiona.
  Nie używaj `/planning/mission_planning/goal`: tam publikuje tylko narzędzie *2D Goal Pose*
  w RViz, więc przy `drive_to_goal` nic by nie przyszło.
- Panel ma działać także wtedy, gdy któregoś tematu jeszcze nie ma (np. przed ustawieniem celu).
  Pokaż wtedy „—” zamiast wywracać program.
- Nie blokuj pętli GUI: żadnych `rclpy.spin()` ani `time.sleep()` w wątku okna.
  Nie wołaj też `rclpy.spin_once()` w timerze okna: obsługuje jeden callback na wywołanie,
  a sama prędkość i pozycja to ok. 35 wiadomości/s, więc panel by się spóźniał.
- Ctrl+C w terminalu nie zamknie okna Qt sam z siebie. Dodaj
  `signal.signal(signal.SIGINT, lambda *_: app.quit())`.

## Co oddajesz

- pakiet `panel_kierowcy` w `ws/src/` budujący się bez błędów (`colcon build`),
- krótkie nagranie ekranu (do 1 min): przejazd autonomiczny ze zmianą limitu prędkości,
  widoczne RViz i panel,
- `README.md` w pakiecie: jak uruchomić i co pokazuje każde pole.

## Dla chętnych

- wykres prędkości i limitu z ostatnich 60 s (matplotlib osadzony w PyQt5),
- liczba i odległość najbliższego obiektu z `/perception/object_recognition/objects`,
- przycisk „Zatrzymaj” wywołujący `/api/operation_mode/change_to_stop`.
