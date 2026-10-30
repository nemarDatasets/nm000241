import argparse
import pathlib
import platform

import mne
import numpy as np
import pandas as pd

TRIAL_S = 1.5

parser = argparse.ArgumentParser()
parser.add_argument("root", type=pathlib.Path, help="nm000241 BIDS root")
root = parser.parse_args().root
print(f"Python {platform.python_version()}, MNE {mne.__version__}, numpy {np.__version__}\n")

rows = []
for hga_vhdr in sorted(root.glob("sub-*/ieeg/*hga_ieeg.vhdr")):
    stem = hga_vhdr.name.removesuffix("hga_ieeg.vhdr")
    data = {}
    for feature in ("hga", "lfs", "bbs"):
        vhdr = hga_vhdr.with_name(f"{stem}{feature}_ieeg.vhdr")
        raw = mne.io.read_raw_brainvision(vhdr, preload=True, verbose="error")
        x = raw.get_data()  # MNE scaling applied: float32 x 0.1 µV resolution -> V
        data[feature] = x
        n_trial = round(TRIAL_S * raw.info["sfreq"])
        n_trials, leftover = divmod(x.shape[1], n_trial)
        trials = x[:, : n_trials * n_trial].reshape(len(x), n_trials, n_trial)
        events = pd.read_csv(vhdr.with_name(f"{stem}{feature}_events.tsv"), sep="\t")
        rows.append(
            {
                "run": f"{stem}{feature}",
                "channels": len(x),
                "samples": x.shape[1],
                "trials (1.5 s)": n_trials,
                "leftover samples": leftover,
                "events.tsv rows": len(events),
                "onset = k x 1.5 s, duration 1.5 s": bool(
                    np.allclose(events.onset, np.arange(len(events)) * TRIAL_S)
                    and np.allclose(events.duration, TRIAL_S)
                ),
                "max abs(SD - 1)": f"{np.abs(trials.std(axis=-1) - 1).max():.1e}",
                "max abs(mean)": f"{np.abs(trials.mean(axis=-1)).max():.1e}",
                "BBS = [HGA; LFS]": "",
            }
        )
    rows[-1]["BBS = [HGA; LFS]"] = str(np.array_equal(data["bbs"], np.vstack([data["hga"], data["lfs"]])))

table = pd.DataFrame(rows)
print("| " + " | ".join(table.columns) + " |\n|" + "---|" * len(table.columns))
for row in table.itertuples(index=False):
    print("| " + " | ".join(map(str, row)) + " |")
for feature in ("hga", "lfs", "bbs"):
    print(f"\n{feature}: {table[table.run.str.endswith(feature)]['trials (1.5 s)'].sum()} trials in total")
