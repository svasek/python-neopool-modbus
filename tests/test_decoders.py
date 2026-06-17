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

from neopool_modbus.decoders import (
    aggregate_filtration_remaining,
    build_timer_block,
    combine_u32,
    compute_filtration_speed_state,
    decode_cell_boost,
    decode_filtration_mode,
    decode_filtration_speed,
    decode_par_model_modules,
    derive_timer_stop,
    encode_cell_boost,
    encode_filtration_mode,
    encode_filtration_speed,
    generate_time_options,
    get_filtration_pump_type,
    get_machine_name,
    get_timer_interval,
    hhmm_to_seconds,
    is_hydrolysis_in_percent,
    modbus_regs_to_ascii,
    modbus_regs_to_hex_string,
    pad_list,
    parse_timer_block,
    parse_version,
    seconds_to_hhmm,
)


def test_parse_version():
    assert parse_version(0x0123) == "1.35"
    assert parse_version("invalid") == "?"


def test_pad_list():
    assert pad_list([1, 2], 5) == [1, 2, 0, 0, 0]
    assert pad_list([], 3, pad_value=7) == [7, 7, 7]


def test_modbus_regs_to_ascii():
    assert modbus_regs_to_ascii([0x4142, 0x4300]) == "ABC"
    assert modbus_regs_to_ascii([0x4100]) == "A"


def test_build_timer_block():
    d = {"enable": 1, "on": 60, "off": 120, "function": 3, "work_time": 30}
    regs = build_timer_block(d)
    assert isinstance(regs, list) and len(regs) == 15


def test_compute_filtration_speed_state_mid():
    d = {
        "MBF_RELAY_STATE": 0x0202,
        "MBF_PAR_FILTRATION_CONF": 0x0000,
        "Filtration Pump": True,
    }
    # relay_speed == 2 → mid
    assert compute_filtration_speed_state(d) == "mid"


def test_compute_filtration_speed_state_high():
    d = {
        "MBF_RELAY_STATE": 0x0402,
        "MBF_PAR_FILTRATION_CONF": 0x0000,
        "Filtration Pump": True,
    }
    # relay_speed == 4 → high
    assert compute_filtration_speed_state(d) == "high"


def test_compute_filtration_speed_state_conf_speed_0():
    d = {
        "MBF_RELAY_STATE": 0x0002,
        "MBF_PAR_FILTRATION_CONF": 0x0000,
        "Filtration Pump": True,
    }
    assert compute_filtration_speed_state(d) == "low"


def test_compute_filtration_speed_state_conf_speed_1():
    d = {
        "MBF_RELAY_STATE": 0x0002,
        "MBF_PAR_FILTRATION_CONF": 0x0010,
        "Filtration Pump": True,
    }
    assert compute_filtration_speed_state(d) == "mid"


def test_compute_filtration_speed_state_conf_speed_2():
    d = {
        "MBF_RELAY_STATE": 0x0002,
        "MBF_PAR_FILTRATION_CONF": 0x0020,
        "Filtration Pump": True,
    }
    assert compute_filtration_speed_state(d) == "high"


def test_compute_filtration_speed_state_relay_speed_1():
    d = {
        "MBF_RELAY_STATE": 0x0102,
        "MBF_PAR_FILTRATION_CONF": 0x0000,
        "Filtration Pump": True,
    }
    assert compute_filtration_speed_state(d) == "low"


@pytest.mark.parametrize(
    ("relay_state", "expected"),
    [
        (0x0302, "mid"),  # cumulative mid: bits 8+9 → relay_speed 0x03
        (0x0702, "high"),  # cumulative high: bits 8+9+10 → relay_speed 0x07
    ],
    ids=["cumulative-mid", "cumulative-high"],
)
def test_compute_filtration_speed_state_cumulative_encoding(relay_state, expected):
    """Controllers using cumulative (thermometer) speed bits (#152)."""
    d = {
        "MBF_RELAY_STATE": relay_state,
        "MBF_PAR_FILTRATION_CONF": 0x0020,  # conf says high - must be ignored
        "Filtration Pump": True,
    }
    assert compute_filtration_speed_state(d) == expected


