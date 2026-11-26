#!/usr/bin/env bash
# Kto jest podłączony do serwera CARLA i jak szybko idzie symulacja.
# Działa na serwerze (przez kontener carla-master) i na terminalu (przez kontener autoware,
# serwer z CARLA_HOST w .env).
# Użycie: ./scripts/carla_status.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [ -n "$(docker compose ps -q --status running carla-master 2>/dev/null)" ]; then
    ON_SERVER=1
    RUN=(docker compose exec -T -e CARLA_HOST=localhost carla-master python3 -)
elif [ -n "$(docker compose ps -q --status running autoware 2>/dev/null)" ]; then
    ON_SERVER=0
    RUN=(docker compose exec -T autoware python3 -)
else
    echo "Nie działa ani carla-master (serwer), ani autoware (terminal): docker compose up -d autoware" >&2
    exit 1
fi

"${RUN[@]}" <<'EOF'
import os
import time

import carla

host = os.environ.get("CARLA_HOST", "localhost").split("/")[0]
client = carla.Client(host, 2000)
client.set_timeout(10.0)
world = client.get_world()

print(f"== Serwer CARLA {host}, mapa {world.get_map().name.split('/')[-1]}")
start = world.wait_for_tick(10.0)
t0 = time.time()
time.sleep(3.0)
end = world.wait_for_tick(10.0)
wall = time.time() - t0
steps = (end.frame - start.frame) / wall
sim = (end.timestamp.elapsed_seconds - start.timestamp.elapsed_seconds) / wall
print(f"   {steps:.1f} kroków/s, czas symulacji {100 * sim:.0f}% czasu rzeczywistego")

print("\n== Auta w świecie")
vehicles = world.get_actors().filter("vehicle.*")
kinds = {"ego_": "Autoware (carla-aw)", "manual_": "jazda ręczna (carla-manual)"}
npc = 0
for v in sorted(vehicles, key=lambda v: v.attributes.get("role_name", "")):
    role = v.attributes.get("role_name", "")
    if role == "npc":
        npc += 1
        continue
    kind = next((k for p, k in kinds.items() if role.startswith(p)), "inne")
    print(f"   {role:35s} {kind:28s} {v.type_id:35s} {3.6 * v.get_velocity().length():5.0f} km/h")
print(f"   ruch uliczny (npc): {npc} aut")
EOF

echo
if [ "$ON_SERVER" = 1 ]; then
    echo "== Komputery połączone z CARLA (TCP 2000)"
    ss -tn state established '( sport = :2000 )' | awk 'NR>1 {split($4, a, ":"); print a[1]}' \
        | grep -v '^127\.0\.0\.1$' | sort | uniq -c | awk '{print "   " $2 " (" $1 " połączeń)"}' || true
    echo
    echo "== Ostatnie statystyki carla-master"
    # --tail zamiast --since: przy niezsynchronizowanym zegarze serwera --since potrafi nic nie zwrócić.
    LINE=$(docker compose logs -t --tail 20 carla-master 2>/dev/null | grep "kroków/s" | tail -1)
    if [ -n "$LINE" ]; then
        echo "$LINE" | sed -E 's/^[^|]*\| ([0-9-]+)T([0-9:]+)\.[0-9]+Z /   [\1 \2 UTC] /'
    else
        echo "   brak statystyk w ostatnich wpisach logu"
    fi
else
    echo "(Adresy IP podłączonych komputerów i statystyki mastera: uruchom ten skrypt na serwerze)"
fi
