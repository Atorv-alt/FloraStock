"""Тесты запрета отрицательных чисел (п.1.3 курсовой)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "frontend"))

from src.ui.widgets.products_widget import _check_int as p_int, _check_decimal as p_dec
from src.ui.widgets.batches_widget import _check_int as b_int, _check_decimal as b_dec
from src.ui.widgets.orders_widget import _check_decimal as o_dec
from src.ui.widgets.inventory_widget import _check_int as i_int


def test_negative_quantity_rejected():
    assert b_int("-5", "Количество", min_val=0) is not None
    assert i_int("-1", "Количество", min_val=0) is not None
    assert b_int("0", "Количество", min_val=0) is None
    assert i_int("10", "Количество", min_val=0) is None


def test_negative_price_rejected():
    assert b_dec("-100", "Стоимость", min_val=0) is not None
    assert o_dec("-50", "Общая сумма", min_val=0) is not None
    assert p_dec("-10", "Закупочная цена", min_val=0) is not None
    assert b_dec("0", "Стоимость", min_val=0) is None


def test_retail_price_must_be_positive():
    assert p_dec("-5", "Розничная цена", min_val=0.01) is not None
    assert p_dec("0", "Розничная цена", min_val=0.01) is not None
    assert p_dec("300", "Розничная цена", min_val=0.01) is None


def test_shelf_life_must_be_positive():
    assert p_int("0", "Срок годности", 36500, min_val=1) is not None
    assert p_int("-3", "Срок годности", 36500, min_val=1) is not None
    assert p_int("10", "Срок годности", 36500, min_val=1) is None


def test_stem_length_non_negative():
    assert p_int("-1", "Длина стебля", 10000, min_val=0) is not None
    assert p_int("0", "Длина стебля", 10000, min_val=0) is None


def test_garbage_still_rejected():
    assert p_int("abc", "Количество", min_val=0) is not None
    assert p_dec("xyz", "Цена", min_val=0) is not None
    assert p_int("99999999999", "Количество", min_val=0) is not None  # переполнение