@pytest.mark.parametrize("aux_bit", [0x0010, 0x0020, 0x0040])
def test_compute_filtration_speed_state_aux_bits_do_not_affect_speed(aux_bit):
    # filtration ON (0x0002), speed MID (0x0200), plus AUX relay bit set
    d = {
        "MBF_RELAY_STATE": 0x0202 | aux_bit,
        "MBF_PAR_FILTRATION_CONF": 0x0000,
        "Filtration Pump": True,
    }
    assert compute_filtration_speed_state(d) == "mid"


def test_compute_filtration_speed_state_no_match():
    d = {
        "MBF_RELAY_STATE": 0x0002,
        "MBF_PAR_FILTRATION_CONF": 0x00F0,
        "Filtration Pump": True,
    }
    # relay_speed == 0, conf_speed == 15 (not 0,1,2) → "off"
    assert compute_filtration_speed_state(d) == "off"


def test_compute_filtration_speed_state_none():
    # Empty dict: "Filtration Pump" is None (not yet decoded) → "off".
    assert compute_filtration_speed_state({}) == "off"


def test_compute_filtration_speed_state_pump_off():
    # "Filtration Pump" explicitly False → "off"
    assert compute_filtration_speed_state({"Filtration Pump": False}) == "off"


def test_get_filtration_pump_type():
    assert get_filtration_pump_type(0x0001) == 1


def test_hhmm_seconds_conversion():
    assert hhmm_to_seconds("01:30") == 5400
    assert seconds_to_hhmm(5400) == "01:30"


def test_parse_version_invalid():
    assert parse_version(None) == "?"
    assert parse_version("not-a-number") == "?"
    assert parse_version(0xFFFF) == "255.255"


def test_parse_version_with_zero():
    assert parse_version(0x0000) == "0.00"


def test_modbus_regs_to_ascii_empty():
    assert modbus_regs_to_ascii([]) == ""


def test_build_timer_block_with_missing_keys():
    # Missing work_time, function, etc.
    data = {"enable": 1, "on": 0, "off": 0}
    regs = build_timer_block(data)
    assert len(regs) == 15


def test_generate_time_options_default():
    """Test generate_time_options produces every 15 min option in a day."""
    opts = generate_time_options()
    assert len(opts) == 96  # 24h * 4 per hour
    assert opts[0] == "00:00"
    assert opts[-1] == "23:45"


def test_generate_time_options_step_30():
    """Test generate_time_options with 30-minute steps."""
    opts = generate_time_options(step_minutes=30)
    assert len(opts) == 48
    assert opts[0] == "00:00"
    assert opts[1] == "00:30"
    assert opts[-1] == "23:30"


def test_parse_timer_block_full():
    """Test parse_timer_block with a full list of 15 registers."""
    regs = list(range(1, 16))
    result = parse_timer_block(regs)
    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "enable",
        "on",
        "off",
        "period",
        "interval",
        "stop",
        "countdown",
        "function",
        "work_time",
    }
    # Example: on = u32(regs[1], regs[2]) == (regs[2] << 16) | regs[1]
    assert result["enable"] == 1
    assert result["on"] == (3 << 16) | 2
    # stop = (on + interval) % 86400
    on = (3 << 16) | 2
    interval = (9 << 16) | 8
    assert result["stop"] == (on + interval) % 86400


def test_parse_timer_block_short():
    """Test parse_timer_block pads missing registers with zeros."""
    regs = [1, 2, 3]  # Only first three
    result = parse_timer_block(regs)
    assert result["enable"] == 1
    assert result["on"] == (3 << 16) | 2  # padded msb=3
    assert result["off"] == 0
    # stop = (on + 0) % 86400; padded interval is 0, so stop is on mod day.
    assert result["stop"] == result["on"] % 86400
    assert len(result) == 9


