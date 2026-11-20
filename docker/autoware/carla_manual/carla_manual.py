#!/usr/bin/env python3
"""Ręczna jazda (manual_control.py z CARLA 0.9.16) we wspólnym świecie z carla-master.

manual_control.py jest bez zmian. Tu tylko blokujemy to, co zmieniłoby świat wszystkim
podłączonym: pogodę (C), warstwy mapy (V/B) oraz nagrywanie i odtwarzanie symulacji
(CTRL+R/CTRL+P - odtwarzanie podmieniłoby symulację każdemu). Tryb --sync też jest wyłączony,
bo świat taktuje carla-master.

Dodatkowa opcja --fps N: ile klatek na sekundę wysyła kamera (domyślnie 20, czyli w każdym
kroku symulacji). Mniej klatek = mniej danych w sieci.
"""

import argparse
import sys

import carla

import manual_control as mc


def _blocked(message):
    def method(self, *args, **kwargs):
        self.hud.notification(message)
    return method


mc.World.next_weather = _blocked("Pogoda jest wspólna dla wszystkich - nie można jej zmienić")
mc.World.next_map_layer = _blocked("Warstwy mapy są wspólne dla wszystkich - nie można ich zmienić")
mc.World.load_map_layer = _blocked("Warstwy mapy są wspólne dla wszystkich - nie można ich zmienić")


def _no_recorder(self, *args, **kwargs):
    print("Nagrywanie i odtwarzanie symulacji jest wyłączone na wspólnym serwerze")
    return ""


carla.Client.start_recorder = _no_recorder
carla.Client.stop_recorder = _no_recorder
carla.Client.replay_file = _no_recorder

_camera_fps = 20.0
_camera_manager_init = mc.CameraManager.__init__


def _camera_manager_with_fps(self, *args, **kwargs):
    _camera_manager_init(self, *args, **kwargs)
    for item in self.sensors:
        blueprint = item[-1]
        if blueprint.id.startswith("sensor.camera") and blueprint.has_attribute("sensor_tick"):
            blueprint.set_attribute("sensor_tick", str(1.0 / _camera_fps))


mc.CameraManager.__init__ = _camera_manager_with_fps

_parse_args = argparse.ArgumentParser.parse_args


def _parse_args_with_fps(self, *args, **kwargs):
    # Dopisujemy --fps do parsera z manual_control.py, żeby był też w --help.
    if not any("--fps" in action.option_strings for action in self._actions):
        self.add_argument(
            "--fps", metavar="N", type=float, default=20.0,
            help="camera frames per second sent over the network (default: 20 = every "
                 "simulation step; fewer = less network traffic, e.g. --fps 8)")
        self.epilog = (
            "carla-manual sets: --host from CARLA_HOST (.env), --rolename manual_<hostname>, "
            "--res 800x450 (override with your own --res). --sync is disabled on the shared "
            "server. Network traffic per person ~ width x height x 4 B x fps, "
            "e.g. --res 320x180 --fps 8 ~ 1.8 MB/s.")
    parsed = _parse_args(self, *args, **kwargs)
    global _camera_fps
    _camera_fps = parsed.fps
    return parsed


argparse.ArgumentParser.parse_args = _parse_args_with_fps

if __name__ == "__main__":
    if "--sync" in sys.argv:
        sys.exit("--sync nie działa ze wspólnym serwerem: świat taktuje carla-master")
    mc.main()
