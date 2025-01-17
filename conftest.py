import pytest


def pytest_configure(config):
    config.option.capture = "no"
