# Projekt 1 krok po kroku: Panel kierowcy

## Wprowadzenie

W tym projekcie napiszesz okno, które pokazuje, co „myśli” autonomiczne auto. Gotowy panel
wygląda mniej więcej tak:

```
+-----------------------------+
|             15              |
|            km/h             |
|     [   AUTONOMOUS   ]      |
|  Limit             15 km/h  |
|  Trasa                 SET  |
|  Do celu              83 m  |
+-----------------------------+
```

Projekt jest podzielony na 8 kroków. Każdy kończy się punktem **Sprawdź**: nie idź dalej,
dopóki nie działa. Proponowany podział: na pierwszych zajęciach kroki 1–5 (węzeł danych
w terminalu), na drugich kroki 6–8 (okno, ostrzeżenia, oddanie).

**Zanim zaczniesz:** przerób tutorial „Licznik jazdy”. Projekt korzysta z trzech rzeczy,
które tam poznasz: obiektu stanu z timerem (krok 4 tutorialu), QoS `API_QOS` (krok 5)
i okna PyQt5 z ROS w osobnym wątku (krok 6). Kod z tutorialu możesz kopiować.

**Co oddajesz** (szczegóły w kroku 8): pakiet `panel_kierowcy`, nagranie ekranu do 1 minuty
i `README.md` pakietu.

## Krok 1. Rozpoznaj tematy

Uruchom Autoware (`carla-aw`) i ustaw dowolny cel w RViz (*2D Goal Pose*). Niektóre tematy
pojawiają się dopiero, gdy Autoware pierwszy raz zaplanuje trasę. W drugim terminalu
(`./scripts/aw_shell.sh`) obejrzyj tematy, z których zbudujesz panel:

| Informacja | Temat |
|---|---|
| prędkość | `/vehicle/status/velocity_status` |
| pozycja auta | `/localization/kinematic_state` |
| tryb pracy | `/api/operation_mode/state` |
| stan trasy | `/api/routing/state` |
| cel trasy | `/api/routing/route` |
| obowiązujący limit prędkości | `/planning/scenario_planning/current_max_velocity` |

Dla każdego tematu:

```bash
ros2 topic info -v /planning/scenario_planning/current_max_velocity   # Type i Durability
ros2 interface show <typ z poprzedniej komendy>                         # pola wiadomości
ros2 topic echo /api/routing/route                                      # przykładowa wiadomość
```

Zapisz w notatkach: typ wiadomości, pole z potrzebną wartością i jednostkę, a także
`Durability` u nadawcy (VOLATILE albo TRANSIENT_LOCAL).

**Sprawdź:**

1. Limit prędkości jest typu `autoware_internal_planning_msgs/msg/VelocityLimit`, a wartość
   jest w polu `max_velocity` w m/s.
2. Trzy tematy `/api/...` i limit mają `TRANSIENT_LOCAL`. Te cztery będziesz subskrybować
   z `API_QOS`.
3. Wiesz, gdzie w wiadomości `Route` jest pozycja celu (podpowiedź: `data` to lista).
4. Po kliknięciu **Clear Route** w RViz lista `data` w `/api/routing/route` jest pusta.

Nie używaj tematu `/planning/mission_planning/goal`. Publikuje tam tylko narzędzie
*2D Goal Pose* w RViz, więc gdy trasę ustawi `drive_to_goal`, nic by tam nie przyszło.

## Krok 2. Pakiet

```bash
cd ~/ws/src
ros2 pkg create panel_kierowcy --build-type ament_python --license Apache-2.0 \
    --dependencies rclpy nav_msgs autoware_vehicle_msgs autoware_adapi_v1_msgs \
    autoware_internal_planning_msgs
```

Kod podzielisz na dwa pliki w `panel_kierowcy/panel_kierowcy/`:

- `stan.py`: węzeł danych (kroki 3–5). Uruchomiony sam wypisuje stan w terminalu.
- `panel.py`: okno (kroki 6–7). Korzysta z węzła z `stan.py`.

Dopisz od razu obie komendy w `setup.py`:

```python
        'console_scripts': [
            'stan = panel_kierowcy.stan:main',
            'panel = panel_kierowcy.panel:main',
        ],
```

**Sprawdź:** `cd ~/ws && colcon build --symlink-install --packages-select panel_kierowcy`
kończy się `Summary: 1 package finished`. Pliki `stan.py` i `panel.py` mogą być na razie puste,
komenda `ros2 run` zadziała dopiero po kroku 3.

## Krok 3. Węzeł danych: prędkość i pozycja

Zacznij od dwóch najprostszych tematów, tak jak licznik w tutorialu. W `stan.py`:

