import json
import pathlib
import sys
import zipfile

ROOT = "resourcepacks/supporteatinganimation"
RESOURCES = "src/main/resources/"
MODEL_DIR = "assets/minecraft/models/item/"
MOD_TEXTURES = "assets/eatinganimationid/textures/item/"
USAGE = "usage: python3 tools/make_frame_pack.py <EatingAnimation download (zip or folder)> <out.zip>"


def is_frame(path):
    if "/models/item/" in path:
        return "_eating_" in path or "_drinking_" in path
    return "/textures/" in path and path.endswith((".png", ".png.mcmeta"))


def read_files(src):
    if src.is_dir():
        return {p.relative_to(src).as_posix(): p.read_bytes() for p in src.rglob("*") if p.is_file()}
    with zipfile.ZipFile(src) as z:
        return {n: z.read(n) for n in z.namelist() if not n.endswith("/")}


def sources(src):
    files = {}
    for name, data in read_files(src).items():
        i = name.find(RESOURCES)
        if i >= 0:
            files[name[i + len(RESOURCES):]] = data
    if f"{ROOT}/pack.mcmeta" not in files:
        raise SystemExit(f"{src} has no {RESOURCES}{ROOT}/pack.mcmeta; is it the EatingAnimation download?")
    for name, data in files.items():
        if name == f"{ROOT}/pack.mcmeta":
            yield "pack.mcmeta", data
        elif name.startswith(f"{ROOT}/assets/") and is_frame(name[len(f"{ROOT}/assets/"):]):
            yield name[len(f"{ROOT}/"):], data
        elif name.startswith(MOD_TEXTURES) and name.endswith(".png"):
            yield name, data
        elif name.startswith(MODEL_DIR) and is_frame(name):
            yield name, data


def check(out):
    with zipfile.ZipFile(out) as z:
        names = set(z.namelist())
        missing = []
        for name in sorted(names):
            if not (name.startswith(MODEL_DIR) and name.endswith(".json") and is_frame(name)):
                continue
            for slot, ref in json.loads(z.read(name)).get("textures", {}).items():
                ns, _, path = ref.partition(":")
                if not path:
                    ns, path = "minecraft", ref
                if f"assets/{ns}/textures/{path}.png" not in names:
                    missing.append(f"{name}: {slot} -> {ref}")
    if missing:
        raise SystemExit("textures missing from the pack:\n  " + "\n  ".join(missing))


def main():
    if len(sys.argv) != 3:
        raise SystemExit(USAGE)
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in sources(src):
            z.writestr(name, data)
            count += 1
    check(out)
    print(f"{out}: {count} files, every frame texture present")


if __name__ == "__main__":
    main()
