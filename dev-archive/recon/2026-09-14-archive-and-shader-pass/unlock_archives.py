"""Recover the Hard Reset data-archive password from YOUR OWN installed copy.

The data\\*.bin files are ordinary ZIP archives with ZipCrypto-locked entries.
The password is a plain string inside hardreset.exe. This script tries every
printable string in the exe against the smallest locked entry (Python's zipfile
checks the CRC, so a hit is a real unlock, not a lucky header byte), then
confirms the hit opens one entry in every archive.

It never prints the password and never writes it anywhere inside a repo:
pass an output path OUTSIDE the repo. Nothing extracted with it may be
committed - it is game content.

usage: python unlock_archives.py "<HardReset install dir>" <key-out-path>
"""
import glob
import os
import re
import sys
import zipfile


def candidates(exe_path):
    blob = open(exe_path, "rb").read()
    found = set(m.group().decode() for m in re.finditer(rb"[\x21-\x7e]{4,64}", blob))
    found |= set(m.group().decode("utf-16le")
                 for m in re.finditer(rb"(?:[\x21-\x7e]\x00){4,64}", blob))
    return found


def smallest_locked(zf):
    locked = [e for e in zf.infolist() if e.flag_bits & 1 and e.file_size]
    return min(locked, key=lambda e: e.compress_size)


def main():
    install, key_out = sys.argv[1], sys.argv[2]
    data = os.path.join(install, "data")
    probe = zipfile.ZipFile(os.path.join(data, "data_10_shaders.bin"))
    entry = smallest_locked(probe)

    hits = []
    for c in candidates(os.path.join(install, "hardreset.exe")):
        try:
            probe.read(entry, pwd=c.encode("latin-1"))
            hits.append(c)
        except Exception:
            pass
    print("candidate strings that unlock the probe entry:", len(hits))
    if len(hits) != 1:
        sys.exit("expected exactly one hit; stopping")
    key = hits[0].encode("latin-1")

    failed = 0
    for path in sorted(glob.glob(os.path.join(data, "*.bin"))):
        zf = zipfile.ZipFile(path)
        try:
            zf.read(smallest_locked(zf), pwd=key)
        except Exception as ex:
            failed += 1
            print("FAIL", os.path.basename(path), ex)
    print("archives the key failed on:", failed)

    with open(key_out, "w") as fh:
        fh.write(hits[0])
    print("key length", len(hits[0]), "written to", key_out)


if __name__ == "__main__":
    main()
