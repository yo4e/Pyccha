# Pyccha 関連言語・実装方式・ライセンス調査

調査日: 2026-09-15

Issue: #1

> この文書は設計判断のための技術・ライセンス調査メモであり、法律相談ではない。商標利用や第三者コードの再配布など、公開前に判断が必要な事項は一次情報を再確認する。

## 結論

Pyccha の v0.1 は、**Python を実行基盤にする独立した小言語**として設計し、Pyccha 自身のコードは **MIT License を第一候補**とするのが扱いやすい。

実装方式は、単純な全置換型プリプロセッサではなく、

```text
.cha source
  -> tokenizer / parser
  -> Pyccha AST or small IR
  -> Python source or Python AST
  -> Python runtime
```

とする。v0.1 の parser は **Lark** を第一候補とする。Lark は MIT License、Unicode 対応、行・列位置の追跡、LALR/Earley、曖昧文法の扱いを備えており、北九州弁の助詞・語尾を構文として扱う実験と相性がよい。

PoC の数時間だけであれば行ベース変換でもよいが、`str.replace()` や巨大な正規表現チェーンを製品の核にしない。文字列リテラル、コメント、ネスト、表記ゆれが入った瞬間に「方言文法」と「単語置換」の境界が壊れるためである。

名称は **Pyccha（ぱいっちゃ）** とする。旧称 `Pythoncha` と異なり、製品名そのものに `Python` を含めないため、「別言語の名称に Python 商標を直接含める」懸念は大きく後退する。由来として Python の `Py` と北九州弁の「〜っちゃ」を説明することは、Pythonとの技術的関係を正確に記述する範囲に留める。PSF公式・公認を示唆しないこと、PythonロゴをPycchaのロゴとして改変利用しないことは引き続き守る。

---

## 1. 類似する日本語プログラミング言語

### 比較表

| 言語 | 現状 | 実装・実行方式 | 日本語文法上の特徴 | ライセンス / 配布条件 | Pyccha への示唆 |
|---|---|---|---|---|---|
| なでしこ3 | 現行・公開継続 | JavaScript / TypeScript。JavaScriptへ変換してブラウザ / Node.js等で実行 | 日本語の語順、助詞を活用。日本語として読み下せることを重視 | MIT | 「母語らしい文」を構文にする先例。トランスパイル方式も近い |
| プロデル | 現行・公開継続 | C# / .NET 系。インタプリタとCILコンパイルの系譜 | 助詞を引数の意味付けに使い、動詞をメソッド・制御構文の中心に置く | 公式サイトでは利用可能だが、今回の調査では標準OSSライセンスとしての全体ライセンスを確認できず。コード流用前に要確認 | **助詞を名前付き引数に相当する構文情報として扱う設計が非常に参考になる** |
| ドリトル | 現行。2026年にオンライン版V4.0 | 教育用言語。インストール版 / ブラウザ版 | 日本語の命令・オブジェクト指向を教育向けに整理 | 「フリーソフト」。個人・学校利用は自由、雑誌/Web等で再配布する場合は事前連絡。Wiki文書はCC BY-SA 4.0表記あり | 「無料利用可能」と「OSSライセンス」は同義ではないことの好例。コードや文書を借りる場合は個別条件を見る |

### なでしこ

なでしこ3は日本語プログラミング言語として現在も公開されており、JavaScript / TypeScriptを基盤とし、内部的にJavaScriptへ変換して実行する。

Pycchaに近い点は、「英語キーワードを日本語へ単純置換する」のではなく、日本語で読んだ時の自然さを重視していること、そして既存ランタイムへ変換する方式を採っていること。

参考:
- https://github.com/kujirahand/nadesiko3
- https://nadesi.com/

### プロデル

プロデルはオブジェクト指向の日本語プログラミング言語で、公式説明でも「日本語文のように書ける」ことを重視している。

特に参考になるのは **助詞と動詞の扱い**。FIT2021の論文では、プロデルの助詞は「引数の意味を付加する字句」で、名前付き引数に相当する役割を持つと説明されている。また、補語は `式 + 助詞` で構成され、末尾の動詞へ係る。

これは Pyccha でもそのまま発想の種になる。

例:

```text
54 と 160 から BMI を計算して報告する
```

