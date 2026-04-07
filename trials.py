import random
from config import (
    center_oris,
    surround_oris,
    left_center_contrast,
    right_center_contrast,
    left_surround_contrast,
    right_surround_contrast,
)

# ----------------------------
# trial configuration
# ----------------------------


def get_cs_type(surround_ori, cs_plus_ori=45):
    if surround_ori is None:
        return "none"
    elif surround_ori == cs_plus_ori:
        return "CS+"
    else:
        return "CS-"


def make_trial(
    phase,
    center_ori,
    surround_ori,
    left_center_contrast,
    right_center_contrast,
    left_surround_contrast,
    right_surround_contrast,
    reinforced=0,
):
    return {
        "phase": phase,
        "center_ori": center_ori,
        "surround_ori": surround_ori,
        "surround_present": int(surround_ori is not None),
        "cs_type": get_cs_type(surround_ori),
        "reinforced": reinforced,
        "left_center_contrast": left_center_contrast,
        "right_center_contrast": right_center_contrast,
        "left_surround_contrast": left_surround_contrast,
        "right_surround_contrast": right_surround_contrast,
    }


def generate_habituation_trials():
    trials = []

    for center_ori in center_oris:
        for surround_ori in surround_oris:
            for _ in range(6):
                trials.append(
                    make_trial(
                        phase="habituation",
                        center_ori=center_ori,
                        surround_ori=surround_ori,
                        left_center_contrast=left_center_contrast,
                        right_center_contrast=right_center_contrast,
                        left_surround_contrast=left_surround_contrast,
                        right_surround_contrast=right_surround_contrast,
                    )
                )

    random.shuffle(trials)
    return trials


def generate_acquisition_trials():
    trials = []

    for center_ori in center_oris:
        for surround_ori in surround_oris:
            reps = 3 if surround_ori is None else 6

            for _ in range(reps):
                trials.append(
                    make_trial(
                        phase="acquisition",
                        center_ori=center_ori,
                        surround_ori=surround_ori,
                        left_center_contrast=left_center_contrast,
                        right_center_contrast=right_center_contrast,
                        left_surround_contrast=left_surround_contrast,
                        right_surround_contrast=right_surround_contrast,
                        reinforced=0,
                    )
                )

    cs_plus_indices = [i for i, t in enumerate(trials) if t["cs_type"] == "CS+"]
    n_reinforced = int(len(cs_plus_indices) * 0.5)
    reinforced_indices = set(random.sample(cs_plus_indices, n_reinforced))

    for i in reinforced_indices:
        trials[i]["reinforced"] = 1

    random.shuffle(trials)
    return trials
