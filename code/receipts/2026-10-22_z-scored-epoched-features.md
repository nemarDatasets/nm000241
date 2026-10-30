# Units n/a and RecordingType epoched for the z-scored features (v1.0.3)

**Claim**: each run is per-trial z-scored 1.5 s trials back to back (units n/a, epoched); BBS = HGA + LFS channels.

**Source**
- PR head `cdc4af8ddc1a4bcfd2924e15f62da945097b098a`; data read at NEMAR nm000241 `origin/main`
  `dd83e9790defa9d055611a81a8335e8771c7a844` (upstream: Zenodo 10.5281/zenodo.13332808).
- Files: all 18 `sub-*/ieeg/*_ieeg.vhdr/.eeg` runs with their `.vmrk` and `_events.tsv`. The sha256 of each of the 36
  annexed files (`.vhdr`, `.eeg`) equals its SHA256E git-annex key at that commit.
- Manufacturer: `README.md` at that commit, "Recorded at 1000 Hz with Nihon Kohden EEG-1200"; "Brain Products" is the
  mne-bids default for `.vhdr` files and is stated by no source.

**Method**: MNE `read_raw_brainvision` (scaling applied: float32 x 0.1 µV resolution, returned in V). Each run is cut
into consecutive 300-sample trials (1.5 s at 200 Hz); mean and SD (ddof 0, float64) per trial and channel. Z-scored =
max |SD - 1| and max |mean| at float32 precision (< 1e-7). `events.tsv` checked for one 1.5 s row per trial at
k x 1.5 s. Each BBS run compared element-wise (`numpy.array_equal`) with [HGA channels; LFS channels] of the same subject
and task.

**Result**

| run | channels | samples | trials (1.5 s) | leftover samples | events.tsv rows | onset = k x 1.5 s, duration 1.5 s | max abs(SD - 1) | max abs(mean) | BBS = [HGA; LFS] |
|---|---|---|---|---|---|---|---|---|---|
| sub-1_task-chinesehga | 114 | 250800 | 836 | 0 | 836 | True | 2.2e-08 | 6.6e-09 |  |
| sub-1_task-chineselfs | 114 | 250800 | 836 | 0 | 836 | True | 1.6e-08 | 6.0e-09 |  |
| sub-1_task-chinesebbs | 228 | 250800 | 836 | 0 | 836 | True | 2.2e-08 | 6.6e-09 | True |
| sub-1_task-digithga | 114 | 126000 | 420 | 0 | 420 | True | 1.9e-08 | 6.2e-09 |  |
| sub-1_task-digitlfs | 114 | 126000 | 420 | 0 | 420 | True | 1.5e-08 | 6.4e-09 |  |
| sub-1_task-digitbbs | 228 | 126000 | 420 | 0 | 420 | True | 1.9e-08 | 6.4e-09 | True |
| sub-1_task-englishhga | 114 | 71100 | 237 | 0 | 237 | True | 2.1e-08 | 5.6e-09 |  |
| sub-1_task-englishlfs | 114 | 71100 | 237 | 0 | 237 | True | 1.2e-08 | 6.8e-09 |  |
| sub-1_task-englishbbs | 228 | 71100 | 237 | 0 | 237 | True | 2.1e-08 | 6.8e-09 | True |
| sub-2_task-chinesehga | 158 | 260400 | 868 | 0 | 868 | True | 3.7e-08 | 5.8e-09 |  |
| sub-2_task-chineselfs | 158 | 260400 | 868 | 0 | 868 | True | 1.4e-08 | 6.6e-09 |  |
| sub-2_task-chinesebbs | 316 | 260400 | 868 | 0 | 868 | True | 3.7e-08 | 6.6e-09 | True |
| sub-2_task-digithga | 158 | 144000 | 480 | 0 | 480 | True | 3.3e-08 | 6.9e-09 |  |
| sub-2_task-digitlfs | 158 | 144000 | 480 | 0 | 480 | True | 1.4e-08 | 6.5e-09 |  |
| sub-2_task-digitbbs | 316 | 144000 | 480 | 0 | 480 | True | 3.3e-08 | 6.9e-09 | True |
| sub-2_task-englishhga | 158 | 68400 | 228 | 0 | 228 | True | 2.9e-08 | 6.3e-09 |  |
| sub-2_task-englishlfs | 158 | 68400 | 228 | 0 | 228 | True | 1.2e-08 | 6.2e-09 |  |
| sub-2_task-englishbbs | 316 | 68400 | 228 | 0 | 228 | True | 2.9e-08 | 6.3e-09 | True |

Totals: 3069 trials per feature. Every trial of every channel has SD 1 and mean 0 in the reader's units (under the old
µV label, an SD of 10^6 µV), so the 3264 channel rows of the 18 `channels.tsv` get units n/a (the only column changed)
and the 18 `ieeg.json` get `RecordingType` epoched.

**Coverage**: 18 of 18 runs (3 features x 3 tasks x 2 subjects), all channels, all trials.

Reproduce: `python code/receipts/2026-10-22_z-scored-epoched-features.py <nm000241 root>` (Python 3.15.0, MNE 1.13.2,
numpy 2.5.4).
