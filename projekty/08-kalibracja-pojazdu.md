# Projekt 8: Kalibracja nowego pojazdu

**Poziom:** ★★★ · **Czas:** 3–4 zajęcia · **Zespół:** 2 osoby

## Cel

Autoware steruje autem przez mapy kalibracyjne: jakie położenie gazu lub hamulca daje jakie
przyspieszenie przy danej prędkości. W tym repo są one tylko dla Toyoty Prius. Wybierz inne
auto z CARLA, zmierz jego charakterystykę, zbuduj własne mapy i sprawdź, czy Autoware prowadzi
je płynnie.

## Czego się nauczysz

- jak Autoware zamienia zadane przyspieszenie na pedały (`raw_vehicle_cmd_converter`),
- identyfikacji dynamiki pojazdu z pomiarów,
- planowania eksperymentu i czyszczenia danych pomiarowych.

## Przygotowanie

Mapy Priusa są w obrazie Autoware:
`/opt/autoware/autoware_carla_interface/share/autoware_carla_interface/` (`accel_map.csv`,
`brake_map.csv`, `steer_map.csv`). Skopiuj je do `~/ws/kalibracja/` i obejrzyj.

Format `accel_map.csv` (tak samo `brake_map.csv`):

```
default,0,1.39,2.78,...,13.89      <- prędkość [m/s] w kolumnach
0,0.090,-0.204,-0.490,...           <- pedał 0.0: przyspieszenie [m/s²] dla każdej prędkości
0.100,0.167,0.166,-0.093,...        <- pedał 0.1 ...
```

Konfiguracja konwertera to `config/raw_vehicle_cmd_converter.param.yaml` w tym samym pakiecie.
Ścieżki do map są w polach `csv_path_accel_map`, `csv_path_brake_map`, `csv_path_steer_map`.

## Zadania

1. **Wybór auta.** Wybierz pojazd z CARLA wyraźnie inny niż Prius, np. ciężki van
   (`vehicle.mercedes.sprinter`) albo sportowe auto. Przejedź się nim: `carla-manual --filter vehicle.mercedes.sprinter`.
   Zobacz, jak Autoware prowadzi je z mapami Priusa:
   `carla-aw vehicle_type:=vehicle.mercedes.sprinter`. Opisz, co jest nie tak.
2. **Skrypt pomiarowy.** Napisz skrypt w Pythonie, który przez API CARLA:
   - tworzy Twoje auto testowe z `role_name` = `kalibracja_<komputer>` na długiej prostej
     (przy końcu skryptu usuwa je: `actor.destroy()`, także w `finally`),
   - dla każdej wartości gazu 0,1 … 1,0: rozpędza auto stałym gazem
     (`apply_control(carla.VehicleControl(throttle=...))`) i co krok zapisuje prędkość
     i przyspieszenie wzdłuż kierunku jazdy,
   - tak samo dla hamulca: rozpędza auto do ~50 km/h i hamuje stałą siłą,
   - czeka na kolejne kroki przez `world.wait_for_tick()`. **Nie wywołuje `world.tick()`
     ani nie zmienia ustawień świata.**
3. **Mapy.** Z pomiarów zbuduj `accel_map.csv` i `brake_map.csv` w tym samym formacie
   (te same prędkości w kolumnach), np. uśredniając przyspieszenie w przedziałach prędkości
   (pandas `groupby`) i uzupełniając brakujące komórki interpolacją. Przyspieszenie musi rosnąć
   razem z pedałem gazu, sprawdź to.
4. **Konfiguracja.** Skopiuj `raw_vehicle_cmd_converter.param.yaml` do `~/ws/kalibracja/`,
   wpisz w nim pełne ścieżki do swoich map i uruchom:
   ```bash
   carla-aw vehicle_type:=vehicle.mercedes.sprinter raw_vehicle_cmd_converter_config:=/home/aw/ws/kalibracja/raw_vehicle_cmd_converter.param.yaml
   ```
5. **Ocena.** Przejedź tę samą trasę trzy razy: Prius z jego mapami, nowe auto z mapami Priusa,
   nowe auto z Twoimi mapami. Porównaj zadane przyspieszenie (`/control/command/control_cmd`)
   z rzeczywistym (z prędkości w `/vehicle/status/velocity_status`) i odchyłkę prędkości
   od planu (`/planning/trajectory`).

## Wskazówki

- Przyspieszenie z różniczkowania prędkości jest zaszumione: wygładź prędkość przed
  różniczkowaniem albo licz z większego okna.
- Na początku każdej próby auto rusza i zmienia bieg: odrzuć te fragmenty albo opisz je.
- Ruch innych aut przeszkadza w pomiarach. Wybierz mało uczęszczaną prostą albo zróbcie
  pomiary, gdy na serwerze jest mało osób.
- Mapa skrętu (`steer_map.csv`) jest w konfiguracji wyłączona (`convert_steer_cmd: false`),
  więc wystarczy gaz i hamulec.

## Co oddajesz

- skrypt pomiarowy, surowe dane CSV i skrypt budujący mapy,
- gotowe `accel_map.csv`, `brake_map.csv` i plik konfiguracji,
- raport: wykresy map (przyspieszenie w funkcji prędkości dla każdego pedału, porównanie
  z Priusem), porównanie trzech przejazdów z zadania 5, wnioski.

## Dla chętnych

- porównaj swoje mapy z danymi fizyki pojazdu z CARLA (`vehicle.get_physics_control()`:
  masa, krzywa momentu silnika),
- automatyczny dobór map podczas jazdy: uczenie się poprawek na podstawie błędu przyspieszenia.
