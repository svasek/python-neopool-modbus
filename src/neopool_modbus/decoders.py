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

from datetime import UTC, datetime, timedelta, tzinfo
from typing import Any


def parse_version(val: int | str | None) -> str:
    """Parse version from integer or string."""
    if isinstance(val, int):
        major = (val >> 8) & 0xFF
        minor = val & 0xFF
        return f"{major}.{minor:02d}"
    return "?"


def parse_register_int(raw: object) -> int:
    """Parse a Modbus register value from an ``int`` or a decimal/hex ``str``.

    Accepts:

    - ``int`` in the range ``0..0xFFFF``.
    - ``str`` in decimal (``"1539"``) or hex-prefixed (``"0x0603"``, ``"0X603"``).
      Whitespace is not stripped; the caller is responsible for normalisation.

    Rejects (raises :class:`ValueError`):

    - ``bool``: even though ``isinstance(True, int)`` is ``True`` in Python,
      it is almost never what a caller means when parsing a register value.
    - ``float``: silent truncation would lose information; reject explicitly.
    - Any other type, or a value outside ``0..0xFFFF``.

    Callers that need domain-specific error translation (e.g. a Home Assistant
    ``ServiceValidationError``) should catch :class:`ValueError` and re-raise.
    """
    if isinstance(raw, bool):
        raise ValueError(f"register value must not be a bool: {raw!r}")
    if isinstance(raw, float):
        raise ValueError(f"register value must not be a float: {raw!r}")
    if isinstance(raw, str):
        try:
            val = int(raw, 0)
        except ValueError as err:
            raise ValueError(f"cannot parse register value: {raw!r}") from err
    elif isinstance(raw, int):
        val = raw
    else:
        raise ValueError(f"unsupported register value type: {type(raw).__name__}")
    if not 0 <= val <= 0xFFFF:
        raise ValueError(f"register value out of range 0..0xFFFF: {val}")
    return val


def calculate_next_interval_time(
    seconds: float | None, *, now: datetime | None = None
) -> datetime | None:
    """Return the UTC timestamp for the next interval start, truncated to the minute.

    ``seconds`` is the offset from ``now`` (or the current UTC time when ``now``
    is ``None``). ``None`` or non-positive values return ``None``, matching how
    the NeoPool firmware encodes "no next interval scheduled".

    The returned datetime has ``second=0`` and ``microsecond=0`` so consumers
    can render or compare it without dealing with sub-minute jitter that would
    otherwise change on every poll. Callers who need sub-minute precision
    should compute the offset themselves.

    Pass ``now`` (must be timezone-aware) to inject a fixed reference time,
    typically for testing without freezing the clock.
    """
    if not seconds or seconds <= 0:
        return None
    reference = now if now is not None else datetime.now(UTC)
    target = reference + timedelta(seconds=seconds)
    return target.replace(second=0, microsecond=0)


def decode_device_time(unix_ts: int | None, tz: tzinfo) -> datetime | None:
    """Decode ``MBF_PAR_TIME`` to a timezone-aware UTC datetime.

    The NeoPool firmware has no timezone concept. It stores the value in
    ``MBF_PAR_TIME`` as seconds since the Unix epoch, but interprets that
    number as *wall-clock time in the local timezone* rather than as a real
    Unix timestamp. Callers pass the target timezone (typically the user's
    Home Assistant timezone); the return value is normalised to UTC so that
    downstream code can compare it against ``datetime.now(UTC)`` without
    special-casing the device's TZ-less encoding.

    Returns ``None`` when the register is absent (``unix_ts is None``).
    """
    if unix_ts is None:
        return None
    # Intentionally naive: the device stores the value as if it were UTC seconds,
    # but the digits themselves represent the wall-clock in ``tz``. The naive
    # datetime is then re-labelled with ``tz`` (not converted) and normalised
    # to UTC. See docstring above.
    dt_naive = datetime(1970, 1, 1) + timedelta(seconds=unix_ts)  # noqa: DTZ001
    dt_local = dt_naive.replace(tzinfo=tz)
    return dt_local.astimezone(UTC)


