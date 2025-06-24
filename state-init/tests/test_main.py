from state_init.main import main


def test_main_output(capsys):
    main()
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out