のように、`と` / `から` を単なる可読性用文字列ではなく「どの役割の引数か」を示す構文要素にできる。

Pycchaであれば将来的に、

```text
名前を "山田" にする
3回 "まだやるん？" って言う
```

の `を` `に` `って` などを、明示的な引数ロールとして扱う設計が可能。

参考:
- https://produ.irelang.jp/
- https://www.ieice.org/publications/conference-FIT-DVDs/FIT2021/data/pdf/A-006.pdf

### ドリトル

ドリトルは教育用途を中心に長期運用されている日本語プログラミング言語。2026年にもオンライン版V4.0が公開されている。

今回特に参考になるのはライセンス面で、公式ダウンロードページでは「フリーソフト」として個人・学校での利用を認める一方、再配布には連絡を求めている。したがって、単に「無料で使える」からといってOSSコードとして再利用可能とは限らない。

参考:
- https://dolittle.eplang.jp/
- https://dolittle.eplang.jp/doku.php?id=download

---

## 2. 自然言語風 / 文化的文体を文法にする言語

| 言語 | 文体 | 実装の考え方 | ライセンス例 | Pyccha への示唆 |
|---|---|---|---|---|
| LOLCODE | lolcat / Internet slang | 専用lexer/parser/interpreter | lci は GPL-3.0-or-later | スラングを予約語体系として徹底すると世界観が成立する |
| Rockstar | ロック歌詞 | 独自言語・interpreter | 現行repoは AGPL-3.0 | 「自然文らしさ」を優先すると曖昧性管理が重要 |
| ArnoldC | 映画の決め台詞 | parser -> Java bytecode | repoの利用条件はコード流用前に要個別確認 | フレーズ全体を構文トークンにできる |
| Shakespeare Programming Language | 戯曲 | 専用compiler/interpreter | 実装ごとに異なる。ミラーには複数ライセンス | 文体の再現を優先しすぎると可読性・実用性が下がる |
| Chef | 料理レシピ | 専用interpreter | Chef-Interpreter実装は CC0-1.0 | 既存文化形式を文法へ写像する典型 |

### 共通して学べること

これらの言語は「特定の単語を置き換える」だけではなく、**文章の型そのもの**をプログラム構造として使っている。

Pycchaにとって重要なのは、この系譜の「面白さ」は借りつつ、可読性を犠牲にしすぎないこと。

特に避けたいのは以下。

- 方言フレーズを長大な予約語へ固定しすぎる
- 同じ意味の自然な言い回しを無制限に受理しようとする
- “自然文なら何でも通る”ことを目指してparserを推測器にする
- 方言らしさをエラーメッセージだけに押し込める

Pycchaは esolang 的な楽しさを持ってよいが、**構文規則は機械的に説明可能**であるべき。

参考:
- LOLCODE / lci: https://github.com/justinmeza/lci
- Rockstar: https://github.com/RockstarLang/rockstar
- ArnoldC: https://github.com/lhartikk/ArnoldC
- SPL mirror: https://github.com/krayon/shakespearelang
- Chef interpreter: https://github.com/joostrijneveld/Chef-Interpreter

---

## 3. Python を実行基盤にする言語・DSL

### Hy

Hy は Lisp 方言を Python へ埋め込む言語で、Hyコードを **Python AST** へ変換する。2026年にもPyPIリリースがあり、MIT License。

Pycchaにとって重要なのは、「必ずしもPythonソース文字列を生成しなくてもよい」という点。parserで得た内部表現からPython ASTを生成し、Pythonの `compile()` へ渡す方式も現実的である。

ただし v0.1 では、変換結果の可視化・デバッグがしやすいという理由で Pythonソースを一度生成するほうが開発しやすい可能性が高い。

- https://pypi.org/project/hy/
- https://github.com/hylang/hy

### Coconut

Coconut は Python へコンパイルする関数型プログラミング言語。Pythonを拡張する形の構文を持ち、Apache-2.0。

「別言語を既存Pythonランタイムへ落とす」という意味ではPycchaと非常に近い。言語処理系を独自VMまで広げず、Pythonの生態系と実行環境を再利用する判断の先例になる。

- https://coconut-lang.org/
- https://github.com/evhub/coconut

### Vex Lang

