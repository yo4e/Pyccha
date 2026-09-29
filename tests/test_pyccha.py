from __future__ import annotations

import pytest

from pyccha import PycchaSyntaxError, parse_source, run_source, transpile_source


E014 = '''\
# 今日のおやつ
おやつ = "シロヤ"
個数 = 3

もし 個数 が 0 よりでかいん やったら
    3回くりかえす
        おやつ っちゆう
    おしまい
ちごうたら
    "今日はなし" っちゆう
おしまい
'''


@pytest.mark.parametrize(
    "source",
    [
        '"こんにちは" っちゆう',
        '名前 = "山田"\n名前 っちゆう',
        'もし 名前 == "山田" やったら "本人っちゃ" っちゆう ちごうたら "誰なん？" っちゆう おしまい',
        '3回くりかえす "まだやるん？" っちゆう おしまい',
        'もし 年齢 が 20 よりでかいん やったら "大人やん" っちゆう おしまい',
        'もし 残り が 3 よりこまいん やったら "もうちょいやん" っちゆう おしまい',
        'もし 天気 == "晴れ" それと 曜日 == "日曜" やったら "出かけよ" っちゆう おしまい',
        'もし 飲み物 == "コーヒー" か 飲み物 == "お茶" やったら "どっちも好き" っちゆう おしまい',
        'もし 売り切れ やないん やったら "まだあるやん" っちゆう おしまい',
        'もし 名前 != "佐藤" やったら "佐藤さんやない" っちゆう おしまい',
        '# コメント\n名前 = "山田"\n"こんにちは" っちゆう',
        E014,
    ],
)
def test_adopted_specimens_parse(source: str) -> None:
    parse_source(source)


def test_e014_runs_end_to_end(capsys: pytest.CaptureFixture[str]) -> None:
    run_source(E014)
    assert capsys.readouterr().out == "シロヤ\nシロヤ\nシロヤ\n"


def test_if_else_and_less_than(capsys: pytest.CaptureFixture[str]) -> None:
    source = '''\
残り = 5
もし 残り が 3 よりこまいん やったら
    "少ない" っちゆう
ちごうたら
    "まだある" っちゆう
おしまい
'''
    run_source(source)
    assert capsys.readouterr().out == "まだある\n"


def test_nested_if_and_repeat(capsys: pytest.CaptureFixture[str]) -> None:
    source = '''\
数 = 2
2回くりかえす
    もし 数 == 2 やったら
        "よし" っちゆう
    おしまい
おしまい
'''
    run_source(source)
    assert capsys.readouterr().out == "よし\nよし\n"


def test_and_binds_more_tightly_than_or(capsys: pytest.CaptureFixture[str]) -> None:
    source = '''\
a = 0
b = 2
c = 0
もし a == 1 か b == 2 それと c == 3 やったら
    "true" っちゆう
ちごうたら
    "false" っちゆう
おしまい
'''
    run_source(source)
    assert capsys.readouterr().out == "false\n"
    python = transpile_source(source)
    assert "a == 1" in python and "b == 2" in python and "c == 3" in python


def test_postfix_not(capsys: pytest.CaptureFixture[str]) -> None:
    source = '''\
売り切れ = 0
もし 売り切れ やないん やったら
    "まだある" っちゆう
おしまい
'''
    run_source(source)
    assert capsys.readouterr().out == "まだある\n"


def test_particle_must_be_separated_from_japanese_identifier() -> None:
    valid = 'もし 個数 が 0 よりでかいん やったら "ok" っちゆう おしまい'
    parse_source(valid)

    invalid = 'もし 個数が 0 よりでかいん やったら "ng" っちゆう おしまい'
    with pytest.raises(PycchaSyntaxError) as exc_info:
        parse_source(invalid)
    assert exc_info.value.line == 1
    assert exc_info.value.column > 1


def test_syntax_error_has_line_and_column() -> None:
    source = '名前 = "山田"\nもし 名前 == "山田" やったら\n    "本人" っちゆう\n'
    with pytest.raises(PycchaSyntaxError) as exc_info:
        parse_source(source)
    message = str(exc_info.value)
    assert exc_info.value.line >= 1
    assert exc_info.value.column >= 1
    assert ":" in message
