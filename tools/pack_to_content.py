#!/usr/bin/env python3
import json
import os
import sys
import zipfile
from pathlib import PurePosixPath

DEFAULT_VERSION = "0.1.0"
FIXED_TIME = (2026, 1, 1, 0, 0, 0)

MANIFEST = """id = "{mod_id}"
name = "{name}"
version = "{version}"
description = "{description}"
authors = [{authors}]
api = "0.2"
side = "client"
capabilities = ["registries"]
namespaces = []
"""


def read_pack(src):
    if os.path.isdir(src):
        for root, _, files in os.walk(src):
            for name in files:
                full = os.path.join(root, name)
                rel = os.path.relpath(full, src).replace(os.sep, "/")
                with open(full, "rb") as fh:
                    yield rel, fh.read()
    else:
        with zipfile.ZipFile(src) as zf:
            for info in zf.infolist():
                if not info.is_dir():
                    yield info.filename, zf.read(info.filename)


def rewrite_model(data, source, mod_id):
    model = json.loads(data)
    textures = model.get("textures")
    if isinstance(textures, dict):
        for key, value in textures.items():
            if not isinstance(value, str) or ":" not in value:
                continue
            ns, path = value.split(":", 1)
            if ns == "minecraft":
                raise SystemExit(f"{source}: texture '{value}' is vanilla; it cannot move into the mod")
            textures[key] = f"{mod_id}:{ns}/{path}"
    return (json.dumps(model, indent=2) + "\n").encode()


def convert(src, out, version=DEFAULT_VERSION, mod_id="mymod"):
    entries = {}
    for rel, data in sorted(dict(read_pack(src)).items()):
        parts = PurePosixPath(rel).parts
        if len(parts) < 5 or parts[0] != "assets" or parts[2] not in ("models", "textures"):
            continue
        ns, kind = parts[1], parts[2]
        inner = PurePosixPath(*parts[3:]).as_posix()
        if kind == "models" and inner.endswith(".json"):
            entries[f"assets/{mod_id}/models/{ns}/{inner}"] = rewrite_model(data, rel, mod_id)
        elif kind == "textures" and inner.endswith(".png"):
            entries[f"assets/{mod_id}/textures/{ns}/{inner}"] = data

    missing = []
    for target, body in entries.items():
        if "/models/" not in target:
            continue
        for ref in json.loads(body).get("textures", {}).values():
            if isinstance(ref, str) and ref.startswith(mod_id + ":"):
                path = ref[len(mod_id) + 1:]
                if f"assets/{mod_id}/textures/{path}.png" not in entries:
                    missing.append(ref)
    if missing:
        raise SystemExit("missing textures: " + ", ".join(sorted(set(missing))[:10]))
    if not entries:
        raise SystemExit(f"{src}: no models or textures found under assets/")

    authors = ", ".join(json.dumps(a.strip()) for a in os.environ.get("MOD_AUTHORS", "").split(",") if a.strip())
    manifest = MANIFEST.format(
        mod_id=mod_id,
        version=version,
        name=os.environ.get("MOD_NAME", f"{mod_id} frames"),
        description=os.environ.get("MOD_DESCRIPTION", f"Textures and models for {mod_id}, moved from a pack."),
        authors=authors,
    )
    entries["horizon-mod.toml"] = manifest.encode()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, entries[name])
    print(f"wrote {out}: {len(entries)} files")


if __name__ == "__main__":
    if not 3 <= len(sys.argv) <= 6:
        sys.exit(__doc__)
    convert(sys.argv[1], sys.argv[2], *sys.argv[3:5])