Vex Lang は Hinglish（Hindi + English）をキーワードに使うPython transpilerとしてPyPI公開されている小規模言語。2026年リリース、MIT License。

規模感と「文化的 / 自然言語的な表現をPythonへ落とす」という意味で参考になる。ただしPycchaは単語置換型より一段踏み込み、**北九州弁の語尾・助詞・接続そのものを文法要素にする**ことを独自性の中心に置くべき。

- https://pypi.org/project/vex-lang/

---

## 4. parser 実装候補

### 比較

| 候補 | ライセンス | 2026時点の状態 | Unicode | 特徴 | 評価 |
|---|---|---|---|---|---|
| Python標準 `ast` / `tokenize` | PSF License | Python標準 | 可 | 追加依存なし | 補助用途には良いが、非Python構文の一次parserには不足 |
| Lark | MIT | 現行 | **明示的に対応** | EBNF、LALR、Earley、曖昧文法、行列位置 | **第一候補** |
| PLY | BSD系 | 2025-12に作者が保守終了宣言 | 可 | lex/yacc、LALR(1) | 新規採用は避ける |
| TatSu | BSD-4-Clause | 2026も活発 | 可 | PEG / Packrat、EBNF | 技術的には有力だがライセンス条件がLarkより少し重い |
| textX | MIT | 2026も活発 | 可 | DSL / metamodel 全体を構築 | 強力だがv0.1にはやや大きい |

### Lark を第一候補にする理由

1. **日本語をそのままterminalに書ける**
2. Unicode対応が明示されている
3. LALRで厳密な文法を作りつつ、必要ならEarleyで曖昧性の調査もできる
4. token位置を保持でき、方言らしいエラーを作る時にも元ソース位置へ戻れる
5. MITでPycchaのMIT案と相性がよい
6. parser frameworkとして十分枯れているが、textXほど設計全体を支配しない

### `ast` / `tokenize` の使いどころ

`ast` はPython構文を解析するためのものなので、`もし 名前 が "山田" やったら` のようなPycchaソースを直接読ませることはできない。

一方で、

- Pythonへ変換した後の妥当性確認
- Python ASTの生成
- 文字列・コメントの扱いを安全にする補助
- 変換結果への位置情報付与

には使える。

---

## 5. 「助詞」「語尾」「表記ゆれ」をどう文法化するか

### 助詞

助詞は「読みやすさ用ノイズ」ではなく、**引数ロール / 構文ロール**として扱う。

例えば、

```text
名前を "山田" にする
```

を、

```text
target(名前) value("山田") assign
```

のような内部表現へ落とす。

プロデルの「助詞 = 名前付き引数に近い」という設計は、この方向の強い先例になる。

### 文末・接続表現

`やったら`、`けん`、`っちゃ` は、文字列置換ではなく **特定の構文位置でだけ意味を持つterminal** とする。

例:

```ebnf
if_stmt: "もし" expr "やったら" block ("ちがったら" block)? "おわり"
reason_stmt: expr "けん" block "おわり"
```

実際の文法は方言として自然か検討してから決める。

### 表記ゆれ

v0.1ではファジー一致をしない。

許容したい表記ゆれは明示的な同義terminalとして列挙し、lexer/parserの入口で正規化する。

例:

```text
やったら
やったらば   # 採用するなら明示
```

のように、何を受理するかを仕様として決める。

「なんとなく似ている文なら通す」は、エラーの再現性がなくなるため避ける。

---

## 6. 正規表現 / 行ベース変換でどこまで行けるか

### PoCだけなら可能

以下程度なら行ベース変換で十分。

- `"文字列" って言う`
- 単純代入
- 1段の `もし ... やったら`
- 数値回数の繰り返し

ただし、最低でも文字列リテラルとコメントの内部は変換しない仕組みが必要。

### v0.1本体にはparserを入れる

Pycchaの特徴は語尾・助詞なので、「構文らしい部分」を後回しにすると、最も重要な設計判断を後から全部やり直すことになる。

そのため、

- **PoC 0**: 行ベースで手触り確認
- **v0.1**: Lark grammar + 小さなAST/IR + Python生成

を推奨する。

---

## 7. Python ライセンス

### Python を実行基盤として呼ぶだけの場合

