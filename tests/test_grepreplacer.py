import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import grepreplacer.cli as cli


def write(file: Path, text: str):
    file.write_text(text, encoding='utf-8')


def test_search_mode(tmp_path):
    d = tmp_path / 'data'
    d.mkdir()
    file1 = d / 'a.txt'
    file2 = d / 'b.txt'
    write(file1, 'hello\nworld\nTODO: test\n')
    write(file2, 'nothing here\n')

    exit_code = cli.main([str(d), 'TODO:'])
    assert exit_code == 0


def test_replace_mode(tmp_path):
    d = tmp_path / 'data'
    d.mkdir()
    file1 = d / 'a.txt'
    file2 = d / 'b.txt'
    write(file1, 'foo_1\nfoo_2\n')
    write(file2, 'foo_3\n')

    exit_code = cli.main([str(d), r'foo_(\d+)', '--replace', r'bar_\1'])
    assert exit_code == 0
    assert file1.read_text() == 'bar_1\nbar_2\n'
    assert file2.read_text() == 'bar_3\n'
