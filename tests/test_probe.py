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

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from neopool_modbus import async_probe_serial
from neopool_modbus.exceptions import (
    NeoPoolConnectionError,
    NeoPoolModbusError,
    NeoPoolTimeoutError,
)
from neopool_modbus.probe import _resolve_framer


def _make_client(connect_result=True, read_result=None):
    """Build a stub AsyncModbusTcpClient with the requested behavior."""
    fake = MagicMock()
    fake.connect = AsyncMock(return_value=connect_result)
    fake.read_holding_registers = AsyncMock(return_value=read_result)
    fake.close = MagicMock(return_value=None)
    return fake


def _make_response(registers, is_error=False):
    rr = MagicMock()
    rr.registers = registers
    rr.isError = lambda: is_error
    return rr


def test_resolve_framer_tcp():
    from pymodbus.framer import FramerType

    assert _resolve_framer("tcp") == FramerType.SOCKET
    assert _resolve_framer("TCP") == FramerType.SOCKET
    assert _resolve_framer(" tcp ") == FramerType.SOCKET


def test_resolve_framer_rtu():
    from pymodbus.framer import FramerType

    assert _resolve_framer("rtu") == FramerType.RTU


def test_resolve_framer_invalid():
    with pytest.raises(ValueError, match="Unknown framer"):
        _resolve_framer("bogus")


@pytest.mark.asyncio
async def test_async_probe_serial_happy_path():
    """Successful probe returns the decoded hex string."""
    # 6 registers worth of data; modbus_regs_to_hex_string concatenates each
    # 16-bit register as 4 hex characters.
    fake_client = _make_client(
        connect_result=True,
        read_result=_make_response([0x0001, 0x00AC, 0x00CD, 0x0012, 0x0034, 0x0000]),
    )
    with patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client):
        serial = await async_probe_serial(
            "192.0.2.10", port=502, unit_id=1, framer="tcp", timeout=2.0
        )
    assert serial == "000100AC00CD001200340000"
    fake_client.connect.assert_awaited_once()
    fake_client.read_holding_registers.assert_awaited_once_with(
        address=0x0004, count=6, device_id=1
    )


@pytest.mark.asyncio
async def test_async_probe_serial_legacy_slave_id_alias():
    """Calling probe with the legacy ``slave_id`` keyword still routes to ``device_id``."""
    fake_client = _make_client(
        connect_result=True,
        read_result=_make_response([0x0001, 0x00AC, 0x00CD, 0x0012, 0x0034, 0x0000]),
    )
    with patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client):
        await async_probe_serial("192.0.2.10", slave_id=4, timeout=2.0)
    fake_client.read_holding_registers.assert_awaited_once_with(
        address=0x0004, count=6, device_id=4
    )


@pytest.mark.asyncio
async def test_async_probe_serial_unit_id_takes_precedence_over_slave_id():
    """When both ``unit_id`` and ``slave_id`` are passed, ``unit_id`` wins."""
    fake_client = _make_client(
        connect_result=True,
        read_result=_make_response([0x0001, 0x00AC, 0x00CD, 0x0012, 0x0034, 0x0000]),
    )
    with patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client):
        await async_probe_serial("192.0.2.10", unit_id=2, slave_id=9, timeout=2.0)
    fake_client.read_holding_registers.assert_awaited_once_with(
        address=0x0004, count=6, device_id=2
    )


@pytest.mark.asyncio
async def test_async_probe_serial_unit_id_defaults_to_one():
    """Neither ``unit_id`` nor ``slave_id`` provided: defaults to ``1``."""
    fake_client = _make_client(
        connect_result=True,
        read_result=_make_response([0x0001, 0x00AC, 0x00CD, 0x0012, 0x0034, 0x0000]),
    )
    with patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client):
        await async_probe_serial("192.0.2.10", timeout=2.0)
    fake_client.read_holding_registers.assert_awaited_once_with(
        address=0x0004, count=6, device_id=1
    )


@pytest.mark.asyncio
async def test_async_probe_serial_connect_returns_false():
    fake_client = _make_client(connect_result=False)
    with (
        patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client),
        pytest.raises(NeoPoolConnectionError, match="returned False"),
    ):
        await async_probe_serial("192.0.2.10")


@pytest.mark.asyncio
async def test_async_probe_serial_connect_timeout():
    fake_client = _make_client()
    fake_client.connect = AsyncMock(side_effect=TimeoutError("connect t/o"))
    with (
        patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client),
        pytest.raises(NeoPoolTimeoutError, match=r"connect to .* timed out after"),
    ):
        await async_probe_serial("192.0.2.10")


