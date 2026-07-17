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

"""Public exception hierarchy for ``neopool_modbus``.

These classes form a stable contract for callers of the library.  Internal
pymodbus exceptions raised by the underlying TCP / Modbus layer are caught
at the library boundary and re-raised as one of these classes, so callers
never need to catch :mod:`pymodbus`-specific types.
"""

from __future__ import annotations

from enum import Enum


class InvalidStateReason(Enum):
    """Discriminator for :class:`NeoPoolInvalidStateError` sub-cases.

    Callers can dispatch on this to render distinct user-facing messages
    (e.g. "relay in AUTO mode" vs "filtration not in manual mode")
    without parsing exception message strings.
    """

    RELAY_IN_AUTO_MODE = "relay_in_auto_mode"
    FILTRATION_NOT_IN_MANUAL_MODE = "filtration_not_in_manual_mode"
    FILTRATION_BOOST_ACTIVE = "filtration_boost_active"


class NeoPoolError(Exception):
    """Base class for all ``neopool_modbus`` errors."""


class NeoPoolConnectionError(NeoPoolError):
    """Raised when the TCP connection to the device fails or is lost."""


class NeoPoolTimeoutError(NeoPoolError):
    """Raised when a Modbus read or write operation times out."""


class NeoPoolModbusError(NeoPoolError):
    """Raised when the device returns a Modbus exception response.

    This covers the case where the TCP transport works but the Modbus
    payload itself indicates a protocol-level failure (``isError()`` is
    true on the response, or the device replied with an unexpected
    payload such as ``ExceptionResponse``).
    """


class NeoPoolInvalidStateError(NeoPoolError):
    """Raised when the device is in a state that rejects the requested operation.

    Distinct from :class:`NeoPoolModbusError` (which indicates a
    protocol-level failure) and :class:`NeoPoolConnectionError` (transport
    issue). Callers can catch this to translate into user-facing messages
    ("device is in auto mode, cannot control manually") without conflating
    a legitimate state with a hardware fault.

    The optional :attr:`reason` attribute discriminates between distinct
    sub-cases (e.g. relay in AUTO vs filtration not in manual mode) so
    callers can dispatch without parsing the exception message.
    """

    def __init__(
        self, message: str, *, reason: InvalidStateReason | None = None
    ) -> None:
        """Store the human-readable *message* and the optional *reason* enum."""
        super().__init__(message)
        self.reason = reason


__all__ = [
    "InvalidStateReason",
    "NeoPoolConnectionError",
    "NeoPoolError",
    "NeoPoolInvalidStateError",
    "NeoPoolModbusError",
    "NeoPoolTimeoutError",
]
