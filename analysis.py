from __future__ import annotations

import argparse
from fractions import Fraction
import math
from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd

from config import center_flicker_hz, surround_flicker_hz


event_codes = {1, 2, 3}
target_frequencies_hz = (center_flicker_hz, surround_flicker_hz)
dynamic_condition_ids = (5, 6, 7, 8)
plot_channel = "POz"
max_plot_hz = 50.0
max_plot_uv = 1500.0
data_dir = Path(__file__).resolve().parent / "data"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create the final dynamic-surround spectra plot for one run.")
    parser.add_argument("sub_id", help="Subject id, e.g. sub-martin")
    parser.add_argument("ses_id", help="Session id, e.g. ses-001")
    parser.add_argument("run_id", help="Run id, e.g. run-002")
    return parser


def _find_run_paths(sub_id: str, ses_id: str, run_id: str) -> tuple[Path, Path, Path]:
    rawdata_dir = data_dir / sub_id / ses_id / "rawdata"
    cnt_paths = sorted(rawdata_dir.glob("*.cnt"))
    if not cnt_paths:
        raise FileNotFoundError(f"No .cnt file found in {rawdata_dir} for {run_id}")
    if len(cnt_paths) > 1:
        raise ValueError(f"Expected 1 .cnt file in {rawdata_dir}, found {len(cnt_paths)}: {cnt_paths}")

    cnt_path = cnt_paths[0]
    trial_conditions_path = data_dir / sub_id / ses_id / "metadata" / f"trial_conditions_{run_id}.csv"
    if not trial_conditions_path.exists():
        raise FileNotFoundError(f"No trial conditions file found at {trial_conditions_path}")

    output_path = cnt_path.parent.parent / "derivatives" / f"dynamic_surround_spectra_{run_id}.png"
    return cnt_path, trial_conditions_path, output_path


def _read_raw_eeg(cnt_path: Path) -> mne.io.BaseRaw:
    raw = mne.io.read_raw_ant(cnt_path, preload=False, verbose="ERROR")
    raw.pick("eeg")
    return raw


def _read_events(cnt_path: Path) -> tuple[np.ndarray, float]:
    raw = mne.io.read_raw_ant(cnt_path, preload=False, verbose="ERROR")
    events, _ = mne.events_from_annotations(raw, verbose="ERROR")
    events = events[np.isin(events[:, 2], list(event_codes))]
    return events, float(raw.info["sfreq"])


def _build_epoch_table(events: np.ndarray, trial_conditions: pd.DataFrame) -> pd.DataFrame:
    onset_rows = np.flatnonzero(events[:, 2] == 1)
    epoch_rows = []

    for onset_row in onset_rows:
        after_onset = events[onset_row + 1 :]
        frame_rows = np.flatnonzero(after_onset[:, 2] == 3)
        offset_rows = np.flatnonzero(after_onset[:, 2] == 2)

        if len(frame_rows) == 0:
            raise ValueError(f"Missing event 3 after onset event at row {onset_row}")
        if len(offset_rows) == 0:
            raise ValueError(f"Missing event 2 after onset event at row {onset_row}")
        if frame_rows[0] > offset_rows[0]:
            raise ValueError(f"First event 3 occurs after event 2 for onset event at row {onset_row}")

        epoch_rows.append(
            {
                "trial_num": int(trial_conditions.iloc[len(epoch_rows)]["trial_num"]),
                "condition_id": int(trial_conditions.iloc[len(epoch_rows)]["condition_id"]),
                "epoch_start_sample": int(after_onset[frame_rows[0], 0]),
                "epoch_stop_sample": int(after_onset[offset_rows[0], 0]),
            }
        )

    if len(epoch_rows) != len(trial_conditions):
        raise ValueError(
            f"Derived {len(epoch_rows)} EEG epochs but found {len(trial_conditions)} trial-condition rows"
        )

    return pd.DataFrame(epoch_rows)


def _shared_cycle_samples(sfreq: float) -> int:
    cycle_blocks = []
    for frequency_hz in target_frequencies_hz:
        ratio = Fraction(str(frequency_hz)) / Fraction(str(sfreq))
        cycle_blocks.append(ratio.denominator)
    return math.lcm(*cycle_blocks)


