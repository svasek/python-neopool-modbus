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

"""Smoke tests for the enumerations and layout mappings in registers.py.

The high-level client methods (``async_set_relay_state`` etc.) resolve
raw register addresses via the private ``_*_LAYOUT`` dicts. If a new
enum member is added but the layout dict is not extended, the client
would raise ``KeyError`` at runtime; these tests catch that at import
time by asserting every enum member has an entry in its layout.
"""

from __future__ import annotations

import pytest

from neopool_modbus.registers import (
    _BINARY_FLAG_LAYOUT,
    _BITMASK_FLAG_LAYOUT,
    _MASKED_FLAG_LAYOUT,
    _RELAY_LAYOUT,
    _RELAY_STATE_KEYS,
    _SETPOINT_LAYOUT,
    BinaryConfigFlag,
    BitmaskConfigFlag,
    MaskedFlag,
    RelayKind,
    RelayMode,
    SetpointKind,
    TimerRelayMode,
)


def test_relay_mode_values_match_timer_relay_mode() -> None:
    """RelayMode is the high-level surface for TimerRelayMode; values must agree.

    ``AUTO`` in the high-level API maps to ``ENABLED`` in the register-level
    enum (timer-driven mode). Manual states share the same numeric values.
    """
    assert RelayMode.AUTO == TimerRelayMode.ENABLED
    assert RelayMode.ALWAYS_ON == TimerRelayMode.ALWAYS_ON
    assert RelayMode.ALWAYS_OFF == TimerRelayMode.ALWAYS_OFF


@pytest.mark.parametrize("relay", list(RelayKind))
def test_relay_layout_covers_every_relay_kind(relay: RelayKind) -> None:
    """Every :class:`RelayKind` member must have a layout entry."""
    function_reg, timer_block_reg, function_code = _RELAY_LAYOUT[relay]
    assert function_reg > 0
    assert timer_block_reg > 0
    assert function_code > 0


@pytest.mark.parametrize("relay", list(RelayKind))
def test_relay_state_keys_covers_every_relay_kind(relay: RelayKind) -> None:
    """Every :class:`RelayKind` member must have an optimistic-key entry."""
    timer_key, runtime_key = _RELAY_STATE_KEYS[relay]
    assert timer_key.startswith("relay_") and timer_key.endswith("_enable")
    assert runtime_key


@pytest.mark.parametrize("flag", list(BinaryConfigFlag))
def test_binary_flag_layout_covers_every_flag(flag: BinaryConfigFlag) -> None:
    """Every :class:`BinaryConfigFlag` member must have a layout entry."""
    register, data_key = _BINARY_FLAG_LAYOUT[flag]
    assert register > 0
    assert data_key.startswith("MBF_")


@pytest.mark.parametrize("flag", list(BitmaskConfigFlag))
def test_bitmask_flag_layout_covers_every_flag(flag: BitmaskConfigFlag) -> None:
    """Every :class:`BitmaskConfigFlag` member must map to a non-zero bit."""
    assert _BITMASK_FLAG_LAYOUT[flag] > 0


@pytest.mark.parametrize("kind", list(SetpointKind))
def test_setpoint_layout_covers_every_kind(kind: SetpointKind) -> None:
    """Every :class:`SetpointKind` member must have a layout entry."""
    register, data_key = _SETPOINT_LAYOUT[kind]
    assert register > 0
    assert data_key.startswith("MBF_PAR_")


@pytest.mark.parametrize("flag", list(MaskedFlag))
def test_masked_flag_layout_covers_every_flag(flag: MaskedFlag) -> None:
    """Every :class:`MaskedFlag` member must have a layout entry with mask + shift."""
    register, mask, shift, data_key = _MASKED_FLAG_LAYOUT[flag]
    assert register > 0
    assert mask > 0
    assert shift >= 0
    assert data_key.startswith("MBF_PAR_")


def test_masked_flag_shift_and_mask_align() -> None:
    """Verify that mask / shift for each MaskedFlag together cover the expected bit range."""
    for flag in MaskedFlag:
        _, mask, shift, _ = _MASKED_FLAG_LAYOUT[flag]
        # A mask shifted right by shift must be contiguous (all 1s).
        shifted = mask >> shift
        # Contiguous 1s <=> (n & (n+1)) == 0 for the shifted mask starting at bit 0.
        assert shifted & (shifted + 1) == 0, (
            f"{flag.name}: mask 0x{mask:04X} >> {shift} = 0x{shifted:04X} is not contiguous"
        )
