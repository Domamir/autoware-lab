# Projekt 4: Autonomiczna taksówka

**Poziom:** ★★☆ · **Czas:** 3 zajęcia · **Zespół:** 2 osoby

## Cel

Rozwiń przykład `drive_to_goal` w usługę taksówki: auto obsługuje listę przystanków
(odbiór, postój, cel), radzi sobie z błędami i wraca do bazy. Na ostatnich zajęciach wszystkie
zespoły jeżdżą jednocześnie w tym samym świecie, a ranking ocenia czas i komfort jazdy.

## Czego się nauczysz

- sterowania Autoware przez AD API (lokalizacja, trasa, tryb pracy),
- projektowania maszyny stanów z obsługą błędów i limitów czasu,
- liczenia wskaźników komfortu jazdy (przyspieszenie, szarpnięcie).

## Przygotowanie

- Przeczytaj [`drive_to_goal.py`](../ws/src/carla_autoware_examples/carla_autoware_examples/drive_to_goal.py)
  i uruchom go (README, sekcja *Uruchomienie* terminala).
- Usługi i tematy AD API używane w przykładzie:

| Co | Nazwa | Typ |
|---|---|---|
| inicjalizacja lokalizacji | `/api/localization/initialize` | `autoware_adapi_v1_msgs/srv/InitializeLocalization` |
| usunięcie trasy | `/api/routing/clear_route` | `autoware_adapi_v1_msgs/srv/ClearRoute` |
| ustawienie trasy | `/api/routing/set_route_points` | `autoware_adapi_v1_msgs/srv/SetRoutePoints` |
| tryb autonomiczny | `/api/operation_mode/change_to_autonomous` | `autoware_adapi_v1_msgs/srv/ChangeOperationMode` |
| stan lokalizacji | `/api/localization/initialization_state` | `autoware_adapi_v1_msgs/msg/LocalizationInitializationState` |
| stan trasy | `/api/routing/state` | `autoware_adapi_v1_msgs/msg/RouteState` |
| tryb pracy | `/api/operation_mode/state` | `autoware_adapi_v1_msgs/msg/OperationModeState` |

## Zadania

1. **Przystanki.** Wybierz na Town01 co najmniej 5 przystanków (współrzędne z RViz, patrz
   projekt 3) i zapisz je w YAML: nazwa, x, y, yaw, czas postoju.
2. **Maszyna stanów.** Węzeł `taksowka` przechodzi przez stany:
   `INICJALIZACJA → TRASA → JAZDA → POSTÓJ → (następny przystanek) … → POWRÓT → KONIEC`.
   - `TRASA`: usuń starą trasę, ustaw nową, czekaj, aż `RouteState` będzie `SET`.
   - `JAZDA`: włącz tryb autonomiczny i czekaj na `ARRIVED`.
   - `POSTÓJ`: odczekaj zadany czas symulacji (`use_sim_time:=true`!).
   Każdy stan loguje wejście i wyjście z czasem.
3. **Błędy.** Obsłuż co najmniej:
   - trasa nie została wyznaczona (np. cel poza drogą): pomiń przystanek i zaloguj błąd,
   - auto stoi w trybie autonomicznym dłużej niż 30 s (zablokowane przez inne auto): spróbuj
     ponownie ustawić trasę; po trzech próbach pomiń przystanek,
   - tryb autonomiczny został wyłączony z zewnątrz (np. przycisk w RViz): przejdź do stanu
     `PRZERWANO` i nie włączaj go sam.
4. **Pomiar.** Dla każdego odcinka zapisz: czas przejazdu, długość drogi (z pozycji),
   średnią i maksymalną prędkość, maksymalne |przyspieszenie| i maksymalne |szarpnięcie|
   (pochodna przyspieszenia). Przyspieszenie licz z prędkości z `/localization/kinematic_state`,
   z wygładzaniem (np. średnia z 5 próbek), bo różniczkowanie wzmacnia szum.
5. **Wyścig.** Wszystkie zespoły jadą tę samą listę przystanków jednocześnie, wychodząc
   z różnych miejsc mapy (inne auta są przeszkodami). Prowadzący może włączyć ruch uliczny
   (`CARLA_NPC_VEHICLES`).

## Wskazówki

- Kolejność wywołań i oczekiwanie na stany macie gotowe w `drive_to_goal.py`
  (`wait_until`, `call`). Przenieś je do klasy maszyny stanów, zamiast kopiować.
- Wartości stanów (`SET`, `ARRIVED`, `AUTONOMOUS`, …) są stałymi w wiadomościach:
  `ros2 interface show autoware_adapi_v1_msgs/msg/RouteState`.
- Przystanek musi leżeć na pasie ruchu i w zgodnym z nim kierunku (yaw), inaczej trasa się
  nie wyznaczy.

## Co oddajesz

- pakiet `taksowka` z plikiem przystanków,
- log z przejazdu całej misji i tabela pomiarów dla każdego odcinka,
- raport: diagram maszyny stanów, opis obsługi błędów z przykładami z logu, wyniki wyścigu.

**Ranking wyścigu:** łączny czas misji + 10 s kary za każdy pominięty przystanek + 5 s za każde
przekroczenie |szarpnięcia| > 2 m/s³.

## Dla chętnych

- zamówienia „na żywo”: węzeł przyjmuje nowe przystanki z tematu w trakcie misji i wybiera
  najbliższy,
- połącz z projektem 1: panel pokazuje aktualny przystanek i stan misji.
