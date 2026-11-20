# Projekt 5: Dokładność lokalizacji

**Poziom:** ★★☆ · **Czas:** 2–3 zajęcia · **Zespół:** 1–2 osoby

## Cel

Zmierz, jak dokładnie Autoware wie, gdzie jest. Porównaj pozycję z lokalizacji Autoware
(dopasowanie chmury punktów z lidaru do mapy, NDT, i filtr Kalmana, EKF) z prawdziwą pozycją
auta w CARLA. Sprawdź, gdzie na mapie i w jakich warunkach błąd rośnie.

## Czego się nauczysz

- jak działa lokalizacja w Autoware i czym jest prawda z symulatora (ground truth),
- przeliczania układów współrzędnych (CARLA ↔ mapa Autoware),
- analizy błędów: wartości średnie, percentyle, mapa cieplna.

Narzędzie z tego projektu (odczyt prawdy z CARLA i przeliczanie układów) przyda się
w projektach 6 i 9, więc napisz je porządnie.

## Przygotowanie

- Przeczytaj [Prawda z CARLA](README.md#prawda-z-carla-ground-truth) w README projektów.
- Uruchom `carla-aw` i zainicjalizuj lokalizację (*Initialize with GNSS*).

## Zadania

1. **Węzeł `prawda_carla`.** Publikuje prawdziwą pozycję Twojego auta jako
   `nav_msgs/msg/Odometry` na temacie `/ground_truth/odometry` (ramka `map`, 20 Hz), już
   w układzie Autoware (y i yaw z przeciwnym znakiem). Sprawdź w RViz, że strzałka z Twojego
   tematu pokrywa się z autem.
2. **Węzeł `blad_lokalizacji`.** Dla każdej wiadomości z `/localization/kinematic_state` liczy
   względem ostatniej prawdy z CARLA:
   - błąd położenia wzdłuż kierunku jazdy i w poprzek (rozbij wektor błędu na te dwie osie),
   - błąd kąta yaw (pamiętaj o zawijaniu kąta do przedziału −π…π),
   - błąd prędkości.
   Zapisuje wszystko do CSV razem z pozycją i prędkością.
3. **Przejazdy.** Nagraj co najmniej 3 przejazdy po różnych częściach Town01: proste ulice,
   skrzyżowania, otwarty teren przy rzece. Jeden z nich z ruchem ulicznym, jeśli prowadzący
   go włączy.
4. **Analiza.**
   - tabela: średni, mediana, 95. percentyl i maksimum błędu w każdej osi,
   - mapa cieplna: trasa na płaszczyźnie x–y pokolorowana wartością błędu (matplotlib `scatter`),
   - wykres błędu w funkcji prędkości.
5. **Wpływ startu.** Zainicjalizuj lokalizację celowo źle (*2D Pose Estimate* kilka metrów
   obok auta) i zmierz, czy i jak szybko błąd maleje.

## Wskazówki

- Błąd „w poprzek” jest ważniejszy niż „wzdłuż”: 30 cm w poprzek to już wjazd na sąsiedni pas.
- Pomiar pierwszych sekund po inicjalizacji odrzuć (osobno opisz w zadaniu 5).
- Jeśli błąd skacze o całe metry, sprawdź najpierw przeliczenie układów i synchronizację
  czasu, a dopiero potem wiń lokalizację.

## Co oddajesz

- pakiet z węzłami `prawda_carla` i `blad_lokalizacji`,
- pliki CSV z przejazdów i notatnik albo skrypt z analizą,
- raport: tabela błędów, mapa cieplna, wnioski, gdzie lokalizacja jest najsłabsza i dlaczego
  (np. mało charakterystycznych obiektów dla lidaru, zasłonięcie przez inne auta).

## Dla chętnych

- porównaj z samym GNSS (`/sensing/gnss/pose_with_covariance`): o ile lokalizacja z lidaru
  jest lepsza?
- deszcz i mgła: poproś prowadzącego o zmianę pogody na serwerze
  (`./scripts/carla_weather.sh HardRainNoon`) i powtórz pomiar.
