# Projekt 6: Ocena percepcji

**Poziom:** ★★☆ · **Czas:** 3 zajęcia · **Zespół:** 2 osoby · **Wymaga:** projekt 5 (prawda z CARLA)

## Cel

Sprawdź, jak dobrze Autoware widzi inne auta. Porównaj obiekty wykryte przez percepcję
z prawdziwymi pozycjami aut w CARLA i policz standardowe metryki detekcji w funkcji odległości.

## Czego się nauczysz

- jak wygląda wyjście percepcji Autoware (`PredictedObjects`),
- parowania wykryć z prawdą (przypisanie najbliższego sąsiada z progiem),
- metryk: precyzja, czułość, błąd pozycji, liczba fałszywych wykryć.

## Przygotowanie

- Z projektu 5 masz odczyt prawdy z CARLA i przeliczanie układów. Teraz potrzebujesz pozycji
  wszystkich aut poza swoim (inni studenci, `carla-manual`, ruch uliczny `npc`).
- Poproś prowadzącego o ruch uliczny (`CARLA_NPC_VEHICLES=20` albo więcej) albo umów się
  z innymi zespołami, żeby jeździli w pobliżu.
- Obejrzyj wiadomość: `ros2 interface show autoware_perception_msgs/msg/PredictedObjects`.
  Pozycja obiektu to `objects[i].kinematics.initial_pose_with_covariance.pose.position`.
  Sprawdź ramkę w `header.frame_id`.

## Zadania

1. **Prawda dla wszystkich aut.** Rozszerz węzeł z projektu 5 o publikację pozycji wszystkich
   pojazdów w promieniu 80 m od Twojego auta (np. jako `visualization_msgs/msg/MarkerArray`,
   żeby widzieć je w RViz obok wykryć Autoware). Listę aut odświeżaj raz na sekundę, pozycje
   w każdym kroku.
2. **Parowanie.** Dla każdej wiadomości z `/perception/object_recognition/objects`:
   - weź prawdziwe auta w zasięgu,
   - sparuj każde wykrycie z najbliższym prawdziwym autem, jeśli odległość < 2 m
     (każde auto najwyżej raz),
   - policz: TP (sparowane), FP (wykrycia bez pary), FN (auta bez pary).
   Zapisz do CSV także odległość każdego auta od Twojego.
3. **Metryki w przedziałach odległości** (0–10, 10–20, …, 70–80 m):
   - czułość = TP / (TP + FN), precyzja = TP / (TP + FP),
   - średni błąd pozycji sparowanych obiektów,
   - błąd orientacji (yaw) sparowanych obiektów.
4. **Wykresy.** Czułość i precyzja w funkcji odległości, błąd pozycji w funkcji odległości.
5. **Porównanie warunków.** Powtórz pomiar na tej samej trasie przy innej pogodzie: poproś
   prowadzącego o deszcz albo mgłę na serwerze (`./scripts/carla_weather.sh HardRainNoon`).
   Porównaj krzywe czułości i uzasadnij, skąd biorą się różnice.

## Wskazówki

- Auta częściowo zasłonięte przez inne auta to klasyczne FN. Zastanów się, czy liczyć je
  jako błąd percepcji (opisz w raporcie swoją decyzję).
- Wykrycie może dotyczyć Twojego własnego auta albo pieszego i innych klas: sprawdź
  `classification` i odfiltruj to, czego nie oceniasz.
- Pozycja z CARLA to środek auta na wysokości podłoża, a Autoware podaje środek bryły.
  Porównuj tylko x i y.

## Co oddajesz

- pakiet z węzłem oceny percepcji,
- CSV z co najmniej 10 minut jazdy w ruchu,
- raport: wykresy z zadania 4, tabela metryk, zrzut RViz z prawdą i wykryciami obok siebie,
  wnioski: do jakiej odległości percepcja jest wiarygodna i co ją psuje.

## Dla chętnych

- metryka śledzenia: jak często obiekt zmienia `object_id` (gubi się i pojawia na nowo),
- 6 kamer zamiast jednej (`carla-aw use_light_weight_sensor_mapping:=False`): wymaga CARLA
  uruchomionej na tym samym komputerze, bo przez sieć to za dużo danych,
- ocena predykcji: porównaj przewidywaną ścieżkę obiektu (`kinematics.predicted_paths`)
  z tym, gdzie auto naprawdę było 2 s później.
