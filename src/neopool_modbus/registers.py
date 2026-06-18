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

"""Modbus register addresses and protocol-level constants for NeoPool devices.

These values describe the device hardware and Modbus protocol; they are stable
specifications, not configuration. The Home Assistant integration consumes
them via re-export.
"""

from __future__ import annotations

from enum import IntEnum

# Default Modbus framer used when reading from a TCP gateway.
#   "tcp" -- standard Modbus TCP (MBAP header)
#   "rtu" -- RTU encoded over TCP (no MBAP, includes CRC)
DEFAULT_MODBUS_FRAMER = "tcp"


class TimerRelayMode(IntEnum):
    """Relay timer enable register values (MBV_PAR_CTIMER_*)."""

    ENABLED = 1  # timer-controlled (MBV_PAR_CTIMER_ENABLED)
    ALWAYS_ON = 3  # MBV_PAR_CTIMER_ALWAYS_ON
    ALWAYS_OFF = 4  # MBV_PAR_CTIMER_ALWAYS_OFF


# Single-register write addresses with special semantics.
MANUAL_FILTRATION_REGISTER = 0x0413
EEPROM_SAVE_REGISTER = 0x02F0  # MBF_SAVE_TO_EEPROM
CLEAR_EEPROM_REGISTER = 0x02F1  # MBF_CLEAR_EEPROM
RESET_USER_COUNTERS_REGISTER = 0x02F2  # MBF_RESET_USER_COUNTERS
STOP_ALL_MODULES_REGISTER = 0x02F4  # MBF_STOP_ALL_MODULES
EXEC_REGISTER = 0x02F5  # MBF_RESTART_MODULES
ESCAPE_REGISTER = 0x0297  # MBF_ESCAPE — clear all error messages
COPY_TO_RTC_REGISTER = 0x04F0  # MBF_ACTION_COPY_TO_RTC

# Command registers auto-clear to 0 after write; readback verification must be
# skipped for these. Each fires a one-shot device action when written and the
# firmware then clears the register itself, so a verify-after-write would
# always see 0 and falsely flag a mismatch.
COMMAND_REGISTERS = {
    CLEAR_EEPROM_REGISTER,
    COPY_TO_RTC_REGISTER,
    EEPROM_SAVE_REGISTER,
    ESCAPE_REGISTER,
    EXEC_REGISTER,
    RESET_USER_COUNTERS_REGISTER,
    STOP_ALL_MODULES_REGISTER,
}

HEATING_SETPOINT_REGISTER = 0x0416  # MBF_PAR_HEATING_TEMP
INTELLIGENT_SETPOINT_REGISTER = 0x041C  # MBF_PAR_INTELLIGENT_TEMP

# Setpoint registers (MBF_PAR_* parameters).
HIDRO_SETPOINT_REGISTER = 0x0502  # MBF_PAR_HIDRO
PH_MAX_SETPOINT_REGISTER = 0x0504  # MBF_PAR_PH1
PH_MIN_SETPOINT_REGISTER = 0x0505  # MBF_PAR_PH2
REDOX_SETPOINT_REGISTER = 0x0508  # MBF_PAR_RX1
CHLORINE_SETPOINT_REGISTER = 0x050A  # MBF_PAR_CL1
SMART_TEMP_HIGH_REGISTER = 0x0418  # MBF_PAR_SMART_TEMP_HIGH
SMART_TEMP_LOW_REGISTER = 0x0419  # MBF_PAR_SMART_TEMP_LOW
HIDRO_COVER_REGISTER = 0x042D  # MBF_PAR_HIDRO_COVER_REDUCTION (bits 0-7: reduction %, bits 8-15: temp shutdown)

# Feature switch registers.
CLIMA_ONOFF_REGISTER = 0x0417  # MBF_PAR_CLIMA_ONOFF
SMART_ANTI_FREEZE_REGISTER = 0x041A  # MBF_PAR_SMART_ANTI_FREEZE
UV_MODE_REGISTER = 0x0427  # MBF_PAR_UV_MODE
HIDRO_COVER_ENABLE_REGISTER = (
    0x042C  # MBF_PAR_HIDRO_COVER_ENABLE / temp shutdown bitmask
)

