import argparse
import os
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


def detect_encoding(path: Path) -> str:
    """Detect file encoding using chardet when available."""
    try:
        with path.open('rb') as f:
            raw = f.read()
        try:
            import chardet  # type: ignore
            result = chardet.detect(raw)
            if result and result.get('encoding'):
                return result['encoding']
        except Exception:
            pass
    except FileNotFoundError:
        pass
    return 'utf-8'


def read_text(path: Path) -> Tuple[str, str]:
    encoding = detect_encoding(path)
    with path.open('r', encoding=encoding, errors='ignore') as f:
        text = f.read()
    return text, encoding


def write_text(path: Path, text: str, encoding: str) -> None:
    with path.open('w', encoding=encoding) as f:
        f.write(text)


def iter_files(folder: Path, exts: Iterable[str]) -> Iterable[Path]:
    for root, _, files in os.walk(folder):
        for name in files:
            p = Path(root) / name
            if not exts or p.suffix in exts:
                yield p


def search_mode(folder: Path, pattern: re.Pattern, exts: List[str], max_hits: int, verbose: bool) -> int:
    hits: List[Tuple[Path, int, str]] = []
    for file_path in iter_files(folder, exts):
        try:
            text, _ = read_text(file_path)
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                hits.append((file_path, i, line.rstrip()))
                if verbose:
                    print(f"{file_path}:{i}:{line.rstrip()}")
                if len(hits) >= max_hits:
                    for fp, ln, l in hits:
                        print(f"{fp}:{ln}:{l}")
                    return 2
    for fp, ln, l in hits:
        print(f"{fp}:{ln}:{l}")
    return 0


def replace_mode(folder: Path, pattern: re.Pattern, replace: str, exts: List[str], backup: bool, dry_run: bool, verbose: bool) -> int:
    total = 0
    for file_path in iter_files(folder, exts):
        try:
            text, encoding = read_text(file_path)
        except Exception:
            continue
        new_text, count = pattern.subn(replace, text)
        if count:
            total += count
            if verbose:
                print(f"{file_path}: {count} replacements")
            if not dry_run:
                if backup:
                    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                    try:
                        backup_path.write_bytes(file_path.read_bytes())
                    except Exception:
                        pass
                write_text(file_path, new_text, encoding)
    print(f"GrepReplacer: 置換完了（総置換件数: {total} 件）")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='GrepReplacer')
    parser.add_argument('folder_path')
    parser.add_argument('pattern')
    parser.add_argument('-r', '--replace')
    parser.add_argument('-m', '--max-hits', type=int, default=10)
    parser.add_argument('-e', '--extensions')
    parser.add_argument('-b', '--backup', action='store_true')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    folder = Path(args.folder_path)
    exts = []
    if args.extensions:
        exts = [e if e.startswith('.') else '.' + e for e in args.extensions.split(',')]
    pattern = re.compile(args.pattern)
    if args.replace is None:
        return search_mode(folder, pattern, exts, args.max_hits, args.verbose)
    return replace_mode(folder, pattern, args.replace, exts, args.backup, args.dry_run, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
