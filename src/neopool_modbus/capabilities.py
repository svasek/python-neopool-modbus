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
"""

from __future__ import annotations

from typing import Any

_MBMSK_MODEL_ION = 0x0001
_MBMSK_MODEL_UV = 0x0004
_MBMSK_MODEL_SALINITY = 0x0008


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


__all__ = [
    "is_chlorine_module_present",
    "is_conductivity_module_present",
    "is_hydrolysis_present",
    "is_ionization_present",
    "is_ph_module_present",
    "is_redox_module_present",
    "is_salinity_module_present",
    "is_uv_lamp_present",
]
