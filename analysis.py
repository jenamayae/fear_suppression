from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd

from config import center_flicker_hz, stimulus_onset_code, trial_duration


def extract_events(raw: mne.io.BaseRaw) -> pd.DataFrame:
    events, event_id = mne.events_from_annotations(raw, verbose="ERROR")
    code_to_label = {code: label for label, code in event_id.items()}

    event_table = pd.DataFrame(
        {
            "event_index": np.arange(len(events), dtype=int),
            "sample": events[:, 0].astype(int),
            "code": events[:, 2].astype(int),
        }
    )
    event_table["time_s"] = event_table["sample"] / raw.info["sfreq"]
    event_table["label"] = event_table["code"].map(code_to_label)

    return event_table
    

def read_trial_conditions(path: str | Path) -> pd.DataFrame:
    trial_table = pd.read_csv(path)

    # PsychoPy writes an empty trailing column.
    trial_table = trial_table.loc[:, ~trial_table.columns.str.startswith("Unnamed")]
    if "" in trial_table.columns:
        trial_table = trial_table.drop(columns="")

    return trial_table


def map_trial_conditions_to_onsets(
    event_table: pd.DataFrame,
    trial_table: pd.DataFrame,
    onset_code: int = stimulus_onset_code,
) -> pd.DataFrame:
    onset_events = (
        event_table.loc[event_table["code"] == onset_code]
        .reset_index(drop=True)
        .copy()
    )

    if len(onset_events) != len(trial_table):
        raise ValueError(
            f"Found {len(onset_events)} onset events but {len(trial_table)} trial rows."
        )

    mapped_table = trial_table.copy().reset_index(drop=True)
    mapped_table["stimulus_onset_sample"] = onset_events["sample"]
    mapped_table["stimulus_onset_time_s"] = onset_events["time_s"]

    return mapped_table


def make_epoch_table(
    trial_table: pd.DataFrame,
    sfreq: float,
    trial_duration_s: float = trial_duration,
    combined_cycle_frames: int = 80,
    refresh_hz: float | None = None,
) -> pd.DataFrame:
    epoch_table = trial_table.copy()
    trial_duration_samples = round(trial_duration_s * sfreq)

    if "refresh_hz" in epoch_table.columns:
        refresh_hz_by_trial = pd.to_numeric(epoch_table["refresh_hz"])
    elif refresh_hz is not None:
        refresh_hz_by_trial = pd.Series(refresh_hz, index=epoch_table.index, dtype=float)
    else:
        raise ValueError("Need refresh_hz from the trial table or as a function argument.")

    combined_cycle_samples = (
        (combined_cycle_frames / refresh_hz_by_trial) * sfreq
    ).round().astype(int)

    epoch_table["epoch_start_sample"] = (
        epoch_table["stimulus_onset_sample"] + combined_cycle_samples
    )
    epoch_table["epoch_stop_sample"] = (
        epoch_table["stimulus_onset_sample"] + trial_duration_samples
    )
    epoch_table["epoch_start_time_s"] = epoch_table["epoch_start_sample"] / sfreq
    epoch_table["epoch_stop_time_s"] = epoch_table["epoch_stop_sample"] / sfreq
    epoch_table["epoch_duration_s"] = (
        epoch_table["epoch_stop_sample"] - epoch_table["epoch_start_sample"]
    ) / sfreq

    if (epoch_table["epoch_stop_sample"] <= epoch_table["epoch_start_sample"]).any():
        raise ValueError("At least one epoch has non-positive duration.")

    return epoch_table


def extract_epoch_data(
    raw: mne.io.BaseRaw,
    epoch_table: pd.DataFrame,
    picks: str | list[str] = "eeg",
) -> tuple[np.ndarray, np.ndarray]:
    data = raw.get_data(picks=picks)
    sfreq = raw.info["sfreq"]

    epochs = []
    for row in epoch_table.itertuples(index=False):
        start = int(row.epoch_start_sample)
        stop = int(row.epoch_stop_sample)
        epochs.append(data[:, start:stop])

    epoch_lengths = np.array([epoch.shape[1] for epoch in epochs], dtype=int)
    if len(epoch_lengths) == 0:
        raise ValueError("No epochs were extracted.")
    if not np.all(epoch_lengths == epoch_lengths[0]):
        raise ValueError("Epoch lengths are not identical.")

    epoch_data = np.stack(epochs, axis=0)
    times_s = np.arange(epoch_data.shape[-1]) / sfreq

    return epoch_data, times_s