Pythonソフトウェアと文書は PSF License Version 2 で提供されている。

Pycchaがユーザー環境のPythonを実行基盤として利用するだけであれば、Pyccha自身をPSF Licenseにする必要はない。MIT / Apache-2.0 / BSD等の独立したライセンスで公開できる。

また、Python 2.2以降のライセンスはGPL-compatibleとPython公式文書に明記されている。

参考:
- https://docs.python.org/3/license.html

### CPython を同梱・再配布する場合

将来、standalone executable 等でCPython本体を同梱する場合は話が変わる。

PSF Licenseは、Pythonまたはその派生版を配布する際に、

- PSF License Agreement
- PSFのcopyright notice

を保持することを求める。

さらにPythonの派生物を作って配布する場合、Pythonへ加えた変更の短い説明を含める必要がある。

Python配布物にはPSF License以外のライセンスが適用される組み込みソフトウェアもあるため、CPythonを丸ごと再配布する場合は `LICENSE` / acknowledgements 一式を保持する方針が安全。

### Python標準ライブラリのコードをコピーする場合

単に `import ast` や `import tokenize` して利用するのと、CPythonの実装コードをPycchaへコピーするのは別。

コピーする場合、そのファイルに適用されるPSF Licenseや個別ライセンスを確認し、必要なnoticeを保持する。

Python 3.8.6以降、公式ドキュメント中のexample / recipe等のコードは PSF License v2 と Zero-Clause BSD のデュアルライセンスとされている。

原則としてPycchaでは、標準ライブラリ実装のコピーを避け、public APIを呼ぶ。

---

## 8. 依存ライブラリのライセンス互換性

PycchaをMITにする場合、MIT / BSD / Apache-2.0 の一般的なparser依存は採用しやすい。

### 推奨優先度

1. **MIT**
2. BSD-2-Clause / BSD-3-Clause
3. Apache-2.0
4. その他は採用前に確認

### GPL系依存

GPLライブラリをPycchaの必須コンポーネントとして配布・密接結合すると、配布形態によってはPyccha側のライセンス方針へ影響する。

MITで「好きに組み込みやすい小言語」を目指すなら、parser等の中核依存ではGPLを避けるほうが単純。

LOLCODEのlci等は設計参考にはなるが、そのコードをPycchaへコピーしない。

### vendoring

依存ライブラリをPyPI依存として宣言するだけでなく、ソースをPycchaリポジトリへvendoringする場合は、依存側のlicense file / copyright noticeを同梱する。

---

## 9. PyPI 配布

現在のPython Packaging User Guideでは PEP 639 に基づき、

```toml
[project]
license = "MIT"
license-files = ["LICENSE"]
```

のように SPDX license expression とlicense fileを宣言する方式が推奨されている。

旧式の `license = { file = "LICENSE" }` は非推奨。

Pycchaの想定例:

```toml
[project]
name = "pyccha"
version = "0.1.0"
requires-python = ">=3.11"
license = "MIT"
license-files = ["LICENSE"]
dependencies = [
  "lark>=1.3,<2",
]

[project.scripts]
pyccha = "pyccha.cli:main"
```

実際の最低Pythonバージョンは実装開始時に決める。

参考:
- https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- https://packaging.python.org/en/latest/specifications/license-expression/
- https://packaging.python.org/en/latest/specifications/pyproject-toml/

### PyPI名

2026-09-15時点のWeb/PyPI検索では、`pyccha` という既存PyPIプロジェクトは確認できなかった。ただしPyPIの名前は先取りされうるため、**初回公開直前に再確認する**。

`pycha` は別のchart libraryとして既に存在するため、短縮名 `pycha` は使わない。

---

## 10. 名称・商標

### PSF の基本ルール

Python Software Foundation は `Python` の名称を登録商標として管理している。

PSFのTrademark Usage Policyでは、

- Pythonについて正確に説明するためのnominative useは許可
- Pythonで書かれた、Python互換、Pythonを含む、という正確な説明は原則可能
- Python用の無償配布製品名で `Python` を使う例は一定範囲で許容
- 商用製品名での利用は事前承認が必要
- modified Python logoの利用は特に注意
- 他のプログラミング言語をPythonと呼んで混同させる利用は避ける

