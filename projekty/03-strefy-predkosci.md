# Projekt 3: Strefy ograniczenia prędkości

**Poziom:** ★★☆ · **Czas:** 2–3 zajęcia · **Zespół:** 1–2 osoby

## Cel

Zdefiniuj na mapie strefy z własnym limitem prędkości (np. „szkoła” 20 km/h, „osiedle”
30 km/h) i napisz węzeł, który ustawia Autoware limit zależnie od tego, w której strefie jest
auto. Sprawdź, jak płynnie i jak wcześnie auto dostosowuje prędkość.

## Czego się nauczysz

- publikowania poleceń do Autoware (zewnętrzny limit prędkości),
- geometrii w układzie mapy: sprawdzanie, czy punkt leży w wielokącie,
- oceny zachowania planowania prędkości na wykresach.

## Przygotowanie

- Uruchom `carla-aw` i przejedź trasę, na której będą strefy.
- Zapisz kilka punktów na mapie: narzędziem *2D Goal Pose* w RViz kliknij w miejsce i odczytaj
  współrzędne z `ros2 topic echo /planning/mission_planning/goal`. Przy okazji przyda się
  narzędzie *Publish Point* w RViz i temat `/clicked_point`.

Limit prędkości ustawia ten sam temat, którego używa suwak *Set Velocity Limit* w RViz:

| | |
|---|---|
| temat | `/planning/scenario_planning/max_velocity_default` |
| typ | `autoware_internal_planning_msgs/msg/VelocityLimit` |
| najważniejsze pola | `stamp`, `max_velocity` (m/s), `sender` |

Zanim zaczniesz, sprawdź to sam: `ros2 topic info -v /planning/scenario_planning/max_velocity_default`,
przesuń suwak w RViz i obejrzyj wiadomość (`ros2 topic echo`).

## Zadania

1. **Strefy.** Zapisz w pliku YAML co najmniej 3 strefy jako wielokąty (lista punktów x, y
   w układzie mapy) z nazwą i limitem w km/h. Przynajmniej dwie strefy leżą na jednej trasie.
2. **Węzeł `strefy_predkosci`.**
   - Czyta YAML (ścieżka jako parametr).
   - Subskrybuje `/localization/kinematic_state` i sprawdza, w której strefie jest auto.
     Do testu „punkt w wielokącie” wystarczy `matplotlib.path.Path(punkty).contains_point((x, y))`.
   - Przy wjeździe do strefy i wyjeździe z niej publikuje nowy limit (poza strefami: limit
     domyślny, parametr). Loguje zmianę.
3. **Wizualizacja.** Publikuj strefy jako `visualization_msgs/msg/MarkerArray` (np. `LINE_STRIP`
   w ramce `map`, z podpisem `TEXT_VIEW_FACING`). Dodaj temat w RViz (*Add → By topic*).
4. **Pomiary.** Nagraj przejazd przez strefy (`ros2 bag`: prędkość, pozycja, Twoje limity).
   Narysuj wykres prędkości i limitu w funkcji drogi.
5. **Analiza.** Auto zwalnia dopiero po wjeździe do strefy, bo wtedy dostaje nowy limit.
   Zmień węzeł tak, żeby limit przychodził wcześniej: sprawdzaj nie tylko bieżącą pozycję, ale
   też punkt kilkadziesiąt metrów dalej na trajektorii (`/planning/trajectory`). Porównaj
   wykresy przed i po zmianie.

## Wskazówki

- Nie publikuj limitu w każdej wiadomości odometrii (50 Hz), tylko przy zmianie strefy i np.
  raz na sekundę dla pewności.
- `max_velocity` jest w m/s, a strefy w km/h.
- Ustaw strefę z limitem wyższym niż prędkość, z jaką auto normalnie jedzie. Czy przyspiesza?
  Jeśli nie, to coś innego ogranicza prędkość: znajdź co (np. limit pasa w mapie lanelet2,
  atrybut `speed_limit` w `~/autoware_data/maps/Town01/lanelet2_map.osm`, albo parametry
  planowania) i opisz to w raporcie.

## Co oddajesz

- pakiet `strefy_predkosci` z plikiem stref i plikiem launch,
- zrzut ekranu RViz z widocznymi strefami,
- wykresy prędkości i limitu przed i po ulepszeniu z zadania 5 oraz komentarz: w jakiej
  odległości przed strefą auto zaczyna hamować i z jakim opóźnieniem.

## Dla chętnych

- strefy czasowe (np. „szkoła” obowiązuje tylko co drugą minutę czasu symulacji),
- płynne przejście: limit maleje liniowo na ostatnich 30 m przed strefą,
- zapis stref z RViz: klikanie punktów narzędziem *Publish Point* dopisuje je do YAML.