# Filtration scheduling.
INTELLIGENT_FILT_MIN_TIME_REGISTER = 0x041D  # MBF_PAR_INTELLIGENT_FILT_MIN_TIME
RELAY_ACTIVATION_DELAY_REGISTER = 0x0433  # MBF_PAR_RELAY_ACTIVATION_DELAY

# Filter valve registers.
FILTVALVE_MODE_REGISTER = 0x04E9  # MBF_PAR_FILTVALVE_MODE
FILTVALVE_PERIOD_REGISTER = 0x04ED  # MBF_PAR_FILTVALVE_PERIOD_MINUTES

# Relay function/timer-block addresses and function codes.
# Each AUX relay has a timer-block start address, a function-select register,
# and a bitmask that identifies the relay in MBF_RELAY_STATE.
AUX1_TIMER_BLOCK_REGISTER = 0x04AC
AUX1_FUNCTION_REGISTER = 0x04B7
AUX1_FUNCTION_CODE = 0x0800

AUX2_TIMER_BLOCK_REGISTER = 0x04BB
AUX2_FUNCTION_REGISTER = 0x04C6
AUX2_FUNCTION_CODE = 0x1000

AUX3_TIMER_BLOCK_REGISTER = 0x04CA
AUX3_FUNCTION_REGISTER = 0x04D5
AUX3_FUNCTION_CODE = 0x2000

AUX4_TIMER_BLOCK_REGISTER = 0x04D9
AUX4_FUNCTION_REGISTER = 0x04E4
AUX4_FUNCTION_CODE = 0x4000

LIGHT_TIMER_BLOCK_REGISTER = 0x0470
LIGHT_FUNCTION_REGISTER = 0x047B

# 32-bit RTC counter (low word here, high at +1).
DEVICE_TIME_REGISTER = 0x0408  # MBF_PAR_TIME_LOW

# Filtration mode (MBF_PAR_FILT_MODE).
FILTRATION_MODE_REGISTER = 0x0411

# Cell boost composite register (MBF_CELL_BOOST).
CELL_BOOST_REGISTER = 0x020C

# Filtration speed lives in bits 4-6 of MBF_PAR_FILTRATION_CONF (0x050F).
# Writes must read-modify-write to preserve the surrounding bits (pump
# type in 0-3, etc.).
FILTRATION_CONF_REGISTER = 0x050F
FILTRATION_SPEED_MASK = 0x0070
FILTRATION_SPEED_SHIFT = 4

# MBF_RELAY_STATE has 7 relays (bits 0-6); MBF_PAR_*_RELAY_GPIO is 1-based.
MAX_RELAY_GPIO = 7

# Registers that assign physical relay outputs (GPIO number, valid range 1-MAX_RELAY_GPIO).
# A value outside this range indicates register corruption (e.g. framer mismatch).
GPIO_REGISTERS: dict[str, str] = {
    "MBF_PAR_FILT_GPIO": "Filtration relay",
    "MBF_PAR_LIGHTING_GPIO": "Lighting relay",
    "MBF_PAR_HEATING_GPIO": "Heating relay",
    "MBF_PAR_PH_ACID_RELAY_GPIO": "pH acid pump relay",
    "MBF_PAR_PH_BASE_RELAY_GPIO": "pH base pump relay",
    "MBF_PAR_RX_RELAY_GPIO": "Redox pump relay",
    "MBF_PAR_CL_RELAY_GPIO": "Chlorine pump relay",
    "MBF_PAR_CD_RELAY_GPIO": "Conductivity pump relay",
    "MBF_PAR_UV_RELAY_GPIO": "UV lamp relay",
    "MBF_PAR_FILTVALVE_GPIO": "Filter valve relay",
}

# NeoPool firmware refuses Modbus read requests larger than this many
# registers per request. The library batches its own internal reads to
# stay below the limit; the public read API enforces it on the caller.
MAX_REGISTERS_PER_READ = 31

# Modbus function-code classifier. The 0x01 page (MEASURE) is exposed as
# input registers (FC 0x04, "Read Input Registers"); every other page
# uses holding registers (FC 0x03, "Read Holding Registers"). The page
# prefix is what selects the namespace — the entire 0x01XX range is
# input-registers, not just the documented 0x0100-0x011F MEASURE block.
# Mismatching the function code reads a different namespace and returns
# either an exception or — worse — a plausible-looking wrong value.
INPUT_REGISTER_RANGES: tuple[tuple[int, int], ...] = ((0x0100, 0x01FF),)