```python
@dataclass
class StanPojazdu:
    predkosc_kmh: float | None = None       # None = jeszcze nic nie przyszło
    pozycja: tuple[float, float] | None = None   # (x, y) w układzie mapy
    # w krokach 4-5 dopiszesz: limit_kmh, tryb, stan_trasy, cel
```

Napisz klasę węzła `StanNode`, która:

- tworzy obiekt `StanPojazdu`,
- subskrybuje prędkość i pozycję (zwykły QoS, kolejka 10) i zapisuje wartości do stanu,
- ma metodę `podsumowanie()` zwracającą tekst w rodzaju
  `v=12.3 km/h, pozycja=(201.4, -55.0)`, z „—” w miejscu brakujących wartości.

Konstruktor niech przyjmuje nazwę węzła, jak `Licznik` w tutorialu. W kroku 6 okno użyje
tej samej klasy pod inną nazwą. Funkcja `main()` w `stan.py` tworzy węzeł o nazwie
`stan_pojazdu` i timer, który co sekundę wypisuje `podsumowanie()`.

**Sprawdź:**

```bash
ros2 run panel_kierowcy stan --ros-args -p use_sim_time:=true
```

Co sekundę jedna linia. W czasie jazdy prędkość i pozycja się zmieniają, a na postoju
prędkość wynosi 0.

## Krok 4. Tematy stanu Autoware

Dopisz do stanu i do węzła tryb pracy, stan trasy i limit prędkości. Wszystkie trzy tematy
subskrybuj z `API_QOS` (skopiuj z tutorialu). Bez tego dostaniesz wartość dopiero przy jej
zmianie.

- **Tryb** i **stan trasy** to liczby. Zamiast przepisywać nazwy ręcznie, odczytaj je ze stałych
  zdefiniowanych w samej wiadomości:

```python
NAZWY_TRYBOW = {v: k for k, v in vars(OperationModeState).items()
                if k.isupper() and isinstance(v, int)}
# {0: 'UNKNOWN', 1: 'STOP', 2: 'AUTONOMOUS', 3: 'LOCAL', 4: 'REMOTE'}
```

- **Limit** przychodzi w m/s, a panel pokazuje km/h.

Dopisz nowe pola do `podsumowanie()`.

**Sprawdź:**

1. Zaraz po uruchomieniu węzła tryb i stan trasy mają wartość (np. `tryb=STOP, trasa=UNSET`),
   a nie „—”.
2. Limit pojawia się, gdy Autoware pierwszy raz zaplanuje trasę. W tej konfiguracji to 15 km/h.
3. Po kliknięciu Auto w RViz tryb zmienia się na AUTONOMOUS, a po dojeździe do celu sam
   wraca na STOP przy stanie trasy ARRIVED.

## Krok 5. Cel trasy i odległość

Cel jest w pierwszym elemencie listy `data` wiadomości `Route`. Lista jest pusta, gdy trasy
nie ma, więc trzeba to sprawdzić:

```python
def on_route(self, msg):
    if msg.data:                        # pusta lista = brak trasy
        g = msg.data[0].goal.position
        self.stan.cel = (g.x, g.y)
    else:
        self.stan.cel = None
```

Odległość do celu w linii prostej policz z pozycji i celu (`math.dist`). Zwracaj `None`,
gdy brakuje któregoś z nich. Najwygodniej jako metodę albo `@property` w `StanPojazdu`.

**Sprawdź:**

1. Bez ustawionego celu: `do celu=—`, a program działa dalej.
2. Po ustawieniu celu odległość jest bliska tej z RViz i maleje w czasie jazdy.
3. Po dojeździe zostaje mniej niż ok. 2 m.
4. Po **Clear Route** w RViz znowu pojawia się „—”.

Teraz węzeł danych jest gotowy: to jest zadanie 1 projektu.

## Krok 6. Okno

Zbuduj okno w `panel.py` według kroku 6 tutorialu: ROS w osobnym wątku z executorem,
`QTimer` co 100 ms przepisuje stan do etykiet, a na końcu sprzątanie w dobrej kolejności.
Węzeł utwórz jako `StanNode('panel_kierowcy')`, czyli pod inną nazwą niż w `stan.py`.

Elementy okna:

- duży licznik prędkości (`QLabel` z dużą czcionką, `setAlignment(Qt.AlignCenter)`),
- etykieta trybu pracy,
- trzy wiersze: Limit, Trasa, Do celu (`QGridLayout`: nazwa w kolumnie 0, wartość w kolumnie 1).

Licznik pokazuj bez miejsc po przecinku. Uwaga na „-0”: na postoju Autoware raportuje czasem
-0.0 km/h. Pomoże `round()` albo `abs()`.

**Sprawdź:**

```bash
ros2 run panel_kierowcy panel --ros-args -p use_sim_time:=true
```

