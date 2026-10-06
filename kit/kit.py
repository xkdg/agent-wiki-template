#!/usr/bin/env python3
"""agent-wiki-template: развернуть кит в проекте и обновлять его ядро.

Запускается из клона кита (полного, не --depth 1: sync читает прошлые версии из истории git):

    python kit/kit.py init   --project <корень проекта> [--ref <коммит|тег>]
    python kit/kit.py sync   --project <корень проекта> [--ref ...] [--dry-run]
    python kit/kit.py status --project <корень проекта>
    python kit/kit.py stamp  --project <корень проекта> [--ref ...]
    python kit/kit.py take   --project <корень проекта> --path <файл ядра> [--path ...] [--ref ...]

Состав и тип файлов — kit/MANIFEST: core перезаписывается при sync, если в проекте его не правили;
seed создаётся один раз при init и дальше принадлежит проекту. Версия кита в проекте —
wiki/.kit-version. Только стандартная библиотека Python 3.8+ и git.
"""
import argparse
import difflib
import subprocess
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[1]
STAMP = "wiki/.kit-version"
SOURCE = "https://github.com/xkdg/agent-wiki-template"
DIFF_LIMIT = 120  # строк на один diff в отчёте


def git(*args, check=True):
    r = subprocess.run(["git", "-C", str(KIT_ROOT), *args], capture_output=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r


def resolve(ref):
    return git("rev-parse", "--verify", f"{ref}^{{commit}}").stdout.decode().strip()


def read_at(sha, relpath):
    """Содержимое файла кита на коммите или None, если его там нет."""
    r = git("show", f"{sha}:{relpath}", check=False)
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def manifest_at(sha):
    text = read_at(sha, "kit/MANIFEST")
    if text is None:
        return {}
    entries = {}
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            kind, path = line.split(None, 1)
            entries[path.strip()] = kind
    return entries


def version_at(sha):
    return (read_at(sha, "kit/VERSION") or "?").strip()


def norm(text):
    return None if text is None else text.replace("\r\n", "\n")


def read_project(project, relpath):
    """Файл проекта как текст; BOM снимается — иначе файл ядра навсегда «правлен в проекте»."""
    p = project / relpath
    if not p.exists():
        return None
    try:
        return p.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError:
        sys.exit(f"{relpath}: не UTF-8 — пересохранить в UTF-8 и повторить.")


def write_project(project, relpath, content, like=None):
    """Пишет файл; если прежняя версия была с CRLF — сохраняет CRLF."""
    p = project / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    content = norm(content)
    if like is not None and "\r\n" in like:
        content = content.replace("\n", "\r\n")
    p.write_bytes(content.encode("utf-8"))


def read_stamp(project):
    p = project / STAMP
    if not p.exists():
        return None
    fields = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return fields


def write_stamp(project, sha):
    write_project(project, STAMP, f"ref: {sha}\nversion: {version_at(sha)}\nsource: {SOURCE}\n")


def diff(a, b, label_a, label_b):
    lines = list(difflib.unified_diff(norm(a or "").splitlines(), norm(b or "").splitlines(),
                                      label_a, label_b, lineterm=""))
    if len(lines) > DIFF_LIMIT:
        lines = lines[:DIFF_LIMIT] + [f"... ещё {len(lines) - DIFF_LIMIT} строк"]
    return "\n".join(lines)


def cmd_init(project, ref):
    if read_stamp(project):
        sys.exit(f"{STAMP} уже есть — проект развёрнут, нужен sync, а не init.")
    sha = resolve(ref)
    created, skipped = [], []
    for path, kind in manifest_at(sha).items():
        if (project / path).exists():
            skipped.append(f"{kind}  {path}")
            continue
        write_project(project, path, read_at(sha, f"template/{path}"))
        created.append(f"{kind}  {path}")
    write_stamp(project, sha)
    print(f"init: кит {version_at(sha)} ({sha[:12]}) → {project}")
    print("создано:\n  " + ("\n  ".join(created) or "—"))
    if skipped:
        print("уже были, не тронуты:\n  " + "\n  ".join(skipped))
        print("Если среди них core — следующий sync покажет их расхождение с китом как конфликт.")


def cmd_sync(project, ref, dry_run):
    stamp = read_stamp(project)
    if not stamp:
        sys.exit(f"нет {STAMP} — проект не развёрнут китом: init (или миграция, kit/INSTALL.md).")
    base, new = resolve(stamp["ref"]), resolve(ref)
    base_m, new_m = manifest_at(base), manifest_at(new)
    report = {"updated": [], "added": [], "same": [], "conflict": [], "removed": []}
    conflicts = []
    for path, kind in new_m.items():
        theirs = read_at(new, f"template/{path}")
        ours = read_project(project, path)
        if kind == "seed":
            if ours is None:
                report["added"].append(f"seed  {path}")
                if not dry_run:
                    write_project(project, path, theirs)
            continue
        base_c = read_at(base, f"template/{path}") if path in base_m else None
        if ours is None:
            report["added"].append(f"core  {path}")
            if not dry_run:
                write_project(project, path, theirs)
        elif norm(ours) == norm(theirs):
            report["same"].append(path)
        elif base_c is not None and norm(ours) == norm(base_c):
            report["updated"].append(path)
            if not dry_run:
                write_project(project, path, theirs, like=ours)
        else:
            report["conflict"].append(path)
            conflicts.append((path, base_c, ours, theirs))
    for path, kind in base_m.items():
        if kind == "core" and path not in new_m:
            report["removed"].append(path)

    print(f"sync: {version_at(base)} ({base[:12]}) → {version_at(new)} ({new[:12]})"
          + ("  [dry-run]" if dry_run else ""))
    titles = {"updated": "обновлено", "added": "добавлено", "same": "без изменений",
              "conflict": "КОНФЛИКТ — файл ядра правили в проекте", "removed": "убрано из кита (в проекте не удалено)"}
    for key, title in titles.items():
        if report[key]:
            print(f"{title}:\n  " + "\n  ".join(report[key]))
    for path, base_c, ours, theirs in conflicts:
        print(f"\n=== {path}: что изменили в проекте ===")
        print(diff(base_c, ours, "кит (база)", "проект") if base_c is not None
              else "(базовой версии нет — файл появился в проекте до кита)")
        if base_c is None:
            print(f"=== {path}: проект против кита ===")
            print(diff(ours, theirs, "проект", "кит (новый)"))
        elif base != new:
            print(f"=== {path}: что изменилось в ките ===")
            print(diff(base_c, theirs, "кит (база)", "кит (новый)"))
    if dry_run:
        return
    if conflicts:
        print(f"\nВерсия в {STAMP} не сдвинута. Разрешить конфликты (kit/INSTALL.md §Конфликты), затем:\n"
              f"  python \"{Path(__file__).resolve()}\" stamp --project \"{project}\" --ref {new}")
    else:
        write_stamp(project, new)
        print(f"\n{STAMP} → {version_at(new)}")


def cmd_status(project):
    stamp = read_stamp(project)
    if not stamp:
        sys.exit(f"нет {STAMP} — проект не развёрнут китом.")
    base, head = resolve(stamp["ref"]), resolve("HEAD")
    print(f"проект на ките {version_at(base)} ({base[:12]}); в клоне кита — {version_at(head)} ({head[:12]})"
          + ("" if base == head else " → есть обновление, sync"))
    for path, kind in manifest_at(base).items():
        if kind != "core":
            continue
        ours = read_project(project, path)
        state = ("нет в проекте" if ours is None else
                 "как в ките" if norm(ours) == norm(read_at(base, f"template/{path}")) else
                 "ПРАВИЛИ В ПРОЕКТЕ — кандидат в upstream или откат")
        print(f"  core  {path}: {state}")


def cmd_take(project, ref, paths):
    """Взять версию кита для файлов ядра — исход конфликта «взять версию кита»."""
    if not paths:
        sys.exit("take: укажите --path <файл ядра> (можно несколько раз).")
    sha = resolve(ref)
    manifest = manifest_at(sha)
    for path in paths:
        path = path.replace("\\", "/")
        if manifest.get(path) != "core":
            sys.exit(f"take: {path} — не файл ядра в kit/MANIFEST этой версии.")
        write_project(project, path, read_at(sha, f"template/{path}"), like=read_project(project, path))
        print(f"взята версия кита {version_at(sha)} ({sha[:12]}): {path}")


def cmd_stamp(project, ref):
    sha = resolve(ref)
    write_stamp(project, sha)
    print(f"{STAMP} → {version_at(sha)} ({sha[:12]})")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["init", "sync", "status", "stamp", "take"])
    ap.add_argument("--project", required=True, type=Path, help="корень проекта")
    ap.add_argument("--ref", default="HEAD", help="версия кита: коммит или тег (по умолчанию — текущий HEAD клона)")
    ap.add_argument("--dry-run", action="store_true", help="sync: только показать, ничего не писать")
    ap.add_argument("--path", action="append", help="take: файл ядра, для которого взять версию кита")
    a = ap.parse_args()
    project = a.project.resolve()
    if not project.is_dir():
        sys.exit(f"нет каталога {project}")
    if a.command == "init":
        cmd_init(project, a.ref)
    elif a.command == "sync":
        cmd_sync(project, a.ref, a.dry_run)
    elif a.command == "status":
        cmd_status(project)
    elif a.command == "take":
        cmd_take(project, a.ref, a.path)
    else:
        cmd_stamp(project, a.ref)


if __name__ == "__main__":
    main()
