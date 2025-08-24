from detector.main import dummy_test_aux


def test_main_output():
    value = dummy_test_aux(10)
    assert value, 10
