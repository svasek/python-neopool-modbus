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

import pytest

from neopool_modbus import capabilities
from neopool_modbus.capabilities import (
    CAPABILITY_KEYS,
    capability_snapshot,
    has_filtvalve,
    has_heating_relay,
    has_variable_speed_pump,
    is_chlorine_module_present,
    is_conductivity_module_present,
    is_hydrolysis_present,
    is_ionization_present,
    is_ph_module_present,
    is_redox_module_present,
    is_salinity_module_present,
    is_temperature_active,
    is_uv_lamp_present,
)


@pytest.mark.parametrize(
    ("predicate", "key"),
    [
        (is_hydrolysis_present, "Hydrolysis module detected"),
        (is_ph_module_present, "pH measurement module detected"),
        (is_redox_module_present, "Redox measurement module detected"),
        (is_chlorine_module_present, "Chlorine measurement module detected"),
        (is_conductivity_module_present, "Conductivity measurement module detected"),
    ],
)
def test_runtime_predicates(predicate, key):
    """Runtime predicates read a single boolean key from the snapshot."""
    assert predicate({key: True}) is True
    assert predicate({key: False}) is False
    assert predicate({}) is False
    assert predicate({key: None}) is False


@pytest.mark.parametrize(
    ("predicate", "bit"),
    [
        (is_ionization_present, 0x0001),
        (is_uv_lamp_present, 0x0004),
        (is_salinity_module_present, 0x0008),
    ],
)
def test_factory_bitmask_predicates(predicate, bit):
    """Factory predicates read the matching bit of MBF_PAR_MODEL."""
    assert predicate({"MBF_PAR_MODEL": bit}) is True
    assert predicate({"MBF_PAR_MODEL": 0xFFFF}) is True
    assert predicate({"MBF_PAR_MODEL": 0}) is False
    # Other-bit-only must not produce a false positive.
    assert predicate({"MBF_PAR_MODEL": 0xFFFF & ~bit}) is False
    # Missing or None register defaults to absent.
    assert predicate({}) is False
    assert predicate({"MBF_PAR_MODEL": None}) is False


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({"MBF_PAR_TEMPERATURE_ACTIVE": 1}, True),
        ({"MBF_PAR_TEMPERATURE_ACTIVE": 0}, False),
        ({"MBF_PAR_TEMPERATURE_ACTIVE": None}, False),
        ({}, False),
    ],
)
def test_is_temperature_active(data, expected):
    assert is_temperature_active(data) is expected


@pytest.mark.parametrize(
    ("gpio", "expected"),
    [
        (1, True),
        (7, True),
        (0, False),
        (8, False),  # outside valid range
        (None, False),
    ],
)
def test_has_heating_relay(gpio, expected):
    """has_heating_relay accepts only valid relay GPIO numbers (1-7)."""
    data = {} if gpio is None else {"MBF_PAR_HEATING_GPIO": gpio}
    assert has_heating_relay(data) is expected


@pytest.mark.parametrize(
    ("conf", "expected"),
    [
        # MBF_PAR_FILTRATION_CONF lower nibble: 0 = standard pump,
        # 1/2 = variable-speed pump types
        (0x0000, False),
        (0x0001, True),
        (0x0002, True),
        # Upper bits (speed selection, etc.) must not affect the predicate.
        (0x00F0, False),
        (0x00F1, True),
        (None, False),
    ],
)
def test_has_variable_speed_pump(conf, expected):
    data = {} if conf is None else {"MBF_PAR_FILTRATION_CONF": conf}
    assert has_variable_speed_pump(data) is expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ({"MBF_PAR_FILTVALVE_GPIO": 5}, True),
        ({"MBF_PAR_FILTVALVE_GPIO": 0, "MBF_PAR_FILTVALVE_ENABLE": 1}, True),
        ({"MBF_PAR_FILTVALVE_ENABLE": 1}, True),
        ({"MBF_PAR_FILTVALVE_GPIO": 0, "MBF_PAR_FILTVALVE_ENABLE": 0}, False),
        # GPIO outside the hardware range and no enable -> not present.
        ({"MBF_PAR_FILTVALVE_GPIO": 8}, False),
        ({}, False),
    ],
)
def test_has_filtvalve(data, expected):
    assert has_filtvalve(data) is expected


# ---------------------------------------------------------------------------
# capability_snapshot + CAPABILITY_KEYS
# ---------------------------------------------------------------------------


def test_capability_snapshot_extracts_only_listed_keys():
    """Snapshot keeps every CAPABILITY_KEYS that is present and drops the rest."""
    data = {
        "MBF_PAR_MODEL": 0x000F,
        "Hydrolysis module detected": True,
        # Not in CAPABILITY_KEYS, must be dropped:
        "MBF_FOO_BAR": 42,
        "FILTRATION_SPEED": 2,
    }
    snapshot = capability_snapshot(data)
    assert snapshot == {
        "MBF_PAR_MODEL": 0x000F,
        "Hydrolysis module detected": True,
    }


def test_capability_snapshot_skips_missing_keys():
    """Missing keys are not back-filled; the snapshot mirrors what was present."""
    assert capability_snapshot({}) == {}


def test_capability_snapshot_preserves_falsey_values():
    """Falsey values (0, False, None) are still part of the snapshot if present."""
    data = {
        "MBF_PAR_MODEL": 0,
        "Hydrolysis module detected": False,
        "MBF_PAR_FILTVALVE_GPIO": None,
    }
    assert capability_snapshot(data) == data


_ALL_PREDICATES = (
    has_filtvalve,
    has_heating_relay,
    has_variable_speed_pump,
    is_chlorine_module_present,
    is_conductivity_module_present,
    is_hydrolysis_present,
    is_ionization_present,
    is_ph_module_present,
    is_redox_module_present,
    is_salinity_module_present,
    is_temperature_active,
    is_uv_lamp_present,
)


def test_capability_keys_covers_every_predicate_lookup():
    """CAPABILITY_KEYS must list every key any predicate consults.

    Without this, a snapshot persisted across a restart could miss a key the
    predicates need, and the integration would silently lose entities in
    winter mode.
    """
    accessed: set[str] = set()

    class TrackingDict(dict):
        def get(self, key, default=None):
            accessed.add(key)
            return super().get(key, default)

    snapshot = TrackingDict()
    for predicate in _ALL_PREDICATES:
        predicate(snapshot)

    missing = accessed - set(CAPABILITY_KEYS)
    assert not missing, (
        f"CAPABILITY_KEYS is missing keys read by predicates: {sorted(missing)}"
    )


def test_all_public_capabilities_predicates_are_in_all():
    """Sanity guard: every is_*/has_* defined in the module surfaces via __all__."""
    public = {
        name
        for name in dir(capabilities)
        if name.startswith(("is_", "has_"))
        and callable(getattr(capabilities, name))
        and getattr(getattr(capabilities, name), "__module__", "")
        == capabilities.__name__
    }
    assert public.issubset(set(capabilities.__all__))
