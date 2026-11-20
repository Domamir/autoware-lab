# Projekt 2: Człowiek kontra Autoware

**Poziom:** ★☆☆ · **Czas:** 2–3 zajęcia · **Zespół:** 2 osoby (kierowca + inżynier testów)

## Cel

Sprawdź, jak Autoware reaguje na niebezpieczne zachowania innego kierowcy. Jedna osoba jedzie
ręcznie (`carla-manual`) i odgrywa scenariusze, druga obserwuje Autoware i mierzy reakcję.
Tak wygląda testowanie scenariuszowe w prawdziwych projektach jazdy autonomicznej.

## Czego się nauczysz

- projektowania powtarzalnych scenariuszy testowych,
- definiowania metryk bezpieczeństwa (odległość, czas reakcji, opóźnienie),
- odczytu prawdziwych pozycji aut z symulatora i zapisu pomiarów do CSV.

## Przygotowanie

- Oba komputery łączą się z tym samym serwerem CARLA (`CARLA_HOST` w `.env`).
- Osoba A: `carla-aw` i przejazd do celu w trybie autonomicznym.
- Osoba B: `carla-manual` na drugim komputerze. Jej auto widać w świecie Autoware jako zwykłą
  przeszkodę.
- Przeczytaj [Prawda z CARLA](README.md#prawda-z-carla-ground-truth).

## Zadania

1. **Scenariusze.** Zaprojektujcie co najmniej 4 scenariusze, każdy opisany tak, żeby dało się
   go powtórzyć: miejsce na mapie, prędkości, co robi kierowca. Propozycje:
   - auto stoi na pasie Autoware za zakrętem,
   - kierowca wjeżdża przed Autoware z bocznej ulicy (zajechanie drogi),
   - kierowca jedzie przed Autoware i nagle hamuje,
   - kierowca jedzie pod prąd na pasie Autoware.
2. **Rejestrator.** Węzeł w pakiecie `testy_scenariuszy`, który w czasie scenariusza zapisuje
   do CSV co krok:
   - czas symulacji,
   - prędkość Autoware (`/vehicle/status/velocity_status`),
   - zadane przyspieszenie (`/control/command/control_cmd`, typ `autoware_control_msgs/msg/Control`,
     pole `longitudinal.acceleration`),
   - odległość między autami z CARLA (`ego_<komputer A>` i `manual_<komputer B>`). Liczysz ją
     w układzie CARLA, więc przeliczanie współrzędnych nie jest potrzebne,
   - czy Autoware widzi auto kierowcy: obiekt z `/perception/object_recognition/objects` bliżej
     niż 3 m od jego prawdziwej pozycji (tu już potrzebne przeliczenie z README).
3. **Metryki.** Dla każdego przejazdu policz w Pythonie (pandas):
   - minimalną odległość między autami,
   - czas reakcji: od pierwszego wykrycia auta kierowcy do chwili, gdy zadane przyspieszenie
     spada poniżej −1 m/s²,
   - największe opóźnienie (najmniejsze `longitudinal.acceleration`),
   - wynik: zaliczony, jeśli nie było kolizji i minimalna odległość > 2 m.
4. **Seria.** Każdy scenariusz co najmniej 3 razy. Zmieniajcie się rolami.

## Wskazówki

- Kolizję w CARLA poznasz po gwałtownym spadku odległości do ~0 i skoku prędkości. Możesz też
  dołączyć do auta Autoware czujnik `sensor.other.collision`, ale wtedy pamiętaj o usunięciu go
  na końcu (`sensor.destroy()`), żeby nie zostawiać obiektów na wspólnym serwerze.
- Uruchamiaj rejestrator przed rozpoczęciem scenariusza i zatrzymuj po nim: jeden plik CSV
  na przejazd.
- Scenariusz z nagłym hamowaniem jest najłatwiejszy do powtórzenia: kierowca jedzie przed
  Autoware i hamuje spacją (hamulec ręczny) w umówionym miejscu.

## Co oddajesz

- opis scenariuszy (tabela: nazwa, miejsce, przebieg, oczekiwane zachowanie Autoware),
- pakiet z rejestratorem i skrypt liczący metryki,
- raport (2–3 strony): tabela wyników wszystkich przejazdów, wykres odległości i przyspieszenia
  w czasie dla najciekawszego przejazdu, wnioski: które scenariusze Autoware oblewa i dlaczego
  (percepcja nie wykryła? za późno? planowanie nie zahamowało?).

## Dla chętnych

- powtórz najtrudniejszy scenariusz z ruchem ulicznym i porównaj wyniki,
- zautomatyzuj scenariusz nagłego hamowania: zamiast człowieka skrypt w Pythonie sterujący
  własnym autem (`apply_control`) przez API CARLA.
