import pytest
from app.services.test_result_service import _compute_clb_listening_reading

def test_clb_calculation_bands():
    # Max score 38 (Standard CELPIP)
    max_score = 38.0

    # CLB 10 (>= 92%) -> 35-38
    assert _compute_clb_listening_reading(38, max_score) == 10
    assert _compute_clb_listening_reading(35, max_score) == 10

    # CLB 9 (>= 86%) -> 33-34
    assert _compute_clb_listening_reading(34, max_score) == 9
    assert _compute_clb_listening_reading(33, max_score) == 9

    # CLB 8 (>= 78%) -> 30-32
    assert _compute_clb_listening_reading(32, max_score) == 8
    assert _compute_clb_listening_reading(30, max_score) == 8

    # CLB 7 (>= 71%) -> 27-29
    assert _compute_clb_listening_reading(29, max_score) == 7
    assert _compute_clb_listening_reading(27, max_score) == 7

    # CLB 6 (>= 58%) -> 22-26
    assert _compute_clb_listening_reading(26, max_score) == 6
    assert _compute_clb_listening_reading(22, max_score) == 6

    # CLB 5 (>= 44%) -> 17-21
    assert _compute_clb_listening_reading(21, max_score) == 5
    assert _compute_clb_listening_reading(17, max_score) == 5

    # CLB 4 (>= 29%) -> 11-16
    assert _compute_clb_listening_reading(16, max_score) == 4
    assert _compute_clb_listening_reading(11, max_score) == 4

    # CLB 3 (< 29% but > 0)
    assert _compute_clb_listening_reading(10, max_score) == 3
    assert _compute_clb_listening_reading(1, max_score) == 3

    # Score 0
    assert _compute_clb_listening_reading(0, max_score) == 0

def test_clb_zero_max_score():
    assert _compute_clb_listening_reading(10, 0) == 0
    assert _compute_clb_listening_reading(0, 0) == 0