といった方針を示している。

参考:
- https://www.python.org/psf/trademarks/
- https://www.python.org/psf/trademarks-faq/

### Pyccha への当てはめ

Pycchaは「Python向けlibrary」ではなく、独自の表面構文を持ち、Pythonを実行基盤として利用する**別言語**である。

旧称 `Pythoncha` は名称そのものに `Python` を含んでいたため、PSFの商標ポリシー上、「Pythonを別のプログラミング言語名として使う」点を個別確認する必要性が高かった。

2026-09-15に名称を **Pyccha（ぱいっちゃ）** へ変更したことで、この直接的な懸念は大きく後退した。`Py` は名称の由来としてPythonとの関係を想起させるが、少なくとも製品名そのものを `Python` と呼ぶ構造ではない。

公開時の運用方針:

- 「Pythonを実行基盤にする独立した言語」と正確に説明する
- PSF公式・公認・提携プロジェクトであると誤認させない
- Pythonロゴを改変してPycchaロゴとして使わない
- PythonやPSFの商標ポリシーが改定された場合は再確認する
- 商用展開やブランド利用の仕方が変わり、Python商標を製品名・ロゴ・販促物で強く使う場合は、その時点でPSFポリシーを再確認する

現時点では、**Pycchaという名称だけを理由にPSF Trademarks Committeeへの事前問い合わせを必須タスクとはしない**。

READMEに非提携表記を置く場合は、例えば次のように簡潔に書ける。

```text
Pyccha is an independent project and is not affiliated with or endorsed by
the Python Software Foundation.
```

### .cha 拡張子

`.cha` は既にIRC設定、Photoshop関連、CLAN/CHILDES transcript等、複数の用途で使われている。

ただしファイル拡張子は中央管理された一意なnamespaceではないため、技術的な使用不可を意味しない。

Pycchaの文脈では短く覚えやすいため第一候補のままでよい。ただしOSの既存関連付けと衝突する可能性はREADMEに記載してもよい。

---

## 11. Pyccha 側の推奨OSSライセンス

### 第一候補: MIT

理由:

- 短く理解しやすい
- 商用利用・改変・再配布を広く許容
- Lark / textX / Hy 等の参考プロジェクトとも親和性が高い
- Pythonをruntime dependencyとして利用することと矛盾しない
- 小さな実験言語としてcontributionの心理的コストが低い

### 第二候補: Apache-2.0

明示的なpatent grantを重視するなら有力。

ただし、小規模言語としてはNOTICE等の運用を含めMITより少し重い。

### BSD

BSD-2-Clause / BSD-3-Clauseも問題ないが、PycchaでMITより優先する明確な利点は現時点では薄い。

### 推奨結論

**Pyccha自身: MIT**

ただし、以下は別管理する。

- Python本体を将来同梱するならPSF License等を同梱
- third-party vendored codeには各licenseを保持
- Python商標はcopyright licenseとは別問題

---

## 12. v0.1 推奨アーキテクチャ

```text
src/pyccha/
  __init__.py
  cli.py
  parser.py
  grammar.lark
  nodes.py
  transpiler.py
  diagnostics.py
```

### 流れ

1. `pyccha hello.cha`
2. UTF-8でsource読込
3. Larkでparse
4. Pyccha AST / dataclassへ変換
5. Pythonソースを生成
6. `compile(..., filename=original_cha_path, ...)`
7. 実行
8. エラー時は元の `.cha` の行・列へ対応付け

### 最初の文法範囲

- literal: string / integer / boolean
- assignment
- print
- equality comparison
- if / else
- counted repeat
- comment

### 実装しないもの

- Pythonの任意式をそのまま埋め込むescape hatch
- import
- function
- class
- async
- 自動的な自然言語解析
- fuzzy spelling correction

---

## 13. Pyccha 独自性の仮説

既存の日本語プログラミング言語には、助詞・動詞を本格的に文法へ取り込む先例がある。

したがってPycchaの独自性を、

> 「日本語の助詞を使う言語」

だけに置くのは弱い。

より強い仮説は、

> **北九州弁の文末・接続・距離感そのものを、制御構造や発話構文の意味へ対応付ける言語**

である。

例えば `やったら` は英語の `if` の単なる翻訳ではなく「条件を受ける接続表現」として構文に置く。

