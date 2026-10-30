"""nm000241 fix-20261030: rewrite the unit field of the 18 BrainVision headers (_ieeg.vhdr) from 0.1 µV to n/a.

The features in this dataset are z-scored per 1.5 s trial (see code/receipts/2026-10-22_z-scored-epoched-features.md
on Julien Gadonneix's PR #3: channels.tsv units n/a), so they have no physical unit. The version 1.0.2 headers declared
every channel as `Ch<n>=<name>,,0.1,µV`. MNE (mne/io/brainvision/brainvision.py, `_unit_dict`: "µV": 1e-6,
"n/a": 1) returns stored value x resolution x unit factor, i.e. stored x 0.1 x 1e-6 = stored x 1e-07 with the old
header. The new header writes `Ch<n>=<name>,,1e-07,n/a`, which MNE reads as stored x 1e-07 x 1: the same float64
calibration (0.1 * 1e-6 == 1e-07 exactly), so the sample values returned by MNE (the z-scores, SD 1 per trial) do
not change. Only the resolution and unit fields of the Ch<n> lines change, plus one ';' comment line before Ch1.
The .eeg and .vmrk files are not touched.

Usage: python code/fix-20261030_vhdr_units.py <dir holding the version 1.0.2 sub-*/ieeg/*_ieeg.vhdr> <output dir>
The input headers are checked against their git-annex SHA256 keys of version 1.0.2 (commit dd83e97).
"""
import hashlib
import os
import re
import sys

# sha256 of the 18 version 1.0.2 headers (git-annex SHA256E keys at commit dd83e97)
OLD_SHA256 = {
    "sub-1/ieeg/sub-1_task-chinesebbs_ieeg.vhdr": "f976df0ad6650e5a13a521280abc4157e2db21b1921fca1872c8fdb6799b0a1c",
    "sub-1/ieeg/sub-1_task-chinesehga_ieeg.vhdr": "5682963ae3a6d436516d0e185b7b67c7376f52bc5082096aeea4ea201331bd9f",
    "sub-1/ieeg/sub-1_task-chineselfs_ieeg.vhdr": "8f06858a56b62e32368ba50bbe1da2ce45ef644ab6661ba0410c3ed149cef075",
    "sub-1/ieeg/sub-1_task-digitbbs_ieeg.vhdr": "d4232be0bb0e7edf524d59dd03ea31c52ade0dcf13d93b082122a6dd28be8e12",
    "sub-1/ieeg/sub-1_task-digithga_ieeg.vhdr": "19a52e5740b788dd51b38e91cd3b77996927c06778eabcf85f9f71c6e39b7f29",
    "sub-1/ieeg/sub-1_task-digitlfs_ieeg.vhdr": "393c3daff5106f3123483c206992e045c72f373a9772743fbc5441431d52fcab",
    "sub-1/ieeg/sub-1_task-englishbbs_ieeg.vhdr": "5fe700fb8d12ca58928e19579316aa142a825d3ee46a8e1a0387e5f522b240c6",
    "sub-1/ieeg/sub-1_task-englishhga_ieeg.vhdr": "a9cd63fae6e0f4ffd449802816212d969a6716b76d50ab0f678dfad6a11487a1",
    "sub-1/ieeg/sub-1_task-englishlfs_ieeg.vhdr": "a0172e7d9312c0bcc0caaf8baae6828c0436e219e09eb206db9636d1e2101dc8",
    "sub-2/ieeg/sub-2_task-chinesebbs_ieeg.vhdr": "e1ab7fea43fbd8b6a8c0f941430f5c4261565821c78400784ff7de3392019da5",
    "sub-2/ieeg/sub-2_task-chinesehga_ieeg.vhdr": "40d53e050c860a76f9d891235157b75b8a6a6e4994c8bc2f3c3e47e6de33a1ce",
    "sub-2/ieeg/sub-2_task-chineselfs_ieeg.vhdr": "50c5a26e31623e2c612c2d6c30b7d372bcca47f43778f8a7b996e83f4dae2af1",
    "sub-2/ieeg/sub-2_task-digitbbs_ieeg.vhdr": "abfb97a14aaae35e43f1f8d19c64acf9256b5f01a2893d465a9893100a94575b",
    "sub-2/ieeg/sub-2_task-digithga_ieeg.vhdr": "dbbaa08ccd1d146123becf9c55d9e57640dca8473d172d3f027508b682085876",
    "sub-2/ieeg/sub-2_task-digitlfs_ieeg.vhdr": "1323a06bf1c5ba37d419bc9c2ef3e535c0c8c5a6767dba68259a11368fb94fe3",
    "sub-2/ieeg/sub-2_task-englishbbs_ieeg.vhdr": "02d8d03db6d545b456fd92215e2acc15d6e4b7e228614ffa23dcb48e6de44ef1",
    "sub-2/ieeg/sub-2_task-englishhga_ieeg.vhdr": "e29a4ee2eb282ffc220b70f8b5b18c34f1ea89c8621b621533226caae0109e61",
    "sub-2/ieeg/sub-2_task-englishlfs_ieeg.vhdr": "e06c96ab0ed28d3583f62217197caf991ea641e6e452dc547edd010b47a4926d",
}

COMMENT = ("; nm000241 fix-20261030: the values are per-trial z-scores without a physical unit (channels.tsv "
           "units n/a); unit n/a with resolution 1e-07 keeps the values MNE returned with the former 0.1 µV "
           "header (stored value x 1e-07)\n")
CH = re.compile(r"^(Ch\d+=[^,\n]*,[^,\n]*),0\.1,µV$")


def convert(text):
    lines = text.split("\n")
    out, n, inserted = [], 0, False
    for line in lines:
        m = CH.match(line)
        if line.startswith("Ch") and "=" in line and not m:
            raise ValueError(f"unexpected channel line: {line!r}")
        if m:
            if not inserted:
                out.append(COMMENT.rstrip("\n"))
                inserted = True
            out.append(f"{m.group(1)},1e-07,n/a")
            n += 1
        else:
            out.append(line)
    return "\n".join(out), n


def main(src, dst):
    done = 0
    for rel, digest in sorted(OLD_SHA256.items()):
        raw = open(os.path.join(src, rel), "rb").read()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise SystemExit(f"{rel}: sha256 differs from the version 1.0.2 key")
        new, n = convert(raw.decode("utf-8"))
        os.makedirs(os.path.dirname(os.path.join(dst, rel)), exist_ok=True)
        with open(os.path.join(dst, rel), "w", encoding="utf-8", newline="") as f:
            f.write(new)
        print(f"{rel}: {n} channel lines -> 1e-07,n/a")
        done += 1
    print(f"{done} headers written")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