def test_modbus_regs_to_hex_string_basic():
    """Test modbus_regs_to_hex_string converts list to hex string."""
    regs = [0x1234, 0xABCD, 0x0001]
    hexstr = modbus_regs_to_hex_string(regs)
    assert hexstr == "1234ABCD0001"


def test_modbus_regs_to_hex_string_empty():
    """Test modbus_regs_to_hex_string handles empty and invalid input."""
    assert modbus_regs_to_hex_string([]) == ""
    assert modbus_regs_to_hex_string(None) == ""
    assert modbus_regs_to_hex_string("notalist") == ""


def test_get_timer_interval_daytime():
    """Test get_timer_interval with stop >= start."""
    assert get_timer_interval(3600, 7200) == 3600  # 01:00 - 02:00


def test_get_timer_interval_overnight():
    """Test get_timer_interval with stop < start (over midnight)."""
    assert get_timer_interval(82800, 3600) == 3600 + (
        86400 - 82800
    )  # 23:00 - 01:00 = 2h


def test_get_timer_interval_zero():
    """Test get_timer_interval returns 0 if times are equal."""
    assert get_timer_interval(5000, 5000) == 0


def test_is_hydrolysis_in_percent_force_percentage_bit():
    """Test is_hydrolysis_in_percent when MBMSK_VS_FORCE_UNITS_PERCENTAGE bit is set."""
    data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x4000,  # bit 14 set
        "MBF_PAR_UICFG_MACHINE": 0,
    }
    assert is_hydrolysis_in_percent(data) is True


def test_is_hydrolysis_in_percent_force_grh_bit():
    """Test is_hydrolysis_in_percent when MBMSK_VS_FORCE_UNITS_GRH bit is set."""
    data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x2000,  # bit 13 set
        "MBF_PAR_UICFG_MACHINE": 0,
    }
    assert is_hydrolysis_in_percent(data) is False


def test_is_hydrolysis_in_percent_both_force_bits():
    """Test is_hydrolysis_in_percent when both force bits are set (percentage takes precedence)."""
    data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x6000,  # both bits 13 and 14 set
        "MBF_PAR_UICFG_MACHINE": 0,
    }
    assert is_hydrolysis_in_percent(data) is True


def test_is_hydrolysis_in_percent_hidrolife():
    """Test is_hydrolysis_in_percent for HIDROLIFE machine type."""
    data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x0000,  # no force bits
        "MBF_PAR_UICFG_MACHINE": 1,  # HIDROLIFE
    }
    assert is_hydrolysis_in_percent(data) is False


def test_is_hydrolysis_in_percent_bionet():
    """Test is_hydrolysis_in_percent for BIONET machine type."""
    data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x0000,  # no force bits
        "MBF_PAR_UICFG_MACHINE": 4,  # BIONET
    }
    assert is_hydrolysis_in_percent(data) is False


def test_is_hydrolysis_in_percent_generic_with_electrolisis():
    """Test is_hydrolysis_in_percent for GENERIC machine with ELECTROLISIS bit."""
    data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x8000,  # bit 15 (ELECTROLISIS) set
        "MBF_PAR_UICFG_MACHINE": 9,  # GENERIC
    }
    assert is_hydrolysis_in_percent(data) is False


def test_is_hydrolysis_in_percent_generic_without_electrolisis():
    """Test is_hydrolysis_in_percent for GENERIC machine without ELECTROLISIS bit."""
    data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x0000,  # no special bits
        "MBF_PAR_UICFG_MACHINE": 9,  # GENERIC
    }
    assert is_hydrolysis_in_percent(data) is True


def test_is_hydrolysis_in_percent_default_case():
    """Test is_hydrolysis_in_percent default case (returns True for other machine types)."""
    data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": 0x0000,
        "MBF_PAR_UICFG_MACHINE": 2,  # AQUASCENIC
    }
    assert is_hydrolysis_in_percent(data) is True


