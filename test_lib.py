from lib import average


def test_verage() -> None:
    assert average([1, 2, 3]) == 2
    assert average([1, 2]) == 1.5
    assert average([-3, 0, 3]) == 0
