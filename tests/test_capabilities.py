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

from neopool_modbus.capabilities import (
    is_chlorine_module_present,
    is_conductivity_module_present,
    is_hydrolysis_present,
    is_ionization_present,
    is_ph_module_present,
    is_redox_module_present,
    is_salinity_module_present,
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