def test_is_hydrolysis_in_percent_empty_data():
    """Test is_hydrolysis_in_percent with empty data (defaults to True)."""
    data = {}
    assert is_hydrolysis_in_percent(data) is True


def test_is_hydrolysis_in_percent_missing_visual_style():
    """Test is_hydrolysis_in_percent with missing visual style (defaults based on machine)."""
    data = {
        "MBF_PAR_UICFG_MACHINE": 1,  # HIDROLIFE
    }
    assert is_hydrolysis_in_percent(data) is False


def test_is_hydrolysis_in_percent_none_values():
    """Test is_hydrolysis_in_percent when Modbus populates keys with None (get_safe IndexError)."""
    # Both keys present but explicitly None - must not raise TypeError
    data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": None,
        "MBF_PAR_UICFG_MACHINE": None,
    }
    assert is_hydrolysis_in_percent(data) is True  # falls through to default True

    # Only visual_style is None, machine is HIDROLIFE → g/h
    data = {
        "MBF_PAR_UICFG_MACH_VISUAL_STYLE": None,
        "MBF_PAR_UICFG_MACHINE": 1,  # HIDROLIFE
    }
    assert is_hydrolysis_in_percent(data) is False


@pytest.mark.parametrize(
    "machine_type, expected",
    [
        (0, ""),  # MBV_PAR_MACH_NONE → no machine assigned
        (1, "Hidrolife"),
        (2, "Aquascenic"),
        (3, "Oxilife"),
        (4, "Bionet"),
        (5, "Hidroniser"),
        (6, "UVScenic"),
        (7, "Station"),
        (8, "Brilix"),
        (9, "Generic"),  # GENERIC but no custom name → fallback
        (10, "Bayrol"),
        (11, "Hay"),
    ],
)
def test_get_machine_name_known_types(machine_type, expected):
    """All 12 known machine types return their brand name."""
    data = {"MBF_PAR_UICFG_MACHINE": machine_type}
    assert get_machine_name(data) == expected


def test_get_machine_name_unknown_type():
    """Out-of-range value returns empty string."""
    assert get_machine_name({"MBF_PAR_UICFG_MACHINE": 99}) == ""
    assert get_machine_name({"MBF_PAR_UICFG_MACHINE": 12}) == ""


def test_get_machine_name_empty_data():
    """Missing key defaults to 0 → empty string (no machine assigned)."""
    assert get_machine_name({}) == ""


def test_get_machine_name_none_value():
    """Explicit None value defaults to 0 → empty string (no machine assigned)."""
    assert get_machine_name({"MBF_PAR_UICFG_MACHINE": None}) == ""


def test_get_machine_name_generic_with_custom_name():
    """GENERIC (9) with both name parts returns 'bold light'."""
    data = {
        "MBF_PAR_UICFG_MACHINE": 9,
        "MBF_PAR_UICFG_MACH_NAME_BOLD": "vista",
        "MBF_PAR_UICFG_MACH_NAME_LIGHT": "pool",
    }
    assert get_machine_name(data) == "vista pool"


def test_get_machine_name_generic_bold_only():
    """GENERIC with only bold part returns just that string."""
    data = {
        "MBF_PAR_UICFG_MACHINE": 9,
        "MBF_PAR_UICFG_MACH_NAME_BOLD": "aqua",
        "MBF_PAR_UICFG_MACH_NAME_LIGHT": "",
    }
    assert get_machine_name(data) == "aqua"


def test_get_machine_name_generic_light_only():
    """GENERIC with only light part returns just that string."""
    data = {
        "MBF_PAR_UICFG_MACHINE": 9,
        "MBF_PAR_UICFG_MACH_NAME_BOLD": None,
        "MBF_PAR_UICFG_MACH_NAME_LIGHT": "scenic",
    }
    assert get_machine_name(data) == "scenic"


