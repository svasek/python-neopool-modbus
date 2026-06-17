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

"""Pure decoders, encoders and computations for NeoPool register values.

These helpers translate raw Modbus register values to Python types and back.
They have no I/O, no Home Assistant dependencies, and no global state.
"""

from __future__ import annotations

from typing import Any


def parse_version(val: int | str | None) -> str:
    """Parse version from integer or string."""
    if isinstance(val, int):
        major = (val >> 8) & 0xFF
        minor = val & 0xFF
        return f"{major}.{minor:02d}"
    return "?"


def combine_u32(low: int | None, high: int | None) -> int | None:
    """Return ``(high << 16) | low``, or ``None`` if either half is missing."""
    if low is None or high is None:
        return None
    return (int(high) << 16) | int(low)


# MBF_PAR_MODEL bitmask -- which optional modules the controller has installed.
_MBMSK_MODEL_ION = 0x0001
_MBMSK_MODEL_HIDROLYSIS = 0x0002
_MBMSK_MODEL_UV = 0x0004
_MBMSK_MODEL_SALINITY = 0x0008

_PAR_MODEL_MODULES: tuple[tuple[int, str], ...] = (
    (_MBMSK_MODEL_ION, "ionization"),
    (_MBMSK_MODEL_HIDROLYSIS, "hydrolysis"),
    (_MBMSK_MODEL_UV, "uv_lamp"),
    (_MBMSK_MODEL_SALINITY, "salinity"),
)


def decode_par_model_modules(bitmask: int | None) -> list[str]:
    """Return the optional modules encoded in MBF_PAR_MODEL, ordered by bit."""
    if bitmask is None:
        return []
    return [name for mask, name in _PAR_MODEL_MODULES if bitmask & mask]


# MBF_PAR_FILT_MODE values (wire protocol).
_FILTRATION_MODES: dict[int, str] = {
    0: "manual",
    1: "auto",
    2: "heating",
    3: "smart",
    4: "intelligent",
    13: "backwash",
}
_FILTRATION_MODE_VALUES: dict[str, int] = {v: k for k, v in _FILTRATION_MODES.items()}


def decode_filtration_mode(reg_val: int | None) -> str | None:
    """Return the filtration-mode name for *reg_val*, or ``None`` if unknown."""
    if reg_val is None:
        return None
    return _FILTRATION_MODES.get(int(reg_val))


def encode_filtration_mode(name: str) -> int:
    """Return the wire value for a filtration-mode *name*.

    Raises :class:`ValueError` if *name* is not one of the known modes.
    """
    try:
        return _FILTRATION_MODE_VALUES[name]
    except KeyError:
        raise ValueError(
            f"unknown filtration mode {name!r}; "
            f"expected one of {sorted(_FILTRATION_MODE_VALUES)}"
        ) from None


# MBF_CELL_BOOST composite register bits.
_MBMSK_CELL_BOOST_ACTIVE = 0x05A0  # boost active pattern
_MBMSK_CELL_BOOST_NO_REDOX = 0x8000  # disables redox-driven dosing while active

_CELL_BOOST_MODES: tuple[str, ...] = ("inactive", "active", "active_with_redox")


def decode_cell_boost(reg_val: int | None) -> str | None:
    """Return the cell-boost mode for *reg_val*, or ``None`` if unrecognised."""
    if reg_val is None:
        return None
    val = int(reg_val)
    if val == 0:
        return "inactive"
    if val & _MBMSK_CELL_BOOST_NO_REDOX:
        return "active"
    if (val & _MBMSK_CELL_BOOST_ACTIVE) == _MBMSK_CELL_BOOST_ACTIVE:
        return "active_with_redox"
    return None


def encode_cell_boost(name: str) -> int:
    """Return the wire value for a cell-boost *name*.

    Raises :class:`ValueError` if *name* is not one of ``inactive``,
    ``active`` or ``active_with_redox``.
    """
    if name == "inactive":
        return 0
    if name == "active":
        return _MBMSK_CELL_BOOST_ACTIVE | _MBMSK_CELL_BOOST_NO_REDOX
    if name == "active_with_redox":
        return _MBMSK_CELL_BOOST_ACTIVE
    raise ValueError(
        f"unknown cell-boost mode {name!r}; expected one of {list(_CELL_BOOST_MODES)}"
    )