def _extract_condition_epochs(raw: mne.io.BaseRaw, epoch_table: pd.DataFrame, condition_id: int) -> np.ndarray:
    condition_epochs = epoch_table.loc[epoch_table["condition_id"] == condition_id].reset_index(drop=True)
    if condition_epochs.empty:
        raise ValueError(f"No epochs found for condition {condition_id}")

    epoch_arrays = []
    for epoch_row in condition_epochs.itertuples(index=False):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Unit .* not recognized.*", category=RuntimeWarning)
            epoch_data = raw.get_data(start=int(epoch_row.epoch_start_sample), stop=int(epoch_row.epoch_stop_sample))
        epoch_arrays.append(epoch_data)

    min_epoch_length = min(epoch_array.shape[1] for epoch_array in epoch_arrays)
    fft_epoch_length = (min_epoch_length // _shared_cycle_samples(float(raw.info["sfreq"]))) * _shared_cycle_samples(
        float(raw.info["sfreq"])
    )
    if fft_epoch_length == 0:
        raise ValueError(f"Condition {condition_id} epochs are shorter than one shared cycle block")

    trimmed_epochs = np.stack([epoch_array[:, :fft_epoch_length] for epoch_array in epoch_arrays], axis=0)
    trimmed_epochs = trimmed_epochs - trimmed_epochs.mean(axis=2, keepdims=True)

    time_index = np.arange(fft_epoch_length, dtype=float)
    time_index = time_index - time_index.mean()
    time_scale = np.sum(time_index ** 2)
    slopes = np.sum(trimmed_epochs * time_index[None, None, :], axis=2, keepdims=True) / time_scale
    linear_trend = slopes * time_index[None, None, :]

    return trimmed_epochs - linear_trend


def _build_condition_spectrum(raw: mne.io.BaseRaw, epoch_table: pd.DataFrame, condition_id: int) -> tuple[np.ndarray, np.ndarray]:
    epochs = _extract_condition_epochs(raw, epoch_table, condition_id)
    coherent_average = epochs.mean(axis=0)
    taper = np.hanning(coherent_average.shape[1])
    fft_values = np.fft.rfft(coherent_average * taper[None, :], axis=1)
    freq_hz = np.fft.rfftfreq(epochs.shape[2], d=1.0 / float(raw.info["sfreq"]))

    if plot_channel not in raw.ch_names:
        raise ValueError(f"Channel {plot_channel} not found in EEG channels: {raw.ch_names}")

    channel_index = raw.ch_names.index(plot_channel)
    magnitude_uv = np.abs(fft_values[channel_index]) * 1e6
    keep = freq_hz <= max_plot_hz
    return freq_hz[keep], magnitude_uv[keep]


def make_final_spectra_plot(sub_id: str, ses_id: str, run_id: str) -> tuple[plt.Figure, Path]:
    cnt_path, trial_conditions_path, output_path = _find_run_paths(sub_id, ses_id, run_id)
    raw = _read_raw_eeg(cnt_path)
    events, _ = _read_events(cnt_path)
    trial_conditions = pd.read_csv(trial_conditions_path)
    epoch_table = _build_epoch_table(events, trial_conditions)
    condition_lookup = (
        trial_conditions[
            ["condition_id", "surround_condition", "modulation_mode", "upper_lower_phase_mode"]
        ]
        .drop_duplicates()
        .set_index("condition_id")
    )

    fig, axes = plt.subplots(2, 2, figsize=(18, 10), constrained_layout=True)

    for axis, condition_id in zip(axes.flat, dynamic_condition_ids, strict=False):
        freq_hz, magnitude_uv = _build_condition_spectrum(raw, epoch_table, condition_id)
        bar_width = float(freq_hz[1] - freq_hz[0]) if len(freq_hz) > 1 else 1.0
        condition_row = condition_lookup.loc[condition_id]

        axis.bar(freq_hz, magnitude_uv, width=bar_width, align="center", color="#1f5aa6", edgecolor="#1f5aa6")
        axis.set_title(
            f"{condition_row['modulation_mode']}, {condition_row['upper_lower_phase_mode']}\n"
            f"condition {condition_id}, channel {plot_channel}"
        )
        axis.set_xlabel("Frequency (Hz)")
        axis.set_ylabel("Magnitude (uV)")
        axis.set_xlim(0.0, max_plot_hz)
        axis.set_ylim(0.0, max_plot_uv)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    return fig, output_path


def main() -> Path:
    args = build_parser().parse_args()
    _, output_path = make_final_spectra_plot(args.sub_id, args.ses_id, args.run_id)
    print(f"Wrote final spectra plot to {output_path}")
    return output_path


if __name__ == "__main__":
    main()