`けん` も単純に `because` へ置換するのではなく、条件・前提・理由のどの意味をプログラム上で与えるかを言語設計として決める。

`っちゃ` は断定・強調・出力・文終端のどこへ割り当てると北九州弁として自然かを検討する。

**方言の意味とprogram semanticsの対応そのもの**がPycchaの研究テーマになる。

---

## 14. 避けたほうがよい設計

- 英語Python keywordの1対1方言置換
- source全体への `replace()`
- “自然な日本語ならだいたい動く”という曖昧な受理
- v0.1からPython全機能を覆う
- Python標準ライブラリ名まで無理に方言化する
- 方言の誇張を面白さの主成分にする
- parser errorを全部ネタ文へ変えて原因を読めなくする
- GPL等のコードをlicense確認なしでコピーする
- Python logoを少し変えてPyccha logoにする
- 「Python公式の方言版」のような誤認を招く説明

---

## 15. 次に切る実装Issue候補

### Issue A: v0.1 文法スケッチ

- `言う`
- 代入
- `もし ... やったら`
- `ちがったら`
- 回数繰り返し
- コメント
- block終端

について、北九州弁として自然な候補を複数書き、機械的に曖昧にならない形を選ぶ。

### Issue B: Lark 最小transpiler

```text
hello.cha
  -> grammar.lark
  -> AST
  -> generated Python
  -> execute
```

を通す。

### Issue C: source map / diagnostics

Python側のSyntaxError / runtime errorを、元の `.cha` 行へ戻す最小設計を作る。

### Issue D: 名称・公開前チェック

Pycchaへの改名を前提に、公開直前に以下を再確認する。

- `Pyccha` / `pyccha` の主要プロジェクト名との衝突
- PyPI `pyccha` の取得可否
- CLI `pyccha` の衝突
- READMEでPythonとの関係を正確に説明できているか
- PSF公式・公認を示唆する表現やロゴ利用がないか

旧称 `Pythoncha` で想定していたPSFへの名称問い合わせは、現時点では必須タスクから外す。

### Issue E: PyPI公開準備

初回公開直前に、

- `pyccha` name availability
- CLI `pyccha`
- `.cha`
- READMEのtrademark notice
- `LICENSE`
- `pyproject.toml` のPEP 639 metadata

を再確認する。

---

## 16. 参考資料

### Python / Packaging / Trademark

- Python History and License  
  https://docs.python.org/3/license.html
- PSF Trademark Usage Policy  
  https://www.python.org/psf/trademarks/
- PSF Trademark FAQ  
  https://www.python.org/psf/trademarks-faq/
- Python Packaging User Guide: Writing `pyproject.toml`  
  https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- License Expression  
  https://packaging.python.org/en/latest/specifications/license-expression/
- `pyproject.toml` specification  
  https://packaging.python.org/en/latest/specifications/pyproject-toml/

### 日本語プログラミング言語

- なでしこ3  
  https://github.com/kujirahand/nadesiko3
- プロデル  
  https://produ.irelang.jp/
- プロデル関連論文（FIT2021）  
  https://www.ieice.org/publications/conference-FIT-DVDs/FIT2021/data/pdf/A-006.pdf
- ドリトル  
  https://dolittle.eplang.jp/
- ドリトル配布条件  
  https://dolittle.eplang.jp/doku.php?id=download

### 自然言語風 / esolang

- LOLCODE / lci  
  https://github.com/justinmeza/lci
- Rockstar  
  https://github.com/RockstarLang/rockstar
- ArnoldC  
  https://github.com/lhartikk/ArnoldC
- Shakespeare Programming Language mirror  
  https://github.com/krayon/shakespearelang
- Chef Interpreter  
  https://github.com/joostrijneveld/Chef-Interpreter

### Pythonベース言語 / parser

- Hy  
  https://pypi.org/project/hy/
- Coconut  
  https://coconut-lang.org/
- Vex Lang  
  https://pypi.org/project/vex-lang/
- Lark  
  https://pypi.org/project/lark/
- PLY  
  https://github.com/dabeaz/ply
- TatSu  
  https://pypi.org/project/TatSu/
- textX  
  https://pypi.org/project/textX/