@pytest.mark.asyncio
async def test_async_probe_serial_connect_refused():
    fake_client = _make_client()
    fake_client.connect = AsyncMock(side_effect=ConnectionRefusedError("refused"))
    with (
        patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client),
        pytest.raises(NeoPoolConnectionError, match="connect failed"),
    ):
        await async_probe_serial("192.0.2.10")


@pytest.mark.asyncio
async def test_async_probe_serial_read_timeout():
    fake_client = _make_client(connect_result=True)
    fake_client.read_holding_registers = AsyncMock(side_effect=TimeoutError("read t/o"))
    with (
        patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client),
        pytest.raises(NeoPoolTimeoutError, match=r"read from .* timed out after"),
    ):
        await async_probe_serial("192.0.2.10")


@pytest.mark.asyncio
async def test_async_probe_serial_read_other_exception():
    fake_client = _make_client(connect_result=True)
    fake_client.read_holding_registers = AsyncMock(side_effect=RuntimeError("boom"))
    with (
        patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client),
        pytest.raises(NeoPoolModbusError, match="read failed"),
    ):
        await async_probe_serial("192.0.2.10")


@pytest.mark.asyncio
async def test_async_probe_serial_read_iserror():
    fake_client = _make_client(
        connect_result=True,
        read_result=_make_response([0] * 6, is_error=True),
    )
    with (
        patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client),
        pytest.raises(NeoPoolModbusError, match="Modbus error"),
    ):
        await async_probe_serial("192.0.2.10")


@pytest.mark.asyncio
async def test_async_probe_serial_empty_serial():
    """All-zero registers decode to a non-empty string, so the decoder
    rejection path needs registers that yield an empty string. We force
    that by patching the decoder."""
    fake_client = _make_client(
        connect_result=True,
        read_result=_make_response([0, 0, 0, 0, 0, 0]),
    )
    with (
        patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client),
        patch("neopool_modbus.probe.modbus_regs_to_hex_string", return_value=""),
        pytest.raises(NeoPoolModbusError, match="no usable serial"),
    ):
        await async_probe_serial("192.0.2.10")


@pytest.mark.asyncio
async def test_async_probe_serial_invalid_framer():
    """A bad framer string must raise ValueError before any TCP work."""
    with (
        patch("neopool_modbus.probe.AsyncModbusTcpClient") as ctor,
        pytest.raises(ValueError, match="Unknown framer"),
    ):
        await async_probe_serial("192.0.2.10", framer="ascii")
    ctor.assert_not_called()


@pytest.mark.asyncio
async def test_async_probe_serial_close_raises_is_swallowed():
    """An exception from close() during cleanup must not mask success."""
    fake_client = _make_client(
        connect_result=True,
        read_result=_make_response([0x0001] * 6),
    )
    fake_client.close = MagicMock(side_effect=RuntimeError("close fail"))
    with patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client):
        serial = await async_probe_serial("192.0.2.10")
    assert serial == "000100010001000100010001"


@pytest.mark.asyncio
async def test_async_probe_serial_close_cancelled_propagates():
    """asyncio.CancelledError from close() must propagate, not be swallowed."""
    fake_client = _make_client(
        connect_result=True,
        read_result=_make_response([0x0001] * 6),
    )
    fake_client.close = MagicMock(side_effect=asyncio.CancelledError())
    with (
        patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client),
        pytest.raises(asyncio.CancelledError),
    ):
        await async_probe_serial("192.0.2.10")


@pytest.mark.asyncio
async def test_async_probe_serial_connect_cancelled_propagates():
    """asyncio.CancelledError from connect() must propagate unchanged,
    never be wrapped into a NeoPoolError."""
    fake_client = _make_client()
    fake_client.connect = AsyncMock(side_effect=asyncio.CancelledError())
    with (
        patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client),
        pytest.raises(asyncio.CancelledError),
    ):
        await async_probe_serial("192.0.2.10")


@pytest.mark.asyncio
async def test_async_probe_serial_read_cancelled_propagates():
    """asyncio.CancelledError from read_holding_registers() must propagate
    unchanged, never be wrapped into a NeoPoolError."""
    fake_client = _make_client(connect_result=True)
    fake_client.read_holding_registers = AsyncMock(side_effect=asyncio.CancelledError())
    with (
        patch("neopool_modbus.probe.AsyncModbusTcpClient", return_value=fake_client),
        pytest.raises(asyncio.CancelledError),
    ):
        await async_probe_serial("192.0.2.10")
