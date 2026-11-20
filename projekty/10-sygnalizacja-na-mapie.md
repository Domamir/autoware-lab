# Projekt 10: Sygnalizacja świetlna na mapie

**Poziom:** ★★★ · **Czas:** 3–4 zajęcia · **Zespół:** 2 osoby

## Cel

W CARLA działają sygnalizatory, ale mapy lanelet2 z CARLA nie mają ich jako elementów
regulacyjnych, więc Autoware przejeżdża na czerwonym. Dodaj sygnalizację do mapy Town01 na
wybranym skrzyżowaniu i doprowadź do tego, żeby Autoware zatrzymywało się na czerwonym
i ruszało na zielonym.

## Czego się nauczysz

- budowy mapy HD w formacie lanelet2 (pasy, linie zatrzymania, elementy regulacyjne),
- jak Autoware łączy mapę z rozpoznawaniem świateł z kamery,
- debugowania całego łańcucha: mapa → percepcja → planowanie.

## Przygotowanie

- Przeczytaj sekcję o światłach w
  [dokumentacji `autoware_carla_interface`](https://autowarefoundation.github.io/autoware_universe/main/simulator/autoware_carla_interface/).
  Dokumentacja dotyczy najnowszej wersji: opcje `traffic_light.publish` / `traffic_light.map_path`
  (stan świateł prosto z CARLA) **nie istnieją w Autoware 1.9.0**, z którego korzystamy.
  U nas stan świateł rozpoznaje percepcja z obrazu kamery `CAM_FRONT` i to jest częścią zadania.
- Mapa: `~/autoware_data/maps/Town01/lanelet2_map.osm`. **Najpierw zrób kopię zapasową**
  całego katalogu (`cp -r Town01 Town01_oryginal`). `carla-aw` zawsze bierze mapę z katalogu
  o nazwie mapy serwera (`Town01`), więc edytujesz plik na miejscu.
- Edytor: [Vector Map Builder](https://tools.tier4.jp/feature/vector_map_builder_ll2/)
  (w przeglądarce, wymaga konta). Według dokumentacji mapy z CARLA mają przesunięte
  współrzędne geograficzne (lat/lon) względem chmury punktów, więc przed edycją:
  1. przesuń mapę narzędziem [`offset_lanelet2`](https://github.com/mraditya01/offset_lanelet2/tree/main),
  2. przekonwertuj chmurę punktów (`pointcloud_map.pcd`) z `binary_compressed` do `ascii`
     (`pcl_tools`), bo tylko taką wczyta Vector Map Builder,
  3. wczytaj obie w edytorze i dodaj sygnalizację.
- W dokumentacji jest też link do przykładowej mapy Town01 ze światłami na jednym skrzyżowaniu.
  Pobierz ją i obejrzyj, jak zbudowany jest element regulacyjny, zanim zaczniesz własny.

## Zadania

1. **Wybór skrzyżowania.** W oknie CARLA na serwerze (albo w `carla-manual`) znajdź
   skrzyżowanie z sygnalizatorami blisko Twojej trasy. Zapisz pozycje sygnalizatorów z API
   CARLA (`world.get_actors().filter('traffic.traffic_light')`, `get_transform()`) i przelicz je
   do układu mapy (y z przeciwnym znakiem).
2. **Edycja mapy.** Dla pasa wjazdowego na skrzyżowanie dodaj:
   - linię zatrzymania (stop line) przed skrzyżowaniem,
   - sygnalizator (traffic light) jako linię w miejscu świateł, z wysokością,
   - element regulacyjny `traffic_light`, który łączy sygnalizator, linię zatrzymania i pas.
   Identyfikator tego elementu to `traffic_light_group_id`, pod którym Autoware publikuje stan
   światła. Jeden fizyczny sygnalizator może należeć do kilku elementów, po jednym na każdy
   pas wjazdowy.
3. **Test mapy.** Uruchom `carla-aw` z nową mapą. Sprawdź w RViz, że sygnalizator jest
   wyświetlany na mapie. Typowe błędy: zły układ współrzędnych, brak powiązania z pasem.
4. **Rozpoznawanie.** Podjedź pod skrzyżowanie i sprawdź:
   - `/perception/traffic_light_recognition/traffic_signals`: czy pojawia się stan światła,
   - panel `RecognitionResultOnImage` w RViz: czy na obrazie z kamery zaznaczony jest obszar
     sygnalizatora (domyślnie tam pokazywane jest „No Image”, a teraz powinien pojawić się obraz).
5. **Jazda.** Ustaw cel za skrzyżowaniem. Nagraj przejazdy przy czerwonym i zielonym świetle:
   prędkość, stan światła z percepcji i prawdziwy stan z CARLA (`traffic_light.get_state()`).
   Policz, w jakiej odległości od linii auto się zatrzymuje i z jakim opóźnieniem rusza po
   zmianie na zielone.

## Wskazówki

- Zmieniaj mapę małymi krokami i po każdym kroku sprawdzaj, czy Autoware się uruchamia.
  Błąd w mapie potrafi zatrzymać cały start, a wtedy szukaj komunikatów o lanelet2 w logu `carla-aw`.
- Rozpoznawanie świateł korzysta z kamery. Przy domyślnej jednej kamerze (`CAM_FRONT`) światło
  musi być w jej polu widzenia, więc sprawdź, z jakiej odległości jest widoczne.
- Na serwerze sygnalizatory zmieniają się według zegara symulacji, więc czas cyklu zależy od
  tempa symulacji.

## Co oddajesz

- zmieniona mapa `lanelet2_map.osm` (oraz opis zmian: identyfikatory dodanych elementów),
- nagranie ekranu: Autoware zatrzymuje się na czerwonym i rusza na zielonym,
- raport: opis struktury elementu regulacyjnego z rysunkiem, wyniki z zadania 5, napotkane
  problemy i ich rozwiązania.

## Dla chętnych

- sygnalizacja na całej trasie taksówki z projektu 4,
- porównanie stanu rozpoznanego z kamery z prawdziwym: jak często i z jakiej odległości
  rozpoznanie się myli.
