# Projekt 7: Asystent bezpieczeństwa

**Poziom:** ★★☆ · **Czas:** 3 zajęcia · **Zespół:** 2 osoby · **Wymaga:** projekt 2 (scenariusze)

## Cel

Napisz niezależny węzeł „drugiej pary oczu”, który obserwuje jazdę Autoware i ostrzega
przed ryzykiem, podobnie jak systemy ADAS w autach seryjnych: liczy czas do kolizji, wykrywa
gwałtowne hamowania i zbyt bliskie podjeżdżanie.

## Czego się nauczysz

- metryk ryzyka: czas do kolizji (TTC), odstęp czasowy (time headway),
- łączenia trajektorii z planowania z obiektami z percepcji,
- wizualizacji ostrzeżeń w RViz.

## Przygotowanie

- Scenariusze i rejestrator z projektu 2 posłużą do testów.
- Tematy:

| Co | Temat | Typ |
|---|---|---|
| obiekty | `/perception/object_recognition/objects` | `autoware_perception_msgs/msg/PredictedObjects` |
| plan jazdy | `/planning/trajectory` | `autoware_planning_msgs/msg/Trajectory` |
| stan auta | `/localization/kinematic_state` | `nav_msgs/msg/Odometry` |
| polecenie sterowania | `/control/command/control_cmd` | `autoware_control_msgs/msg/Control` |

## Zadania

1. **Obiekty na trajektorii.** Dla każdego obiektu sprawdź, czy leży na zaplanowanej
   trajektorii: odległość od najbliższego punktu trajektorii < połowa szerokości pasa (~1,5 m).
   Dla takich obiektów policz odległość wzdłuż trajektorii od auta.
2. **TTC i odstęp.**
   - TTC = odległość wzdłuż trajektorii / (prędkość auta − prędkość obiektu wzdłuż trajektorii),
     liczone tylko, gdy auto się zbliża,
   - odstęp czasowy = odległość / prędkość auta.
3. **Poziomy ostrzeżeń.** Publikuj stan na `/asystent/poziom` (np. `std_msgs/msg/String`):
   - `OK`,
   - `UWAGA`: TTC < 4 s albo odstęp < 1,5 s,
   - `ZAGROŻENIE`: TTC < 2 s albo zadane hamowanie mocniejsze niż −3 m/s².
   Dodaj histerezę (stan zmienia się dopiero, gdy warunek trwa co najmniej 0,3 s), żeby
   ostrzeżenia nie migały.
4. **Wizualizacja.** `MarkerArray` w RViz: obiekt, którego dotyczy ostrzeżenie, pokolorowany
   według poziomu, i tekst z wartością TTC nad nim.
5. **Test na scenariuszach.** Odegraj scenariusze z projektu 2. Dla każdego zapisz, kiedy
   asystent ostrzegł, a kiedy zareagowało Autoware (zmiana `longitudinal.acceleration`).
   Czy asystent ostrzega wcześniej? Czy są fałszywe alarmy (np. auto na sąsiednim pasie
   na zakręcie)?

## Wskazówki

- Trajektoria ma punkty z pozycją i prędkością. Odległość wzdłuż niej licz jako sumę odcinków
  od punktu najbliższego autu do punktu najbliższego obiektowi.
- Prędkość obiektu jest w `kinematics.initial_twist_with_covariance` (w układzie obiektu).
  Rzutuj ją na kierunek trajektorii w miejscu obiektu.
- Gdy trajektorii jeszcze nie ma (przed ustawieniem trasy), asystent powinien zgłaszać
  `BRAK DANYCH`, a nie `OK`.

## Co oddajesz

- pakiet `asystent_bezpieczenstwa` z plikiem launch,
- nagranie ekranu RViz z ostrzeżeniami w co najmniej dwóch scenariuszach,
- raport: wzory i progi, tabela „ostrzeżenie asystenta kontra reakcja Autoware” dla każdego
  scenariusza, analiza fałszywych alarmów.

## Dla chętnych

- dyskusja: czy asystent powinien móc sam zatrzymać auto (`/api/operation_mode/change_to_stop`)?
  Jakie ryzyka niesie drugi system, który może hamować? Zaimplementuj to tylko w trybie
  testowym, za parametrem domyślnie wyłączonym,
- połącz z panelem z projektu 1.
