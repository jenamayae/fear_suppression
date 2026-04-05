"""Minimal LabJack trigger helpers (FIO0-FIO7, 8-bit event codes)."""

from __future__ import annotations

import time

FIO_LINES = [f"FIO{i}" for i in range(8)]
FIO_MASK = 0xFF

ONSET_CODE = 1
OFFSET_CODE = 2
FRAME_CODE = 3

PULSE_WIDTH_S = 0.010
FRAME_INTERVAL = 80


def open_labjack(device_type: str = "T7", connection_type: str = "ANY", identifier: str = "ANY"):
    """Open LabJack and configure FIO0-FIO7 as digital outputs."""
    try:
        from labjack import ljm
    except ImportError as exc:
        raise RuntimeError("Could not import labjack-ljm. Install with: pip install labjack-ljm") from exc

    handle = ljm.openS(device_type, connection_type, identifier)

    # Some devices do not expose this register; ignore if unavailable.
    try:
        analog_enable = int(ljm.eReadName(handle, "DIO_ANALOG_ENABLE"))
        ljm.eWriteName(handle, "DIO_ANALOG_ENABLE", float(analog_enable & ~FIO_MASK))
    except Exception:
        pass

    ljm.eWriteName(handle, "FIO_DIRECTION", float(FIO_MASK))
    ljm.eWriteNames(handle, len(FIO_LINES), FIO_LINES, [0.0] * 8)
    return ljm, handle


def write_code(ljm, handle: int, code: int) -> None:
    """Write one 8-bit event code to FIO0-FIO7."""
    if not 0 <= int(code) <= 255:
        raise ValueError(f"Event code must be 0..255, got {code}")

    values = [float((int(code) >> bit) & 1) for bit in range(8)]
    ljm.eWriteNames(handle, len(FIO_LINES), FIO_LINES, values)


def clear_code(ljm, handle: int) -> None:
    write_code(ljm, handle, 0)


def pulse_code(ljm, handle: int, code: int, width_s: float = PULSE_WIDTH_S) -> None:
    write_code(ljm, handle, code)
    if width_s > 0:
        time.sleep(width_s)
    clear_code(ljm, handle)


def send_stimulus_onset(ljm, handle: int, code: int = ONSET_CODE) -> None:
    pulse_code(ljm, handle, code)


def send_stimulus_offset(ljm, handle: int, code: int = OFFSET_CODE) -> None:
    pulse_code(ljm, handle, code)


def maybe_send_frame_marker(
    ljm,
    handle: int,
    frame_num: int,
    interval: int = FRAME_INTERVAL,
    code: int = FRAME_CODE,
) -> bool:
    """Pulse code on every Nth frame. Returns True if sent."""
    if interval <= 0:
        return False
    if frame_num > 0 and frame_num % interval == 0:
        pulse_code(ljm, handle, code)
        return True
    return False


def close_labjack(ljm, handle: int) -> None:
    """Clear lines and close handle safely."""
    try:
        clear_code(ljm, handle)
    except Exception:
        pass
    try:
        ljm.close(handle)
    except Exception:
        pass

