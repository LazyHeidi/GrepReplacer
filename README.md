# GrepReplacer

---

## 1. 概要

`GrepReplacer` は「フォルダ内の全ファイルを対象に，指定の正規表現で検索／置換を行う」シンプルかつ強力な Python 製 CUI ツールです。
ファイルを1つずつ処理するため、大量にファイルが存在しても安定して実行できます。

* **検索のみモード**：ヒット件数が10件に到達した時点で処理を打ち切り，マッチ箇所を一覧表示
* **置換モード**：フォルダ内すべてのファイルをスキャンし，該当箇所を置換。終了後に合計置換件数をワンラインで出力

---

## 2. 実行環境

* Python 3.8 以上
* 依存ライブラリ：

  * `argparse`（標準）
  * `re`（標準）
  * `chardet`（文字コード自動判定用）

---

## 3. インストールと実行方法

1. **リポジトリの取得**

   ```bash
   $ git clone <このリポジトリのURL>
   $ cd GrepReplacer
   ```

2. **依存ライブラリのインストール**

   自動文字コード判定を行う場合は `chardet` を導入してください。

   ```bash
   $ python -m pip install chardet
   ```

3. **ツールの起動**

   モジュールとして実行します。

   ```bash
   $ python -m grepreplacer.cli <FOLDER_PATH> <PATTERN> [OPTIONS]
   ```

   例: 置換せずにヒット件数のみ確認する

   ```bash
   $ python -m grepreplacer.cli ./src '^TODO:' -n
   ```

---

## 4. コマンドライン仕様

```
Usage:
  GrepReplacer [OPTIONS] FOLDER_PATH PATTERN

Positional Arguments:
  FOLDER_PATH           対象フォルダのパス（再帰的に探索）
  PATTERN               検索用正規表現パターン

Options:
  -r, --replace TEXT    置換文字列を指定すると「置換モード」に切り替わる
  -m, --max-hits INT    ── 検索のみモード時の最大ヒット数（デフォルト: 10）
  -e, --extensions TEXT カンマ区切りで処理対象ファイルの拡張子を指定（例: .txt,.py）
  -b, --backup          置換モード時に，元ファイルを `.bak` 拡張子でバックアップ
  -n, --dry-run         置換モードでも実際の書き換えはせず，置換予定の件数だけ表示
  -v, --verbose         処理中のファイル名・行番号を都度出力
  -h, --help            ヘルプを表示して終了
```

---

## 5. 動作フロー

1. **引数解析**

   * `PATTERN` を `re.compile()`
   * `--replace` の有無でモード決定
2. **フォルダ走査**

   * `os.walk()` で再帰的にサブフォルダも含め探索
   * `--extensions` が指定されていればフィルタリング
3. **ファイルごとに処理**

   * テキストモードで開き，必要なら `chardet` で文字コード判定
   * **検索のみモード**：

     * 各マッチをカウントし，`--max-hits` に達したら即座に探索停止
     * マッチ情報（ファイルパス／行番号／該当行）を蓄積
     * 最終的に一覧を標準出力
   * **置換モード**：

     * 全行に対し `re.sub()` を実行
     * 実際に変化があったファイルは上書き（`--backup` があれば事前にコピー）
     * 総置換件数を累積
4. **終了処理**

   * 検索のみモード ⇒ ヒット一覧を出力
   * 置換モード ⇒ `GrepReplacer: 置換完了（総置換件数: XXX 件）` をワンライン表示
   * 終了コード

     * `0`: 正常終了
     * `1`: 致命的エラー
     * `2`: 検索のみモードでヒット数上限到達

---

## 6. 利用例

* **検索のみ（デフォルト上限10件）**

  ```bash
  $ GrepReplacer /home/user/docs '^TODO:'
  ```

  → `/home/user/docs` 以下から `TODO:` を含む行を最大10件まで列挙

* **置換モード**

  ```bash
  $ GrepReplacer ./src 'foo_(\d+)' --replace 'bar_\1'
  ```

  → `foo_数字` をすべて `bar_数字` に置換し，総置換件数を表示

* **拡張子フィルタ＋バックアップ**

  ```bash
  $ GrepReplacer . '[0-9]{4}-[0-9]{2}-[0-9]{2}' --replace '' \
      --extensions .md,.txt --backup
  ```

  → Markdown/Text ファイル限定で日付形式を除去、元ファイルを `.bak` で保存

---

## 7. 実装上の注意

* **大容量フォルダ**：`--max-hits` や `--dry-run` を活用し，安全性優先
* **マルチバイト対応**：Shift-JIS / UTF-8 / EUC-JP 等、エンコーディングの自動判別を推奨
* **テストコード**：`pytest` を用意し，検索／置換結果の整合性を検証

---
