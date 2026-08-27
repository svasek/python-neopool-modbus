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

"""Async Python client for Sugar Valley NeoPool Modbus pool controllers.

The top-level package re-exports the high-level :class:`NeoPoolModbusClient`,
the public exception hierarchy, and the :func:`async_probe_serial` one-shot
helper.  Lower-level helpers are intentionally kept in submodules to keep
the public surface small:

- :mod:`neopool_modbus.registers`    - register addresses, bit masks, timer block layouts
- :mod:`neopool_modbus.decoders`     - register-value parsers and timer helpers
- :mod:`neopool_modbus.capabilities` - module-presence predicates over a data snapshot
- :mod:`neopool_modbus.status_mask`  - status register bit decoders
- :mod:`neopool_modbus.exceptions`   - exception hierarchy
- :mod:`neopool_modbus.probe`        - one-shot probes (e.g. read serial)
"""

from __future__ import annotations

from .client import NeoPoolModbusClient
from .exceptions import (
    InvalidStateReason,
    NeoPoolConnectionError,
    NeoPoolError,
    NeoPoolInvalidStateError,
    NeoPoolModbusError,
    NeoPoolTimeoutError,
)
from .probe import async_probe_serial

__version__ = "4.6.0"

__all__ = [
    "InvalidStateReason",
    "NeoPoolConnectionError",
    "NeoPoolError",
    "NeoPoolInvalidStateError",
    "NeoPoolModbusClient",
    "NeoPoolModbusError",
    "NeoPoolTimeoutError",
    "__version__",
    "async_probe_serial",
]
