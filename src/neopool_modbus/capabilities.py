# Copyright 2026 Milos Svasek

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Capability predicates over a decoded NeoPool data snapshot.

Each predicate consumes the dict produced by ``NeoPoolModbusClient.async_read_all``
and returns whether a given module is present on the controller. The runtime
status bits (set by ``status_mask`` decoders) are preferred where available;
factory-only modules without a runtime indicator (ION, UV, salinity) fall back
to the ``MBF_PAR_MODEL`` bitmask.

The predicates are pure: no I/O, no global state. Callers that need module
presence to survive a Home Assistant restart while the controller is offline
should persist a :func:`capability_snapshot` and feed it back when the live
read is unavailable.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .decoders import get_filtration_pump_type
from .registers import is_valid_relay_gpio

_MBMSK_MODEL_ION = 0x0001
_MBMSK_MODEL_UV = 0x0004
_MBMSK_MODEL_SALINITY = 0x0008

# Every key any of the predicates below consults. capability_snapshot()
# extracts exactly this subset so a persisted snapshot stays predicate-complete
# across restarts.
CAPABILITY_KEYS: tuple[str, ...] = (
    "Chlorine measurement module detected",
    "Conductivity measurement module detected",
    "Hydrolysis module detected",
    "MBF_PAR_FILTRATION_CONF",
    "MBF_PAR_FILTVALVE_ENABLE",
    "MBF_PAR_FILTVALVE_GPIO",
    "MBF_PAR_HEATING_GPIO",
    "MBF_PAR_HEATING_MODE",
    "MBF_PAR_MODEL",
    "MBF_PAR_TEMPERATURE_ACTIVE",
    "Redox measurement module detected",
    "pH measurement module detected",
)


def capability_snapshot(data: Mapping[str, Any]) -> dict[str, Any]:
    """Return the subset of *data* that the capability predicates consult."""
    return {k: data[k] for k in CAPABILITY_KEYS if k in data}


def is_hydrolysis_present(data: dict[str, Any]) -> bool:
    """True when the hydrolysis module is detected by the runtime check."""
    return bool(data.get("Hydrolysis module detected"))


def is_ph_module_present(data: dict[str, Any]) -> bool:
    """True when the pH measurement module reports as present."""
    return bool(data.get("pH measurement module detected"))


def is_redox_module_present(data: dict[str, Any]) -> bool:
    """True when the Redox measurement module reports as present."""
    return bool(data.get("Redox measurement module detected"))


def is_chlorine_module_present(data: dict[str, Any]) -> bool:
    """True when the Chlorine measurement module reports as present."""
    return bool(data.get("Chlorine measurement module detected"))


def is_conductivity_module_present(data: dict[str, Any]) -> bool:
    """True when the Conductivity measurement module reports as present."""
    return bool(data.get("Conductivity measurement module detected"))


def is_ionization_present(data: dict[str, Any]) -> bool:
    """True when the ION bit of MBF_PAR_MODEL is set (factory install)."""
    return bool((data.get("MBF_PAR_MODEL") or 0) & _MBMSK_MODEL_ION)


def is_uv_lamp_present(data: dict[str, Any]) -> bool:
    """True when the UV-lamp bit of MBF_PAR_MODEL is set (factory install)."""
    return bool((data.get("MBF_PAR_MODEL") or 0) & _MBMSK_MODEL_UV)


def is_salinity_module_present(data: dict[str, Any]) -> bool:
    """True when the salinity bit of MBF_PAR_MODEL is set (factory install)."""
    return bool((data.get("MBF_PAR_MODEL") or 0) & _MBMSK_MODEL_SALINITY)


def is_temperature_active(data: dict[str, Any]) -> bool:
    """True when the controller has the temperature sensor enabled."""
    return bool(data.get("MBF_PAR_TEMPERATURE_ACTIVE"))


def has_heating_relay(data: dict[str, Any]) -> bool:
    """True when a relay GPIO is assigned to the heating output."""
    return is_valid_relay_gpio(data.get("MBF_PAR_HEATING_GPIO") or 0)


def has_variable_speed_pump(data: dict[str, Any]) -> bool:
    """True when the configured filtration pump supports variable speeds."""
    return bool(get_filtration_pump_type(data.get("MBF_PAR_FILTRATION_CONF") or 0))


def has_filtvalve(data: dict[str, Any]) -> bool:
    """True when a Besgo automatic filter valve is configured.

    The primary signal is the relay GPIO assignment (1-7); the legacy
    ``MBF_PAR_FILTVALVE_ENABLE`` flag is accepted as a fallback when the
    GPIO register is zero but the feature flag is explicitly set.
    """
    gpio = data.get("MBF_PAR_FILTVALVE_GPIO") or 0
    enable = data.get("MBF_PAR_FILTVALVE_ENABLE") or 0
    return is_valid_relay_gpio(gpio) or enable != 0


def is_heating_mode_enabled(data: dict[str, Any]) -> bool:
    """True when MBF_PAR_HEATING_MODE is set to its enabled value (1)."""
    return int(data.get("MBF_PAR_HEATING_MODE") or 0) == 1


def available_filtration_modes(data: dict[str, Any]) -> tuple[str, ...]:
    """Return the filtration modes that make sense for this controller.

    ``manual`` and ``auto`` are always available. ``smart`` requires the
    temperature sensor to be active; ``heating`` and ``intelligent``
    additionally need the heating relay assigned and MBF_PAR_HEATING_MODE
    enabled. ``backwash`` is offered when an automatic filter valve is
    configured.
    """
    modes: list[str] = ["manual", "auto"]
    temperature_active = is_temperature_active(data)
    heating_ready = (
        temperature_active and has_heating_relay(data) and is_heating_mode_enabled(data)
    )
    if heating_ready:
        modes.append("heating")
    if temperature_active:
        modes.append("smart")
    if heating_ready:
        modes.append("intelligent")
    if has_filtvalve(data):
        modes.append("backwash")
    return tuple(modes)


def available_filtration_speeds(data: dict[str, Any]) -> tuple[str, ...]:
    """Return the speeds offered by a variable-speed filtration pump.

    Empty when the configured pump is single-speed. ``off`` is a valid wire
    value but is not surfaced as a select option since stopping the pump is
    typically driven by the filtration mode rather than the speed select.
    """
    if not has_variable_speed_pump(data):
        return ()
    return ("low", "mid", "high")


def available_cell_boost_modes(data: dict[str, Any]) -> tuple[str, ...]:
    """Return the cell-boost modes offered by this controller.

    Empty without a hydrolysis cell. ``active_with_redox`` is only offered
    when the redox measurement module is also present; without it the user
    can still run the boost without redox-driven dosing.
    """
    if not is_hydrolysis_present(data):
        return ()
    if is_redox_module_present(data):
        return ("inactive", "active", "active_with_redox")
    return ("inactive", "active")


__all__ = [
    "CAPABILITY_KEYS",
    "available_cell_boost_modes",
    "available_filtration_modes",
    "available_filtration_speeds",
    "capability_snapshot",
    "has_filtvalve",
    "has_heating_relay",
    "has_variable_speed_pump",
    "is_chlorine_module_present",
    "is_conductivity_module_present",
    "is_heating_mode_enabled",
    "is_hydrolysis_present",
    "is_ionization_present",
    "is_ph_module_present",
    "is_redox_module_present",
    "is_salinity_module_present",
    "is_temperature_active",
    "is_uv_lamp_present",
]