1. Okno pokazuje te same wartości co `stan` uruchomiony obok w drugim terminalu.
2. `ros2 node list | sort | uniq -d` nic nie wypisuje (nazwy węzłów się nie powtarzają).
3. Okno zamyka się bez błędów i krzyżykiem, i przez Ctrl+C w terminalu.

## Krok 7. Kolory i ostrzeżenia

Dopisz trzy rzeczy w metodzie okna, która co 100 ms odświeża etykiety:

1. **Kolor trybu.** Tło etykiety zależy od trybu, np. zielone dla AUTONOMOUS, czerwone dla STOP,
   szare dla nieznanego: `etykieta.setStyleSheet(f'background: {kolor}; color: white')`.
2. **Czerwony licznik**, gdy prędkość przekracza limit o więcej niż 2 km/h. Gdy prędkości albo
   limitu jeszcze nie ma, licznik zostaje w normalnym kolorze.
3. **„Przejmij sterowanie”**: komunikat widoczny przez 5 s, gdy tryb zmienił się z AUTONOMOUS
   na inny. Okno musi pamiętać tryb z poprzedniego odświeżenia. Czas odmierzaj
   `time.monotonic()`. Wyjątek: po zwykłym dojeździe do celu Autoware samo przechodzi w STOP,
   a stan trasy to wtedy ARRIVED. To nie powód do alarmu.

Wyjście z trybu autonomicznego (do testu 3) wymusisz w drugim terminalu poleceniem:

```bash
ros2 service call /api/operation_mode/change_to_stop autoware_adapi_v1_msgs/srv/ChangeOperationMode
```

**Sprawdź** (wszystkie cztery testy w czasie jazdy autonomicznej):

1. Przy limicie 15 km/h licznik się nie czerwieni. Auto przekracza limit najwyżej o ok. 1 km/h.
2. Obniż limit suwakiem *Set Velocity Limit* w RViz do 5 km/h. Licznik robi się czerwony
   i wraca do normalnego koloru, gdy auto zwolni.
3. Po poleceniu `change_to_stop` pojawia się „Przejmij sterowanie” i znika po 5 s.
4. Po zwykłym dojeździe do celu komunikat się nie pojawia.

Suwak działa tylko w dół: w tej konfiguracji Autoware jedzie najwyżej 15 km/h.

## Krok 8. Test końcowy i oddanie

Przejdź listę kontrolną:

1. `colcon build --packages-select panel_kierowcy` bez błędów.
2. Panel uruchomiony przed ustawieniem celu pokazuje „—” tam, gdzie brak danych, i się nie
   wywraca.
3. Przejazd autonomiczny od startu do celu: wszystkie pola się zgadzają, kolory i komunikat
   działają jak w kroku 7.
4. Okno zamyka się czysto.

Oddajesz:

- pakiet `panel_kierowcy` w `ws/src/`,
- nagranie ekranu do 1 minuty: przejazd autonomiczny ze zmianą limitu prędkości, widoczne
  RViz i panel,
- `README.md` w pakiecie: jak uruchomić i co pokazuje każde pole (z jakiego tematu pochodzi).

**Dla chętnych:**

- wykres prędkości i limitu z ostatnich 60 s (matplotlib osadzony w PyQt5),
- liczba i odległość najbliższego obiektu z `/perception/object_recognition/objects`,
- przycisk „Zatrzymaj” wywołujący `/api/operation_mode/change_to_stop`.

## Gdy coś nie działa

| Objaw | Przyczyna |
|---|---|
| tryb, trasa albo limit pokazują „—” mimo działającego Autoware | brak `API_QOS` przy subskrypcji (krok 4) |
| limit „—”, a reszta działa | Autoware jeszcze nie zaplanowało żadnej trasy: ustaw cel |
| `do celu` zawsze „—” | cel z `/planning/mission_planning/goal` zamiast `/api/routing/route` (krok 1) |
| `IndexError` w `on_route` | brak sprawdzenia, czy lista `data` nie jest pusta (krok 5) |
| przycisk Auto w RViz nieaktywny | dwa węzły o tej samej nazwie (krok 6, `ros2 node list`) |
| panel się spóźnia albo zacina | `rclpy.spin_once()` w timerze okna zamiast osobnego wątku |
| `Segmentation fault` przy zamykaniu | zła kolejność sprzątania (krok 6 tutorialu) |
| okno nie reaguje na Ctrl+C | brak `signal.signal(signal.SIGINT, ...)` |
| `could not connect to display` | na hoście: `xhost +local:docker` |
| „Przejmij sterowanie” po każdym dojeździe do celu | brak wyjątku dla stanu trasy ARRIVED (krok 7) |