def test_get_machine_name_generic_empty_custom_name():
    """GENERIC with both name parts empty/None falls back to 'Generic'."""
    data = {
        "MBF_PAR_UICFG_MACHINE": 9,
        "MBF_PAR_UICFG_MACH_NAME_BOLD": "",
        "MBF_PAR_UICFG_MACH_NAME_LIGHT": None,
    }
    assert get_machine_name(data) == "Generic"


def test_get_machine_name_generic_whitespace_name():
    """GENERIC with only whitespace in name parts falls back to 'Generic'."""
    data = {
        "MBF_PAR_UICFG_MACHINE": 9,
        "MBF_PAR_UICFG_MACH_NAME_BOLD": "   ",
        "MBF_PAR_UICFG_MACH_NAME_LIGHT": "   ",
    }
    assert get_machine_name(data) == "Generic"


def test_get_machine_name_non_generic_ignores_custom_name():
    """Non-GENERIC machine type ignores name registers."""
    data = {
        "MBF_PAR_UICFG_MACHINE": 11,  # Hay
        "MBF_PAR_UICFG_MACH_NAME_BOLD": "something",
        "MBF_PAR_UICFG_MACH_NAME_LIGHT": "else",
    }
    assert get_machine_name(data) == "Hay"


# ---------------------------------------------------------------------------
# combine_u32
# ---------------------------------------------------------------------------


def test_combine_u32_combines_low_and_high_words():
    """combine_u32 returns (high << 16) | low."""
    assert combine_u32(0x1234, 0x5678) == 0x56781234


def test_combine_u32_handles_zero_values():
    """Both halves at 0 -> 0; not None."""
    assert combine_u32(0, 0) == 0


def test_combine_u32_handles_max_32bit():
    """0xFFFF / 0xFFFF -> 0xFFFFFFFF (full 32-bit range)."""
    assert combine_u32(0xFFFF, 0xFFFF) == 0xFFFFFFFF


@pytest.mark.parametrize(
    ("low", "high"),
    [
        (None, None),
        (1, None),
        (None, 1),
    ],
)
def test_combine_u32_missing_or_none_returns_none(low, high):
    """Either half being None yields None."""
    assert combine_u32(low, high) is None


# ---------------------------------------------------------------------------
# decode_par_model_modules
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("bitmask", "expected"),
    [
        (0x0001, ["ionization"]),
        (0x0002, ["hydrolysis"]),
        (0x0004, ["uv_lamp"]),
        (0x0008, ["salinity"]),
        (0x000F, ["ionization", "hydrolysis", "uv_lamp", "salinity"]),
        (0x000A, ["hydrolysis", "salinity"]),
        (0x0000, []),
        (None, []),
        # Unknown bits above the documented mask must not introduce phantom names.
        (0x0010, []),
    ],
)
def test_decode_par_model_modules(bitmask, expected):
    assert decode_par_model_modules(bitmask) == expected


# ---------------------------------------------------------------------------
# filtration_mode codec
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("reg_val", "expected"),
    [
        (0, "manual"),
        (1, "auto"),
        (2, "heating"),
        (3, "smart"),
        (4, "intelligent"),
        (13, "backwash"),
        (None, None),
        (5, None),
        (99, None),
    ],
)
def test_decode_filtration_mode(reg_val, expected):
    assert decode_filtration_mode(reg_val) == expected


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("manual", 0),
        ("auto", 1),
        ("heating", 2),
        ("smart", 3),
        ("intelligent", 4),
        ("backwash", 13),
    ],
)
def test_encode_filtration_mode(name, expected):
    assert encode_filtration_mode(name) == expected


def test_encode_filtration_mode_rejects_unknown():
    with pytest.raises(ValueError, match="unknown filtration mode"):
        encode_filtration_mode("nonsense")