def encode_device_time(now: datetime) -> int:
    """Encode a timezone-aware datetime as a ``MBF_PAR_TIME`` register value.

    The inverse of :func:`decode_device_time`. Given a timezone-aware
    reference datetime, return the seconds-since-1970 value the device
    expects, so that after the write the device displays the correct
    wall-clock time in the same timezone as ``now``.

    Raises :class:`ValueError` when ``now`` is naive (no ``tzinfo``); a naive
    subtraction against a tz-aware epoch would otherwise fail with a
    :class:`TypeError` at runtime.
    """
    if now.tzinfo is None:
        raise ValueError("device time must be timezone-aware")
    epoch_local = datetime(1970, 1, 1, tzinfo=now.tzinfo)
    return int((now - epoch_local).total_seconds())


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
FILTRATION_MODE_LABELS: dict[int, str] = {
    0: "manual",
    1: "auto",
    2: "heating",
    3: "smart",
    4: "intelligent",
    13: "backwash",
}
_FILTRATION_MODE_VALUES: dict[str, int] = {
    v: k for k, v in FILTRATION_MODE_LABELS.items()
}


def decode_filtration_mode(reg_val: int | None) -> str | None:
    """Return the filtration-mode name for *reg_val*, or ``None`` if unknown."""
    if reg_val is None:
        return None
    return FILTRATION_MODE_LABELS.get(int(reg_val))


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

CELL_BOOST_MODE_LABELS: dict[int, str] = {
    0: "inactive",
    1: "active",
    2: "active_redox",
}


def decode_cell_boost(reg_val: int | None) -> str | None:
    """Return the cell-boost mode for *reg_val*, or ``None`` if unrecognised."""
    if reg_val is None:
        return None
    val = int(reg_val)
    if val == 0:
        return CELL_BOOST_MODE_LABELS[0]
    if val & _MBMSK_CELL_BOOST_NO_REDOX:
        return CELL_BOOST_MODE_LABELS[1]
    if (val & _MBMSK_CELL_BOOST_ACTIVE) == _MBMSK_CELL_BOOST_ACTIVE:
        return CELL_BOOST_MODE_LABELS[2]
    return None


def encode_cell_boost(name: str) -> int:
    """Return the wire value for a cell-boost *name*.

    Raises :class:`ValueError` if *name* is not one of ``inactive``,
    ``active`` or ``active_redox``.
    """
    if name == CELL_BOOST_MODE_LABELS[0]:
        return 0
    if name == CELL_BOOST_MODE_LABELS[1]:
        return _MBMSK_CELL_BOOST_ACTIVE | _MBMSK_CELL_BOOST_NO_REDOX
    if name == CELL_BOOST_MODE_LABELS[2]:
        return _MBMSK_CELL_BOOST_ACTIVE
    raise ValueError(
        f"unknown cell-boost mode {name!r}; "
        f"expected one of {list(CELL_BOOST_MODE_LABELS.values())}"
    )


# Filtration-speed indices map to bits 4-6 of MBF_PAR_FILTRATION_CONF.
# "Off" is not a value of these bits -- it is signalled by the filtration
# mode register or the manual filtration-state register, and must be set
# through those, not via this codec.
FILTRATION_SPEED_LABELS: dict[int, str] = {0: "low", 1: "mid", 2: "high"}
_FILTRATION_SPEED_VALUES: dict[str, int] = {
    v: k for k, v in FILTRATION_SPEED_LABELS.items()
}


def decode_filtration_speed(idx: int | None) -> str | None:
    """Return the filtration-speed name for *idx*, or ``None`` if unknown."""
    if idx is None:
        return None
    return FILTRATION_SPEED_LABELS.get(int(idx))


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


# MBF_PAR_FILTVALVE_MODE values exposed by the integration.
# The controller also supports 0 (disabled) and 2 (auto_linked), but
# those states are internal and not selectable through the standard UI,
# so this codec deliberately covers only the user-facing subset.
FILTVALVE_MODE_LABELS: dict[int, str] = {
    1: "enabled",
    3: "always_on",
    4: "always_off",
}
_FILTVALVE_MODE_VALUES: dict[str, int] = {
    v: k for k, v in FILTVALVE_MODE_LABELS.items()
}


def decode_filtvalve_mode(reg_val: int | None) -> str | None:
    """Return the filtration-valve mode label for *reg_val*, or ``None``."""
    if reg_val is None:
        return None
    return FILTVALVE_MODE_LABELS.get(int(reg_val))


