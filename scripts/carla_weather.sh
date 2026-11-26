#!/usr/bin/env bash
# Zmienia pogodę na serwerze CARLA (dla wszystkich podłączonych). Uruchamiać na serwerze.
# Użycie: ./scripts/carla_weather.sh [PRESET]
#   bez argumentu: lista dostępnych presetów i bieżąca pogoda
#   np. ClearNoon, CloudyNoon, WetNoon, HardRainNoon, ClearSunset, ClearNight, HardRainNight
# Ustawiona pogoda obowiązuje do restartu CARLA.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

exec docker compose exec -T carla-master python3 - "${1:-}" <<'EOF'
import sys
import carla

presets = sorted(n for n in dir(carla.WeatherParameters) if n[0].isupper())
world = carla.Client("localhost", 2000).get_world()
name = sys.argv[1]
if not name:
    print("Bieżąca pogoda:", world.get_weather())
    print("Dostępne:", ", ".join(presets))
elif name not in presets:
    sys.exit(f"Nieznana pogoda {name}. Dostępne: {', '.join(presets)}")
else:
    world.set_weather(getattr(carla.WeatherParameters, name))
    print("Pogoda:", name)
EOF
