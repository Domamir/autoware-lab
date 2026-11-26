# Projekt 9: Własny detektor przeszkód z lidaru

**Poziom:** ★★★ · **Czas:** 3–4 zajęcia · **Zespół:** 2 osoby · **Wymaga:** projekt 6 (metryki)

## Cel

Napisz od zera prosty detektor aut z chmury punktów lidaru: usuń podłoże, pogrupuj punkty
w obiekty i otocz je prostopadłościanami. Porównaj go z percepcją Autoware i z prawdą z CARLA,
używając metryk z projektu 6.

## Czego się nauczysz

- pracy z chmurą punktów (`sensor_msgs/msg/PointCloud2`) w Pythonie,
- klasycznego potoku detekcji: filtracja, segmentacja podłoża, grupowanie, dopasowanie bryły,
- pracy offline na nagranych danych (`ros2 bag`).

## Przygotowanie

- Temat lidaru: `/sensing/lidar/top/pointcloud_before_sync`. Sprawdź jego ramkę
  (`header.frame_id`) i pola punktu (`ros2 topic echo --once ... --no-arr` albo
  `ros2 topic info -v`).
- Do odczytu punktów: `sensor_msgs_py.point_cloud2.read_points_numpy(msg, field_names=('x','y','z'))`.
- Dostępne biblioteki: numpy, scipy (`scipy.spatial.cKDTree`, `scipy.ndimage`), matplotlib.
  Open3D i scikit-learn nie są zainstalowane, więc algorytmy napiszesz sam, co jest celem
  projektu.

## Zadania

1. **Dane.** Nagraj 3–5 minut jazdy w ruchu (poproś o `CARLA_NPC_VEHICLES`):
   lidar, `/localization/kinematic_state`, `/perception/object_recognition/objects`, `/tf`,
   `/tf_static` i prawdę z CARLA z projektu 6 (np. Twój temat z pozycjami aut).
   Pracuj na nagraniu (`ros2 bag play --clock`), żeby każdy przebieg był powtarzalny.
2. **Filtracja.** Odrzuć punkty dalej niż 50 m, punkty na samym aucie (prostokąt wokół
   czujnika) i punkty wyżej niż 3 m nad podłożem.
3. **Podłoże.** Zaimplementuj usuwanie podłoża, np. dopasowanie płaszczyzny metodą RANSAC
   albo siatkę komórek 1 × 1 m z odrzuceniem punktów bliskich minimum wysokości w komórce.
4. **Grupowanie.** Euklidesowe grupowanie punktów (sąsiedzi w promieniu ~0,7 m przez
   `cKDTree.query_ball_point`) albo etykietowanie połączonych komórek w siatce 2D
   (`scipy.ndimage.label`). Odrzuć grupy za małe i za duże jak na auto.
5. **Bryły i publikacja.** Dla każdej grupy dopasuj prostokąt w płaszczyźnie x–y
   (np. obrót, który minimalizuje pole prostokąta) i wysokość. Publikuj jako `MarkerArray`
   w RViz obok wykryć Autoware.
6. **Ocena.** Przelicz wykrycia do układu mapy (pozycja auta z lokalizacji albo `tf`)
   i użyj kodu z projektu 6: czułość, precyzja i błąd pozycji w funkcji odległości dla
   Twojego detektora i dla Autoware na tym samym nagraniu.

## Wskazówki

- Zacznij od wizualizacji: po każdym kroku publikuj chmurę pośrednią (`PointCloud2`)
  i oglądaj ją w RViz.
- Python bywa za wolny na pełną chmurę w czasie rzeczywistym. Wektoryzuj w numpy i sprawdzaj
  czas przetwarzania jednej klatki. Na nagraniu możesz odtwarzać wolniej (`ros2 bag play -r 0.5`).
- Dwa auta stojące obok siebie łatwo zlewają się w jedną grupę: pokaż to w raporcie i zaproponuj
  poprawkę.

## Co oddajesz

- pakiet `detektor_lidar` z węzłem i plikiem launch odtwarzającym nagranie,
- nagranie danych (albo instrukcję, jak je odtworzyć),
- raport: opis każdego kroku potoku z obrazkiem z RViz, czas przetwarzania klatki,
  porównanie metryk z Autoware, typowe błędy Twojego detektora.

## Dla chętnych

- śledzenie obiektów między klatkami (najbliższy sąsiad + filtr Kalmana) i prędkość obiektów,
- uruchomienie na żywo podczas jazdy i porównanie z nagraniem.
