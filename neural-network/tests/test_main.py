from neural_network.main import dummy_test


def test_main_output():
    value = dummy_test(10)
    assert value, 10