def compute_ffts(epoch_data: np.ndarray, sfreq: float) -> tuple[np.ndarray, np.ndarray]:
    fft_complex = np.fft.rfft(epoch_data, axis=-1)
    fft_amplitude = np.abs(fft_complex) / epoch_data.shape[-1]
    freqs_hz = np.fft.rfftfreq(epoch_data.shape[-1], d=1.0 / sfreq)

    return freqs_hz, fft_amplitude


def compute_center_tag_rms(
    freqs_hz: np.ndarray,
    fft_amplitude: np.ndarray,
    trial_table: pd.DataFrame,
    ch_names: list[str],
    center_tag_hz: float = center_flicker_hz,
) -> pd.DataFrame:
    center_freq_idx = int(np.argmin(np.abs(freqs_hz - center_tag_hz)))
    center_freq_hz = float(freqs_hz[center_freq_idx])

    if fft_amplitude.ndim != 3:
        raise ValueError(
            "fft_amplitude must have shape (n_trials, n_channels, n_freqs)."
        )

    n_trials, n_channels, _ = fft_amplitude.shape

    if len(trial_table) != n_trials:
        raise ValueError(
            f"Found {n_trials} FFT trials but {len(trial_table)} trial rows."
        )

    if len(ch_names) != n_channels:
        raise ValueError(
            f"Found {n_channels} FFT channels but {len(ch_names)} channel names."
        )

    rms_rows = []
    for trial_idx in range(n_trials):
        trial_row = trial_table.iloc[trial_idx].to_dict()

        for channel_idx, channel_name in enumerate(ch_names):
            rms_row = trial_row.copy()
            rms_row["channel"] = channel_name
            rms_row["center_tag_target_hz"] = center_tag_hz
            rms_row["center_tag_bin_hz"] = center_freq_hz
            rms_row["center_tag_rms"] = float(
                fft_amplitude[trial_idx, channel_idx, center_freq_idx]
            )
            rms_rows.append(rms_row)

    return pd.DataFrame(rms_rows)


def summarize_center_tag_rms_for_plot(
    center_tag_rms_table: pd.DataFrame,
    channels: list[str] | None = None,
) -> pd.DataFrame:
    plot_table = center_tag_rms_table.copy()

    if channels is not None:
        plot_table = plot_table.loc[plot_table["channel"].isin(channels)].copy()

    if len(plot_table) == 0:
        raise ValueError("No rows available for plotting after channel selection.")

    summary_table = (
        plot_table.groupby(
            ["modulation_mode", "upper_lower_phase_mode", "surround_ori"],
            dropna=False,
        )["center_tag_rms"]
        .mean()
        .reset_index()
    )

    return summary_table


def plot_center_tag_rms_by_condition(
    center_tag_rms_table: pd.DataFrame,
    channels: list[str] | None = None,
    ax_by_panel: np.ndarray | None = None,
) -> tuple[plt.Figure, np.ndarray, pd.DataFrame]:
    if channels is None:
        channels = ["Oz"]

    summary_table = summarize_center_tag_rms_for_plot(
        center_tag_rms_table,
        channels=channels,
    )

    panel_conditions = [
        ("phase_reversal", "synchronized"),
        ("phase_reversal", "offset"),
        ("on_off_flicker", "synchronized"),
        ("on_off_flicker", "offset"),
    ]
    surround_order = ["None", "45", "315"]
    surround_labels = ["None", "45", "315"]

    if ax_by_panel is None:
        fig, ax_by_panel = plt.subplots(2, 2, figsize=(10, 8), sharey=True)
    else:
        fig = ax_by_panel.flat[0].figure

    flat_axes = np.asarray(ax_by_panel).ravel()

    for ax, (modulation_mode, upper_lower_phase_mode) in zip(flat_axes, panel_conditions):
        panel_table = summary_table.loc[
            (summary_table["modulation_mode"] == modulation_mode)
            & (summary_table["upper_lower_phase_mode"] == upper_lower_phase_mode)
        ].copy()

        panel_table["surround_ori"] = panel_table["surround_ori"].astype(str)
        panel_table = panel_table.set_index("surround_ori").reindex(surround_order)

        bar_heights = panel_table["center_tag_rms"].to_numpy(dtype=float)
        x = np.arange(len(surround_order))

        ax.bar(x, bar_heights, color=["0.75", "0.45", "0.25"])
        ax.set_xticks(x, surround_labels)
        ax.set_xlabel("surround_ori")
        ax.set_ylabel("center_tag_rms")
        ax.set_title(f"{modulation_mode}, {upper_lower_phase_mode}")

    fig.tight_layout()

    return fig, ax_by_panel, summary_table