# Filtration-speed indices map to bits 4-6 of MBF_PAR_FILTRATION_CONF.
# "Off" is not a value of these bits -- it is signalled by the filtration
# mode register or the manual filtration-state register, and must be set
# through those, not via this codec.
_FILTRATION_SPEEDS: dict[int, str] = {0: "low", 1: "mid", 2: "high"}
_FILTRATION_SPEED_VALUES: dict[str, int] = {v: k for k, v in _FILTRATION_SPEEDS.items()}


def decode_filtration_speed(idx: int | None) -> str | None:
    """Return the filtration-speed name for *idx*, or ``None`` if unknown."""
    if idx is None:
        return None
    return _FILTRATION_SPEEDS.get(int(idx))


def encode_filtration_speed(name: str) -> int:
    """Return the speed index for *name*.

    Raises :class:`ValueError` if *name* is not one of ``low``, ``mid``
    or ``high``.
    """
    try:
        return _FILTRATION_SPEED_VALUES[name]
    except KeyError:
        raise ValueError(
            f"unknown filtration speed {name!r}; "
            f"expected one of {sorted(_FILTRATION_SPEED_VALUES)}"
        ) from None


_SECONDS_PER_DAY = 86400


def derive_timer_stop(on: int | None, interval: int | None) -> int | None:
    """Return ``(on + interval) % 86400``, or ``None`` if either input is missing."""
    if on is None or interval is None:
        return None
    return (int(on) + int(interval)) % _SECONDS_PER_DAY


def aggregate_filtration_remaining(data: dict[str, Any]) -> int | None:
    """Return the largest positive ``filtration{1,2,3}_countdown`` in *data*.

    Returns ``None`` when none of the three filtration timers reports a
    positive countdown.
    """
    remaining: int | None = None
    for n in (1, 2, 3):
        cd = data.get(f"filtration{n}_countdown")
        if cd is not None and cd > 0:
            remaining = max(remaining or 0, int(cd))
    return remaining


def modbus_regs_to_ascii(regs: list[int]) -> str:
    """Convert list of uint16 Modbus registers to ASCII string (ASCIIZ, max 10 chars)."""
    chars: list[str] = []
    for reg in regs:
        # High byte (1st char)
        high = (reg >> 8) & 0xFF
        # Low byte (2nd char)
        low = reg & 0xFF
        if high != 0:
            chars.append(chr(high))
        else:  # pragma: no cover
            break
        if low != 0:
            chars.append(chr(low))
        else:
            break
    return "".join(chars)


def modbus_regs_to_hex_string(regs: list[int] | None) -> str:
    """Return Modbus registers as hex string."""
    # The defensive isinstance check guards against callers passing non-list
    # values via dynamic dict.get() lookups in HA integration code.
    if not regs or not isinstance(regs, list):  # pyright: ignore[reportUnnecessaryIsInstance]
        return ""
    return "".join(f"{reg:04X}" for reg in regs)


def parse_timer_block(regs: list[int]) -> dict[str, Any]:
    """Convert 15 Modbus registers to dict of timer params."""
    # Pads the regs list to length 15 with zeros if needed
    padded = pad_list(regs, 15)

    def u32(lsb: int, msb: int) -> int:
        return (msb << 16) | lsb

    return {
        "enable": padded[0],
        "on": u32(padded[1], padded[2]),
        "off": u32(padded[3], padded[4]),
        "period": u32(padded[5], padded[6]),
        "interval": u32(padded[7], padded[8]),
        "countdown": u32(padded[9], padded[10]),
        "function": padded[11],
        "work_time": u32(padded[13], padded[14]),
    }


def build_timer_block(data: dict[str, Any]) -> list[int]:
    """Convert dict of timer params to 15 Modbus registers (all as int, never None)."""

    def safe_int(val: Any) -> int:
        try:
            return int(val)
        except (TypeError, ValueError):  # pragma: no cover
            return 0

    def split_u32(val: Any) -> list[int]:
        v = safe_int(val)
        return [v & 0xFFFF, (v >> 16) & 0xFFFF]

    return [
        safe_int(data.get("enable", 0)),
        *split_u32(data.get("on", 0)),
        *split_u32(data.get("off", 0)),
        *split_u32(data.get("period", 0)),
        *split_u32(data.get("interval", 0)),
        *split_u32(data.get("countdown", 0)),
        safe_int(data.get("function", 0)),
        0,
        *split_u32(data.get("work_time", 0)),
    ]


