from readium import ReadConfig, Readium


def test_read_config():
    config = ReadConfig()
    assert config.max_file_size == 5 * 1024 * 1024  # Default 5MB
    assert isinstance(config.exclude_dirs, set)
    assert isinstance(config.include_extensions, set)


def test_readium_init():
    reader = Readium()
    assert reader.config is not None
    assert reader.markitdown is None
