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

"""Lightweight one-shot probes against a NeoPool device.

These helpers open a fresh pymodbus connection, perform a single read,
and tear it down again.  They are designed for situations like Home
Assistant config-flow user-input validation where ``NeoPoolModbusClient``
with its retry/backoff state machine would be overkill.

All probes raise the public :class:`NeoPoolError` hierarchy on
transport / protocol failure so callers do not need to import
:mod:`pymodbus` to handle errors.
"""

from __future__ import annotations

import asyncio
import logging

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.framer import FramerType

from .decoders import modbus_regs_to_hex_string
from .exceptions import (
    NeoPoolConnectionError,
    NeoPoolModbusError,
    NeoPoolTimeoutError,
)

_LOGGER = logging.getLogger("neopool_modbus")

_SERIAL_REGISTER = 0x0004  # MBF_POWER_MODULE_NODEID
_SERIAL_COUNT = 6


def _resolve_framer(framer: str) -> FramerType:
    framer_str = framer.strip().lower()
    if framer_str == "rtu":
        return FramerType.RTU
    if framer_str == "tcp":
        return FramerType.SOCKET
    raise ValueError(f"Unknown framer: {framer!r} (expected 'tcp' or 'rtu')")


async def async_probe_serial(
    host: str,
    *,
    port: int = 502,
    unit_id: int | None = None,
    slave_id: int | None = None,
    framer: str = "tcp",
    timeout: float = 5.0,
) -> str:
    """Read the device's hardware serial number with a single Modbus call.

    Reads the 6-register MBF_POWER_MODULE_NODEID block (``0x0004``-``0x0009``)
    and returns it as a 24-character uppercase hex string.

    This is intended for short-lived probes (e.g. validating a user-entered
    host/port pair during a Home Assistant config flow).  For ongoing
    polling use :class:`NeoPoolModbusClient` instead.

    Args:
        host: Hostname or IP of the Modbus TCP gateway.
        port: TCP port (default ``502``).
        unit_id: Modbus unit (server) ID (default ``1``). Identifies the
            device on the bus per Modbus TCP/IP spec V1.1b3 ("Unit
            Identifier"). The new client/server naming replaces the
            legacy master/slave terminology.
        slave_id: Deprecated alias for ``unit_id`` kept for backwards
            compatibility. Ignored when ``unit_id`` is set.
        framer: ``"tcp"`` (Modbus TCP / MBAP, default) or ``"rtu"``
            (RTU-over-TCP for gateways like Elfin EW11).
        timeout: Per-call timeout in seconds for both the connect and the
            register read.

    Returns:
        The 24-character hex serial string.

    Raises:
        ValueError: ``framer`` is not ``"tcp"`` or ``"rtu"``.
        NeoPoolTimeoutError: Connect or read timed out.
        NeoPoolConnectionError: TCP connect was refused or returned False.
        NeoPoolModbusError: The device returned a Modbus exception
            response (``isError()`` true), an unexpected pymodbus
            exception during the read, or registers that did not
            decode into a usable serial string. The original
            pymodbus / asyncio exception (if any) is preserved as
            ``__cause__``.
    """
    framer_type = _resolve_framer(framer)
    if unit_id is None:
        unit_id = slave_id if slave_id is not None else 1
    client = AsyncModbusTcpClient(host, port=port, timeout=timeout, framer=framer_type)
    try:
        try:
            connected = await asyncio.wait_for(client.connect(), timeout=timeout)
        except asyncio.CancelledError:
            raise
        except TimeoutError as exc:
            raise NeoPoolTimeoutError(
                f"Probe connect to {host}:{port} timed out after {timeout}s"
            ) from exc
        except Exception as exc:
            raise NeoPoolConnectionError(
                f"Probe connect failed for {host}:{port}: {exc}"
            ) from exc

        if not connected:
            raise NeoPoolConnectionError(
                f"Probe connect returned False for {host}:{port}"
            )

        try:
            rr = await asyncio.wait_for(
                client.read_holding_registers(
                    address=_SERIAL_REGISTER,
                    count=_SERIAL_COUNT,
                    device_id=unit_id,
                ),
                timeout=timeout,
            )
        except asyncio.CancelledError:
            raise
        except TimeoutError as exc:
            raise NeoPoolTimeoutError(
                f"Probe read from {host}:{port} timed out after {timeout}s"
            ) from exc
        except Exception as exc:
            raise NeoPoolModbusError(
                f"Probe read failed for {host}:{port}: {exc}"
            ) from exc

        if rr.isError():
            raise NeoPoolModbusError(
                f"Probe read returned Modbus error from {host}:{port}: {rr}"
            )

        serial = modbus_regs_to_hex_string(list(rr.registers))
        if not serial:
            raise NeoPoolModbusError(
                f"Probe read for {host}:{port} returned no usable serial bytes"
            )
        _LOGGER.debug("Probe read serial %s from %s:%s", serial, host, port)
        return serial
    finally:
        try:
            client.close()
        except asyncio.CancelledError:
            raise
        except Exception:  # cleanup path: never let close() failures mask the read
            _LOGGER.debug("Probe close raised; ignoring", exc_info=True)


__all__ = ["async_probe_serial"]