def hhmm_to_seconds(hhmm: str) -> int:
    """Convert HH:MM string to seconds since midnight."""
    h, m = map(int, hhmm.split(":"))
    return h * 3600 + m * 60


def seconds_to_hhmm(seconds: int) -> str:
    """Convert seconds since midnight to HH:MM string."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h:02d}:{m:02d}"


def get_timer_interval(start_sec: int, stop_sec: int) -> int:
    """Calculate interval in seconds, handle over-midnight."""
    if stop_sec >= start_sec:
        return stop_sec - start_sec
    else:
        # over-midnight
        return (86400 - start_sec) + stop_sec


def generate_time_options(step_minutes: int = 15) -> list[str]:
    """Generate a list of HH:MM strings for every step_minutes in a day."""
    options: list[str] = []
    for mins in range(0, 24 * 60, step_minutes):
        h = mins // 60
        m = mins % 60
        options.append(f"{h:02d}:{m:02d}")
    return options


def get_filtration_speed(data: dict[str, Any]) -> int:
    """Get filtration speed based on relay state and configuration."""
    relay_state = data.get("MBF_RELAY_STATE", 0)
    # Use the dynamically decoded "Filtration Pump" key (set via GPIO mapping).
    # Only report a speed when the pump is explicitly on; treat both False
    # (pump off) and None (key not yet decoded / GPIO not assigned) as off.
    if data.get("Filtration Pump") is not True:
        return 0  # Filtration is off or unknown

    par_filtration_conf = data.get("MBF_PAR_FILTRATION_CONF", 0)
    relay_speed = (relay_state & 0x0700) >> 8
    # Check highest bit set - supports both individual-bit (1/2/4)
    # and cumulative encodings (1/3/7) used by some controllers.
    if relay_speed & 0x04:
        return 3  # High
    elif relay_speed & 0x02:
        return 2  # Mid
    elif relay_speed & 0x01:
        return 1  # Low

    conf_speed = (par_filtration_conf & 0x0070) >> 4
    # Preserved as if/elif chain for 1:1 port from the HA integration; refactor
    # to dict lookup is tracked separately.
    if conf_speed == 0:  # noqa: SIM116
        return 1
    elif conf_speed == 1:
        return 2
    elif conf_speed == 2:
        return 3
    return 0


def get_filtration_pump_type(par_filtration_conf: int) -> int:
    """Return the type of filtration pump based on configuration."""
    # 0 = standard, 1/2 = variable speed
    return (par_filtration_conf & 0x000F) >> 0


def pad_list(regs: list[int], length: int, pad_value: int = 0) -> list[int]:
    """Return a list padded with pad_value to desired length."""
    return regs + [pad_value] * (length - len(regs))


# Machine type index -> brand name (matches kNeoPoolMachineNames[] in Tasmota)
_MACHINE_NAMES = [
    "None",  # 0  MBV_PAR_MACH_NONE
    "Hidrolife",  # 1  MBV_PAR_MACH_HIDROLIFE
    "Aquascenic",  # 2  MBV_PAR_MACH_AQUASCENIC
    "Oxilife",  # 3  MBV_PAR_MACH_OXILIFE
    "Bionet",  # 4  MBV_PAR_MACH_BIONET
    "Hidroniser",  # 5  MBV_PAR_MACH_HIDRONISER
    "UVScenic",  # 6  MBV_PAR_MACH_UVSCENIC
    "Station",  # 7  MBV_PAR_MACH_STATION
    "Brilix",  # 8  MBV_PAR_MACH_BRILIX
    "Generic",  # 9  MBV_PAR_MACH_GENERIC
    "Bayrol",  # 10 MBV_PAR_MACH_BAYROL
    "Hay",  # 11 MBV_PAR_MACH_HAY
]
_MBV_PAR_MACH_GENERIC = 9


def get_machine_name(data: dict[str, Any]) -> str:
    """Return the human-readable machine/brand name.

    For GENERIC (9): assembles the custom name from the BOLD + LIGHT name registers
    stored in MBF_PAR_UICFG_MACH_NAME_BOLD / MBF_PAR_UICFG_MACH_NAME_LIGHT.
    If the custom name is empty, falls back to "Generic".
    """
    machine_type = int(data.get("MBF_PAR_UICFG_MACHINE") or 0)

    if machine_type == _MBV_PAR_MACH_GENERIC:
        bold = (data.get("MBF_PAR_UICFG_MACH_NAME_BOLD") or "").strip()
        light = (data.get("MBF_PAR_UICFG_MACH_NAME_LIGHT") or "").strip()
        custom_name = " ".join(filter(None, [bold, light]))
        if custom_name:
            return custom_name

    if 0 < machine_type < len(_MACHINE_NAMES):
        return _MACHINE_NAMES[machine_type]
    return ""  # 0 = no machine assigned, or unknown type


def is_hydrolysis_in_percent(data: dict[str, Any]) -> bool:
    """Determine if hydrolysis/electrolysis units are displayed as percentage or g/h.

    Based on Tasmota NeoPoolIsHydrolysisInPercent() logic:
    1. If MBMSK_VS_FORCE_UNITS_PERCENTAGE bit is set, "%" is displayed
    2. If MBMSK_VS_FORCE_UNITS_GRH bit is set, "g/h" is displayed
    3. If neither bit is set:
       a. If machine is HIDROLIFE or BIONET, then "g/h" is displayed
       b. If machine is GENERIC and MBMSK_ELECTROLISIS bit is set, "g/h" is displayed
       c. Otherwise "%" is displayed
    """
    # Bit masks for MBF_PAR_UICFG_MACH_VISUAL_STYLE register
    MBMSK_VS_FORCE_UNITS_GRH = 0x2000  # bit 13
    MBMSK_VS_FORCE_UNITS_PERCENTAGE = 0x4000  # bit 14
    MBMSK_ELECTROLISIS = 0x8000  # bit 15

    # Machine type values for MBF_PAR_UICFG_MACHINE register
    MBV_PAR_MACH_HIDROLIFE = 1
    MBV_PAR_MACH_BIONET = 4
    MBV_PAR_MACH_GENERIC = 9

    visual_style = int(data.get("MBF_PAR_UICFG_MACH_VISUAL_STYLE") or 0)
    machine_type = int(data.get("MBF_PAR_UICFG_MACHINE") or 0)

    # 1. If MBMSK_VS_FORCE_UNITS_PERCENTAGE bit is set, "%" is displayed
    if visual_style & MBMSK_VS_FORCE_UNITS_PERCENTAGE:
        return True

    # 2. If MBMSK_VS_FORCE_UNITS_GRH bit is set, "g/h" is displayed
    if visual_style & MBMSK_VS_FORCE_UNITS_GRH:
        return False

    # 3. If neither of the above bits is set:
    # a. If machine is HIDROLIFE or BIONET, then "g/h" is displayed
    if machine_type in (MBV_PAR_MACH_HIDROLIFE, MBV_PAR_MACH_BIONET):
        return False

    # b. If machine is GENERIC and MBMSK_ELECTROLISIS bit is set, "g/h" is displayed
    # c. Otherwise "%" is displayed
    if machine_type == MBV_PAR_MACH_GENERIC and (visual_style & MBMSK_ELECTROLISIS):  # noqa: SIM103
        return False
    return True


__all__ = [
    "aggregate_filtration_remaining",
    "build_timer_block",
    "combine_u32",
    "decode_cell_boost",
    "decode_filtration_mode",
    "decode_filtration_speed",
    "decode_par_model_modules",
    "derive_timer_stop",
    "encode_cell_boost",
    "encode_filtration_mode",
    "encode_filtration_speed",
    "generate_time_options",
    "get_filtration_pump_type",
    "get_filtration_speed",
    "get_machine_name",
    "get_timer_interval",
    "hhmm_to_seconds",
    "is_hydrolysis_in_percent",
    "modbus_regs_to_ascii",
    "modbus_regs_to_hex_string",
    "pad_list",
    "parse_timer_block",
    "parse_version",
    "seconds_to_hhmm",
]
