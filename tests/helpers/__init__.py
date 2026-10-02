def assert_worked(result, capfd=None):
    """
    Pass copie.copy()/update() result, assert it worked.
    Optionally, pass ``capfd`` fixture to assert init/migrate worked as well.
    """
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_dir.is_dir()
    if capfd is not None:
        # ensure the environment migration did not fail
        # (it does not cause an exit code > 0 since it's optional)
        assert "Failed migrating environment" not in capfd.readouterr().err
