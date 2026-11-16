#!/usr/bin/env python3
"""Render source templates for a NEW installation with credentials outside Git.

Never use this to overwrite an existing deployment's SIP accounts before its
softphones have been coordinated. The Live overlay uses the existing configs.
"""

import argparse
import os
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3] / "src" / "asterisk_pbx"
    outputs = {}
    for name in ("pjsip.conf", "manager.conf"):
        content = (root / name).read_text(encoding="utf-8")
        for key in re.findall(r"@@([A-Z0-9_]+)@@", content):
            value = os.getenv(key, "")
            if len(value) < 16 or not re.fullmatch(r"[A-Za-z0-9_!@%+=./-]+", value):
                parser.error(f"Set {key} to a valid secret of at least 16 characters")
            content = content.replace("@@" + key + "@@", value)
        outputs[name] = content
    args.output_directory.mkdir(parents=True, mode=0o750, exist_ok=True)
    for name, content in outputs.items():
        path = args.output_directory / name
        # Do not overwrite the active configuration by accident.
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o640)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)


if __name__ == "__main__":
    main()