def is_input_register(address: int) -> bool:
    """Return True if `address` is read with FC 0x04 (input registers)."""
    return any(lo <= address <= hi for lo, hi in INPUT_REGISTER_RANGES)


def is_valid_relay_gpio(gpio: int) -> bool:
    """Return True if the relay GPIO number is within the hardware range (1-based, 1-7)."""
    return 1 <= gpio <= MAX_RELAY_GPIO


# Timer blocks 0x0434-0x04E8 are read in groups of 15 registers due to the
# device's per-request limit.
TIMER_BLOCKS = {
    "filtration1": 0x0434,
    "filtration2": 0x0443,
    "filtration3": 0x0452,
    "relay_light": 0x0470,
    "relay_aux1": 0x04AC,
    "relay_aux1b": 0x0461,
    "relay_aux2": 0x04BB,
    "relay_aux2b": 0x047F,
    "relay_aux3": 0x04CA,
    "relay_aux3b": 0x048E,
    "relay_aux4": 0x04D9,
    "relay_aux4b": 0x049D,
}

__all__ = [
    "AUX1_FUNCTION_CODE",
    "AUX1_FUNCTION_REGISTER",
    "AUX1_TIMER_BLOCK_REGISTER",
    "AUX2_FUNCTION_CODE",
    "AUX2_FUNCTION_REGISTER",
    "AUX2_TIMER_BLOCK_REGISTER",
    "AUX3_FUNCTION_CODE",
    "AUX3_FUNCTION_REGISTER",
    "AUX3_TIMER_BLOCK_REGISTER",
    "AUX4_FUNCTION_CODE",
    "AUX4_FUNCTION_REGISTER",
    "AUX4_TIMER_BLOCK_REGISTER",
    "CELL_BOOST_REGISTER",
    "CHLORINE_SETPOINT_REGISTER",
    "CLEAR_EEPROM_REGISTER",
    "CLIMA_ONOFF_REGISTER",
    "COMMAND_REGISTERS",
    "COPY_TO_RTC_REGISTER",
    "DEFAULT_MODBUS_FRAMER",
    "DEVICE_TIME_REGISTER",
    "EEPROM_SAVE_REGISTER",
    "ESCAPE_REGISTER",
    "EXEC_REGISTER",
    "FILTRATION_CONF_REGISTER",
    "FILTRATION_MODE_REGISTER",
    "FILTRATION_SPEED_MASK",
    "FILTRATION_SPEED_SHIFT",
    "FILTVALVE_MODE_REGISTER",
    "FILTVALVE_PERIOD_REGISTER",
    "GPIO_REGISTERS",
    "HEATING_SETPOINT_REGISTER",
    "HIDRO_COVER_ENABLE_REGISTER",
    "HIDRO_COVER_REGISTER",
    "HIDRO_SETPOINT_REGISTER",
    "INPUT_REGISTER_RANGES",
    "INTELLIGENT_FILT_MIN_TIME_REGISTER",
    "INTELLIGENT_SETPOINT_REGISTER",
    "LIGHT_FUNCTION_REGISTER",
    "LIGHT_TIMER_BLOCK_REGISTER",
    "MANUAL_FILTRATION_REGISTER",
    "MAX_REGISTERS_PER_READ",
    "MAX_RELAY_GPIO",
    "PH_MAX_SETPOINT_REGISTER",
    "PH_MIN_SETPOINT_REGISTER",
    "REDOX_SETPOINT_REGISTER",
    "RELAY_ACTIVATION_DELAY_REGISTER",
    "RESET_USER_COUNTERS_REGISTER",
    "SMART_ANTI_FREEZE_REGISTER",
    "SMART_TEMP_HIGH_REGISTER",
    "SMART_TEMP_LOW_REGISTER",
    "STOP_ALL_MODULES_REGISTER",
    "TIMER_BLOCKS",
    "TimerRelayMode",
    "UV_MODE_REGISTER",
    "is_input_register",
    "is_valid_relay_gpio",
]
