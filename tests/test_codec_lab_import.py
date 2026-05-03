import codec_lab


def test_package_importable() -> None:
    assert hasattr(codec_lab, "__version__")
