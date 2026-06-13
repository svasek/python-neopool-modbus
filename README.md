# neopool-modbus

[![PyPI](https://img.shields.io/pypi/v/neopool-modbus.svg)](https://pypi.org/project/neopool-modbus/)
[![Python](https://img.shields.io/pypi/pyversions/neopool-modbus.svg)](https://pypi.org/project/neopool-modbus/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

[![Release](https://github.com/Svasek/python-neopool-modbus/actions/workflows/release.yaml/badge.svg)](https://github.com/Svasek/python-neopool-modbus/actions/workflows/release.yaml)
[![Unit Tests](https://github.com/Svasek/python-neopool-modbus/actions/workflows/test.yaml/badge.svg)](https://github.com/Svasek/python-neopool-modbus/actions/workflows/test.yaml)
[![Type Check](https://github.com/Svasek/python-neopool-modbus/actions/workflows/typecheck.yaml/badge.svg)](https://github.com/Svasek/python-neopool-modbus/actions/workflows/typecheck.yaml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/github/Svasek/python-neopool-modbus/graph/badge.svg)](https://app.codecov.io/github/Svasek/python-neopool-modbus)

[![Conventional Branch](https://img.shields.io/badge/Conventional%20Branch-Spec-6192c3)](https://conventional-branch.github.io/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://www.conventionalcommits.org/)
[![Gitmoji](https://img.shields.io/badge/gitmoji-%20%F0%9F%98%9C%20%F0%9F%98%8D-FFDD67.svg)](https://gitmoji.dev/specification)
[![Sponsor me](https://img.shields.io/badge/sponsor-❤-brightgreen?style=flat)](https://github.com/sponsors/svasek)
[![Ko-fi](https://img.shields.io/badge/ko--fi-support-29abe0?style=flat&logo=ko-fi)](https://ko-fi.com/svasek)

Async Python client for **NeoPool**-based pool controllers connected via
**Modbus TCP**. NeoPool is a control system originally developed by the
Spanish company **Sugar Valley** (acquired by **Hayward** in 2016), sold
under many brand names and product lines worldwide.

**Supported device models** (Sugar Valley / Hayward product lines):
Hidrolife • Aquascenic • Oxilife • Bionet • Hidroniser • UVScenic •
Station • Aquarite

**Distributed by** (vendors selling NeoPool-based hardware):
Hayward • Brilix (Albixon) • Bayrol • Certikin • Poolstar • GrupAquadirect •
Pentair • ProducPool • Pool Technologie • Kripsol

> **Note:** _VistaPool_ is the name of Hayward's mobile/web app for
> cloud-based pool management. This library communicates **locally via
> Modbus TCP** — it does not require or use the VistaPool app or any
> cloud service.

This library is the communication layer extracted from the
[Home Assistant `neopool` integration](https://github.com/svasek/homeassistant-neopool-modbus)
and is suitable for any async Python project — Home Assistant integrations,
scripts, dashboards, or custom automation.

## Installation

```bash
pip install neopool-modbus
```

Requires Python 3.13+ and `pymodbus>=3.10.0` (installed transitively).

## Quick start

```python
import asyncio

from neopool_modbus import NeoPoolModbusClient


async def main() -> None:
    client = NeoPoolModbusClient(
        {"host": "192.168.1.42", "port": 502, "slave_id": 1}
    )
    try:
        data = await client.async_read_all()
        # Keys are the NeoPool register names defined by Sugar Valley
        # (mirrored from Tasmota's xsns_83_neopool.ino driver);
        # values are decoded into native Python types.
        print(f"pH:          {data['MBF_MEASURE_PH']}")           # e.g. 7.42
        print(f"Temperature: {data['MBF_MEASURE_TEMPERATURE']} °C")  # e.g. 27.3
        print(f"Hydrolysis:  {data['MBF_HIDRO_CURRENT']}")        # e.g. 6.5
    finally:
        await client.close()


asyncio.run(main())
```

The client is lazy — it opens the TCP connection on first use and reuses it
across calls; `close()` releases the socket and resets retry/backoff state.

### Reading individual registers

For one-off reads by address, `async_read_register(address, count=1)` picks
the correct Modbus function code automatically: **Read Input Registers**
(FC 0x04) for any address on the 0x01 page (MEASURE) and **Read Holding
Registers** (FC 0x03) elsewhere.

```python
from neopool_modbus import NeoPoolModbusClient

client = NeoPoolModbusClient({"host": "192.168.1.42"})

# Single register — pH level (raw u16, divide by 100 for pH 7.20)
ph_raw = (await client.async_read_register(0x0102))[0]

# Multi-register read (1-31; the firmware refuses larger requests).
# Combine the two halves of a 32-bit cell-runtime counter:
low, high = await client.async_read_register(0x0208, count=2)
partial_seconds = (high << 16) | low
```

The method validates the request before touching the wire and raises
`ValueError` for out-of-range addresses, counts that exceed
`MAX_REGISTERS_PER_READ` (31), or ranges that would either cross the
input/holding namespace boundary or extend past the 16-bit address space.

## Public API

```python
from neopool_modbus import (
    NeoPoolModbusClient,
    NeoPoolError,
    NeoPoolConnectionError,
    NeoPoolModbusError,
    NeoPoolTimeoutError,
    async_probe_serial,
)
from neopool_modbus.registers import (
    CLEAR_EEPROM_REGISTER,
    COMMAND_REGISTERS,
    COPY_TO_RTC_REGISTER,
    DEFAULT_MODBUS_FRAMER,
    EEPROM_SAVE_REGISTER,
    ESCAPE_REGISTER,
    EXEC_REGISTER,
    HEATING_SETPOINT_REGISTER,
    INPUT_REGISTER_RANGES,
    INTELLIGENT_SETPOINT_REGISTER,
    MANUAL_FILTRATION_REGISTER,
    MAX_REGISTERS_PER_READ,
    RESET_USER_COUNTERS_REGISTER,
    STOP_ALL_MODULES_REGISTER,
    TIMER_BLOCKS,
    is_input_register,
    is_valid_relay_gpio,
)
from neopool_modbus.decoders import (
    parse_timer_block,
    build_timer_block,
    hhmm_to_seconds,
    seconds_to_hhmm,
    get_machine_name,
    is_hydrolysis_in_percent,
    # ... see neopool_modbus.decoders for the full list
)
from neopool_modbus.status_mask import (
    decode_relay_state,
    decode_named_relay_states,
    decode_uv_lamp_state,
    decode_hidro_status_bits,
    decode_ion_status_bits,
    decode_ph_rx_cl_cd_status_bits,
)
```

All client methods translate underlying pymodbus exceptions into the
`NeoPoolError` hierarchy at the library boundary, so callers never need
to import `pymodbus` to catch errors:

| Class                    | Raised when                                                                      |
| ------------------------ | -------------------------------------------------------------------------------- |
| `NeoPoolConnectionError` | TCP connect fails, returned `False`, or the client is in its post-failure backoff |
| `NeoPoolTimeoutError`    | Connect, read, or write times out (`asyncio.TimeoutError`)                       |
| `NeoPoolModbusError`     | A read returns a Modbus exception response (`isError()` true), or `async_write_aux_relay` / one of the timer write follow-ups returns `isError()` |
| `NeoPoolError`           | Common base; catch this to handle any of the above                                |

> ⚠️ `NeoPoolModbusClient.async_write_register()` is the exception to the
> table above: it returns `None` (rather than raising) on `isError()` so
> existing callers in the Home Assistant integration keep working. A
> future major release will tighten this to raise `NeoPoolModbusError`
> for consistency.

```python
from neopool_modbus import NeoPoolError, NeoPoolModbusClient

client = NeoPoolModbusClient({"host": "192.168.1.42"})
try:
    data = await client.async_read_all()
except NeoPoolError as exc:
    # exc.__cause__ is the original pymodbus / asyncio exception, if any.
    print(f"NeoPool read failed: {exc}")
```

`ValueError` is still raised directly for programmer errors such as an
out-of-range AUX relay index — those are not transport failures.

## Features

- Async I/O on top of `pymodbus.AsyncModbusTcpClient`
- Batched register reads — one round-trip per protocol page, with
  notification-bit-driven cache invalidation so unchanged pages skip the read
- Public read-by-address API (`async_read_register`) that automatically
  picks Read Input vs Read Holding based on the address
- Exponential connection retry with bounded backoff
- Write-and-verify cycle for configuration registers, with auto-clearing
  command registers (`COMMAND_REGISTERS`) excluded from verification
- Capability detection (hydrolysis, pH, Redox, chlorine, conductivity, ION)
- Strict type hints (`py.typed`), 100 % unit-test coverage

## Logging

The library uses a single logger named `neopool_modbus`. Enable it like any
other Python logger:

```python
import logging
logging.getLogger("neopool_modbus").setLevel(logging.DEBUG)
```

Home Assistant users can flip the integration's "Enable debug logging" toggle
in the UI; the integration's `manifest.json` lists `neopool_modbus` so the
toggle covers the library too.

## Based On

- [Tasmota NeoPool driver](https://github.com/arendst/Tasmota/blob/master/tasmota/tasmota_xsns_sensor/xsns_83_neopool.ino) — implements the NeoPool Modbus register protocol originally documented by Sugar Valley
- _NeoPool Control System MODBUS Register description_ — a Markdown transcription of the official Modbus register documentation by Sugar Valley (see [`docs/modbus-registers.md`](docs/modbus-registers.md))

## Disclaimer

This library is provided "AS IS" and without any warranty or guarantee of any kind.
The author takes no responsibility for any damage, loss, or malfunction resulting from the use or misuse of this code. Use at your own risk.

_This project is not affiliated with or endorsed by Sugar Valley, Hayward, or any other pool equipment manufacturer or distributor._

_"VistaPool" is a trademark of Hayward Industries, Inc. This library communicates locally via Modbus and does not use the VistaPool cloud service._

## License

Apache 2.0 — see [LICENSE](LICENSE).
