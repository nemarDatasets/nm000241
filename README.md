[![DOI](https://img.shields.io/badge/DOI-10.82901%2Fnemar.nm000241-blue)](https://doi.org/10.82901/nemar.nm000241)

CerebroVoice: Bilingual sEEG Speech Dataset
=============================================

Overview
--------
Intracranial EEG (sEEG) recordings from 2 epilepsy patients during bilingual
speech tasks (Mandarin Chinese, English, and digit reading). Recorded at
1000 Hz with Nihon Kohden EEG-1200, depth electrodes (platinum-iridium).

Data distributed as preprocessed NPY derivatives:
- LFS: Low-frequency signal
- HGA: High-gamma activity
- BBS: Broadband signal

Tasks: Chinese reading, English reading, digit reading
Subjects: SUB1 (114 channels post-filtering), SUB2 (158 channels)
Duration: ~73 min (SUB1), ~76 min (SUB2)

Source: Zenodo (doi:10.5281/zenodo.13332808)
License: CC BY 4.0


References
----------
Appelhoff, S., Sanderson, M., Brooks, T., Vliet, M., Quentin, R., Holdgraf, C., Chaumon, M., Mikulan, E., Tavabi, K., Höchenberger, R., Welke, D., Brunner, C., Rockhill, A., Larson, E., Gramfort, A. and Jas, M. (2019). MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. Journal of Open Source Software 4: (1896).https://doi.org/10.21105/joss.01896

Holdgraf, C., Appelhoff, S., Bickel, S., Bouchard, K., D'Ambrosio, S., David, O., … Hermes, D. (2019). iEEG-BIDS, extending the Brain Imaging Data Structure specification to human intracranial electrophysiology. Scientific Data, 6, 102. https://doi.org/10.1038/s41597-019-0105-7


Notes (fix-20261030: BrainVision headers and EpochLength)
---------------------------------------------------------
- The 18 BrainVision headers (`_ieeg.vhdr`) now declare every channel as unit `n/a` with resolution `1e-07`
  (previously `0.1` µV), matching `units` n/a in `channels.tsv`: the features are per-trial z-scores without a physical
  unit. MNE scales unit `n/a` by 1, so `mne.io.read_raw_brainvision` and `mne_bids.read_raw_bids` return the same sample
  values as before (stored value x 1e-07; SD 1 within each trial). Only the resolution and unit fields of the channel
  lines changed, plus one comment line; the `.eeg` and `.vmrk` files are unchanged. Script:
  `code/fix-20261030_vhdr_units.py`.
- `EpochLength` 1.5 (s) was added to the 18 `_ieeg.json`: in the Zenodo release each trial is a separate
  `*_SEEG.npy` array of 300 samples x channels (1.5 s at 200 Hz, with a 1.5 s audio clip per trial), and the runs
  hold these trials back to back.