# ---------------------------------------------------------------------------
# cell_boost codec
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("reg_val", "expected"),
    [
        (0x0000, "inactive"),
        (0x85A0, "active"),
        (0x05A0, "active_with_redox"),
        # any value with bit 0x8000 set decodes as "active" (no-redox variant)
        (0x8000, "active"),
        (0x8001, "active"),
        # missing input returns None
        (None, None),
        # unrecognised non-zero pattern returns None
        (0x0100, None),
    ],
)
def test_decode_cell_boost(reg_val, expected):
    assert decode_cell_boost(reg_val) == expected


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("inactive", 0),
        ("active", 0x85A0),
        ("active_with_redox", 0x05A0),
    ],
)
def test_encode_cell_boost(name, expected):
    assert encode_cell_boost(name) == expected


def test_encode_cell_boost_rejects_unknown():
    with pytest.raises(ValueError, match="unknown cell-boost mode"):
        encode_cell_boost("foo")


def test_cell_boost_round_trip():
    """encode -> decode round trips for every public mode."""
    for name in ("inactive", "active", "active_with_redox"):
        assert decode_cell_boost(encode_cell_boost(name)) == name


# ---------------------------------------------------------------------------
# filtration_speed codec
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("idx", "expected"),
    [
        (0, "low"),
        (1, "mid"),
        (2, "high"),
        (None, None),
        (3, None),
    ],
)
def test_decode_filtration_speed(idx, expected):
    assert decode_filtration_speed(idx) == expected


@pytest.mark.parametrize(
    ("name", "expected"),
    [("low", 0), ("mid", 1), ("high", 2)],
)
def test_encode_filtration_speed(name, expected):
    assert encode_filtration_speed(name) == expected


def test_encode_filtration_speed_rejects_off():
    """``off`` is not encodable -- it lives in filt_mode / manual_state."""
    with pytest.raises(ValueError, match="unknown filtration speed"):
        encode_filtration_speed("off")


def test_encode_filtration_speed_rejects_unknown():
    with pytest.raises(ValueError, match="unknown filtration speed"):
        encode_filtration_speed("turbo")


# ---------------------------------------------------------------------------
# derive_timer_stop
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("on", "interval", "expected"),
    [
        # Same-day stop
        (3600, 7200, 10800),
        # Stop at midnight wraps cleanly to 0 (the modulo)
        (86000, 400, 0),
        # Over-midnight wrap: 85000 + 5000 = 90000 -> 90000 - 86400 = 3600
        (85000, 5000, 3600),
        # Boundary: zero interval keeps the start time
        (3600, 0, 3600),
        # Either input missing -> None
        (None, 100, None),
        (100, None, None),
        (None, None, None),
    ],
)
def test_derive_timer_stop(on, interval, expected):
    assert derive_timer_stop(on, interval) == expected


# ---------------------------------------------------------------------------
# aggregate_filtration_remaining
# ---------------------------------------------------------------------------


def test_aggregate_filtration_remaining_returns_largest_positive():
    """The aggregate is the max of the three positive countdowns."""
    data = {
        "filtration1_countdown": 1200,
        "filtration2_countdown": 3600,
        "filtration3_countdown": 600,
    }
    assert aggregate_filtration_remaining(data) == 3600


def test_aggregate_filtration_remaining_ignores_non_positive():
    """Zero, negative or missing countdowns are ignored."""
    data = {
        "filtration1_countdown": 0,
        "filtration2_countdown": 1500,
        # filtration3_countdown missing
    }
    assert aggregate_filtration_remaining(data) == 1500


def test_aggregate_filtration_remaining_all_inactive_returns_none():
    """No active timers -> None (so the integration knows there is no remaining time)."""
    data = {
        "filtration1_countdown": 0,
        "filtration2_countdown": None,
        "filtration3_countdown": -1,
    }
    assert aggregate_filtration_remaining(data) is None


def test_aggregate_filtration_remaining_empty_data_returns_none():
    assert aggregate_filtration_remaining({}) is None


def test_aggregate_filtration_remaining_ignores_other_keys():
    """Keys outside the three filtration timers must not contribute."""
    data = {
        "filtration1_countdown": 100,
        "filtration4_countdown": 9999,  # nonexistent timer index
        "relay_aux1_countdown": 9999,
    }
    assert aggregate_filtration_remaining(data) == 100