def run_first_pass_analysis(
    cnt_path: str | Path,
    trial_duration_s: float = trial_duration,
    combined_cycle_frames: int = 80,
    picks: str | list[str] = "eeg",
) -> dict[str, object]:
    cnt_path = Path(cnt_path)
    rawdata_dir = cnt_path.parent
    ses_dir = rawdata_dir.parent
    metadata_dir = ses_dir / "metadata"
    derivatives_dir = ses_dir / "derivatives"
    run_id = cnt_path.stem.split("_run-")[1].split("_")[0]
    trial_conditions_path = metadata_dir / f"trial_conditions_run-{run_id}.csv"

    raw = mne.io.read_raw_ant(cnt_path, preload=True, verbose="ERROR")
    event_table = extract_events(raw)
    trial_table = read_trial_conditions(trial_conditions_path)
    trial_event_table = map_trial_conditions_to_onsets(event_table, trial_table)
    epoch_table = make_epoch_table(
        trial_event_table,
        sfreq=raw.info["sfreq"],
        trial_duration_s=trial_duration_s,
        combined_cycle_frames=combined_cycle_frames,
    )
    epoch_data, epoch_times_s = extract_epoch_data(raw, epoch_table, picks=picks)
    freqs_hz, fft_amplitude = compute_ffts(epoch_data, sfreq=raw.info["sfreq"])
    picked_ch_names = raw.copy().pick(picks).ch_names
    center_tag_rms_table = compute_center_tag_rms(
        freqs_hz,
        fft_amplitude,
        epoch_table,
        ch_names=picked_ch_names,
    )
    center_tag_rms_fig, _, center_tag_rms_summary_table = plot_center_tag_rms_by_condition(
        center_tag_rms_table,
        channels=["Oz"],
    )

    derivatives_dir.mkdir(parents=True, exist_ok=True)
    event_table.to_csv(derivatives_dir / "event_table.csv", index=False)
    trial_event_table.to_csv(derivatives_dir / "trial_event_table.csv", index=False)
    epoch_table.to_csv(derivatives_dir / "epoch_table.csv", index=False)
    center_tag_rms_table.to_csv(derivatives_dir / "center_tag_rms_table.csv", index=False)
    center_tag_rms_summary_table.to_csv(
        derivatives_dir / "center_tag_rms_summary_table.csv",
        index=False,
    )
    center_tag_rms_fig.savefig(
        derivatives_dir / "center_tag_rms_by_condition.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(center_tag_rms_fig)

    return {
        "raw": raw,
        "event_table": event_table,
        "trial_table": trial_table,
        "trial_event_table": trial_event_table,
        "epoch_table": epoch_table,
        "epoch_data": epoch_data,
        "epoch_times_s": epoch_times_s,
        "freqs_hz": freqs_hz,
        "fft_amplitude": fft_amplitude,
        "center_tag_rms_table": center_tag_rms_table,
        "center_tag_rms_summary_table": center_tag_rms_summary_table,
        "cnt_path": cnt_path,
        "trial_conditions_path": trial_conditions_path,
        "derivatives_dir": derivatives_dir,
    }