def encode_filtvalve_mode(name: str) -> int:
    """Return the wire value for a filtration-valve mode *name*.

    Raises :class:`ValueError` if *name* is not one of ``enabled``,
    ``always_on`` or ``always_off``.
    """
    try:
        return _FILTVALVE_MODE_VALUES[name]
    except KeyError:
        raise ValueError(
            f"unknown filtvalve mode {name!r}; "
            f"expected one of {sorted(_FILTVALVE_MODE_VALUES)}"
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

    on = u32(padded[1], padded[2])
    interval = u32(padded[7], padded[8])
    return {
        "enable": padded[0],
        "on": on,
        "off": u32(padded[3], padded[4]),
        "period": u32(padded[5], padded[6]),
        "interval": interval,
        "stop": derive_timer_stop(on, interval),
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


def compute_filtration_speed_state(data: dict[str, Any]) -> str:
    """Composite filtration speed: off / low / mid / high.

    Reads MBF_RELAY_STATE speed bits first; falls back to the speed
    nibble of MBF_PAR_FILTRATION_CONF when the relay reports nothing.
    Returns ``"off"`` whenever the dynamically decoded "Filtration Pump"
    key is not ``True``.
    """
    if data.get("Filtration Pump") is not True:
        return "off"

    relay_state = data.get("MBF_RELAY_STATE", 0)
    relay_speed = (relay_state & 0x0700) >> 8
    # Highest set bit wins; supports both individual-bit (1/2/4) and
    # cumulative (1/3/7) encodings.
    if relay_speed & 0x04:
        return "high"
    if relay_speed & 0x02:
        return "mid"
    if relay_speed & 0x01:
        return "low"

    par_filtration_conf = data.get("MBF_PAR_FILTRATION_CONF", 0)
    conf_speed = (par_filtration_conf & 0x0070) >> 4
    if conf_speed == 0:
        return "low"
    if conf_speed == 1:
        return "mid"
    if conf_speed == 2:
        return "high"
    return "off"


# Possible return values of :func:`compute_filtration_speed_state`.
FILTRATION_SPEED_STATE_LABELS: tuple[str, ...] = ("off", "low", "mid", "high")


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


def decode_hidro_polarity(data: dict[str, Any]) -> str | None:
    """Decode hydrolysis cell polarity state from coordinator data snapshot."""
    pol1 = data.get("HIDRO in Pol1")
    pol2 = data.get("HIDRO in Pol2")
    dead = data.get("HIDRO in dead time")
    if pol1 is None and pol2 is None and dead is None:
        return None
    filtration = data.get("Filtration Pump")
    if filtration is not None and filtration is False:
        return "off"
    fl1 = data.get("HIDRO Cell Flow FL1")
    if filtration is True and fl1 is False:
        return "no_flow"
    if dead:
        return "dead_time"
    if pol1:
        return "pol1"
    if pol2:
        return "pol2"
    return "off"


# Possible return values of :func:`decode_hidro_polarity`.
HIDRO_POLARITY_LABELS: tuple[str, ...] = (
    "pol1",
    "pol2",
    "dead_time",
    "no_flow",
    "off",
)


def decode_ion_polarity(data: dict[str, Any]) -> str | None:
    """Decode ionizer cell polarity state from coordinator data snapshot."""
    pol1 = data.get("ION in Pol1")
    pol2 = data.get("ION in Pol2")
    dead = data.get("ION in dead time")
    if pol1 is None and pol2 is None and dead is None:
        return None
    if dead:
        return "dead_time"
    if pol1:
        return "pol1"
    if pol2:
        return "pol2"
    return "off"


# Possible return values of :func:`decode_ion_polarity`.
ION_POLARITY_LABELS: tuple[str, ...] = ("pol1", "pol2", "dead_time", "off")


# MBF_PH_STATUS bits 0-3 (mask 0x000F) encode a pH alarm state.
# Values 0-5 come from the vendor Modbus spec; value 6 (tank level) is
# emitted by real hardware when the acid/base tank runs dry and matches
# the Tasmota driver's handling of the same register.
PH_STATUS_ALARM_LABELS: dict[int, str] = {
    0: "ok",
    1: "ph_high",  # value 0.8 units above the high setpoint
    2: "ph_low",  # value 0.8 units below the low setpoint
    3: "pump_stopped",  # pH pump exceeded MBF_PAR_RELAY_PH_MAX_TIME
    4: "ph_over",  # value above the high setpoint (fine band)
    5: "ph_under",  # value below the low setpoint (fine band)
    6: "tank_level",  # acid/base tank empty (float switch tripped)
}


def decode_ph_alarm(data: dict[str, Any]) -> str | None:
    """Return the pH alarm label for MBF_PH_STATUS_ALARM, or ``None``.

    Reads the ``MBF_PH_STATUS_ALARM`` snapshot key (which the client
    already extracts from bits 0-3 of the ``MBF_PH_STATUS`` register)
    and maps it via :data:`PH_STATUS_ALARM_LABELS`. Returns ``None``
    when the key is missing or holds an unknown value.
    """
    value = data.get("MBF_PH_STATUS_ALARM")
    if value is None:
        return None
    return PH_STATUS_ALARM_LABELS.get(int(value))


def decode_ph_pump_status(data: dict[str, Any]) -> str | None:
    """Decode pH pump operational status from coordinator data snapshot."""
    ctrl = data.get("pH control module")
    acid_bit = data.get("pH acid pump active")
    pump_bit = data.get("pH pump active")
    if ctrl is None and acid_bit is None and pump_bit is None:
        return None
    if ctrl is None:
        return None
    if not ctrl:
        return "off"
    # MBF_PAR_RELAY_PH: 0=acid+base, 1=acid only, 2=base only
    relay_ph = data.get("MBF_PAR_RELAY_PH", 0) or 0
    if relay_ph == 1:
        return "acid" if pump_bit else "idle"
    if relay_ph == 2:
        return "base" if pump_bit else "idle"
    if acid_bit and pump_bit:
        return "both"
    if acid_bit:
        return "acid"
    if pump_bit:
        return "base"
    return "idle"


# Possible return values of :func:`decode_ph_pump_status`.
PH_PUMP_STATUS_LABELS: tuple[str, ...] = ("off", "idle", "acid", "base", "both")


def ph_pump_options(data: dict[str, Any]) -> list[str]:
    """Return the pH pump status options narrowed by ``MBF_PAR_RELAY_PH``.

    ``MBF_PAR_RELAY_PH`` selects the dosing configuration:
    ``0`` = acid + base, ``1`` = acid only, ``2`` = base only. The
    returned list is the ordered subset of :data:`PH_PUMP_STATUS_LABELS`
    that is reachable under the current configuration.
    """
    relay_ph = data.get("MBF_PAR_RELAY_PH", 0) or 0
    if relay_ph == 1:
        return ["off", "idle", "acid"]
    if relay_ph == 2:
        return ["off", "idle", "base"]
    return ["off", "idle", "acid", "base", "both"]


__all__ = [
    "CELL_BOOST_MODE_LABELS",
    "FILTRATION_MODE_LABELS",
    "FILTRATION_SPEED_LABELS",
    "FILTRATION_SPEED_STATE_LABELS",
    "FILTVALVE_MODE_LABELS",
    "HIDRO_POLARITY_LABELS",
    "ION_POLARITY_LABELS",
    "PH_PUMP_STATUS_LABELS",
    "PH_STATUS_ALARM_LABELS",
    "aggregate_filtration_remaining",
    "build_timer_block",
    "calculate_next_interval_time",
    "combine_u32",
    "compute_filtration_speed_state",
    "decode_cell_boost",
    "decode_device_time",
    "decode_filtration_mode",
    "decode_filtration_speed",
    "decode_filtvalve_mode",
    "decode_hidro_polarity",
    "decode_ion_polarity",
    "decode_par_model_modules",
    "decode_ph_alarm",
    "decode_ph_pump_status",
    "derive_timer_stop",
    "encode_cell_boost",
    "encode_device_time",
    "encode_filtration_mode",
    "encode_filtration_speed",
    "encode_filtvalve_mode",
    "generate_time_options",
    "get_filtration_pump_type",
    "get_machine_name",
    "get_timer_interval",
    "hhmm_to_seconds",
    "is_hydrolysis_in_percent",
    "modbus_regs_to_ascii",
    "modbus_regs_to_hex_string",
    "pad_list",
    "parse_register_int",
    "parse_timer_block",
    "parse_version",
    "ph_pump_options",
    "seconds_to_hhmm",
]
