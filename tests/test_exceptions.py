"""Tests for the public exception hierarchy."""

from __future__ import annotations

import pytest

from neopool_modbus import (
    InvalidStateReason,
    NeoPoolConnectionError,
    NeoPoolError,
    NeoPoolInvalidStateError,
    NeoPoolModbusError,
    NeoPoolTimeoutError,
)


def test_invalid_state_error_default_reason_is_none():
    """``reason`` defaults to None so legacy call sites keep working."""
    err = NeoPoolInvalidStateError("something is off")
    assert err.reason is None
    assert str(err) == "something is off"


def test_invalid_state_error_accepts_reason():
    """The optional ``reason`` kwarg is stored and readable."""
    err = NeoPoolInvalidStateError(
        "relay in auto", reason=InvalidStateReason.RELAY_IN_AUTO_MODE
    )
    assert err.reason == InvalidStateReason.RELAY_IN_AUTO_MODE
    assert str(err) == "relay in auto"


def test_invalid_state_error_reason_is_positional_only():
    """``reason`` must be passed as keyword to keep the signature stable."""
    with pytest.raises(TypeError):
        NeoPoolInvalidStateError(
            "msg",  # pyright: ignore[reportCallIssue]
            InvalidStateReason.FILTRATION_NOT_IN_MANUAL_MODE,
        )


@pytest.mark.parametrize(
    ("exc_cls", "base"),
    [
        (NeoPoolConnectionError, NeoPoolError),
        (NeoPoolTimeoutError, NeoPoolError),
        (NeoPoolModbusError, NeoPoolError),
        (NeoPoolInvalidStateError, NeoPoolError),
    ],
)
def test_exception_hierarchy(exc_cls, base):
    """All lib exceptions descend from NeoPoolError."""
    assert issubclass(exc_cls, base)
    assert issubclass(exc_cls, Exception)


def test_invalid_state_reason_values_are_stable():
    """The enum values form part of the API surface and must not drift silently."""
    assert InvalidStateReason.RELAY_IN_AUTO_MODE.value == "relay_in_auto_mode"
    assert (
        InvalidStateReason.FILTRATION_NOT_IN_MANUAL_MODE.value
        == "filtration_not_in_manual_mode"
    )
