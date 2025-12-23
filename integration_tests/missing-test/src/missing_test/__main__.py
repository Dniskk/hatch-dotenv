# ruff: noqa: S101, T201
import os

if __name__ == "__main__":
    assert os.getenv("SECRET") == "12345", f"SECRET is {os.getenv('SECRET')}"
    print("Test suite 'missing-test' passed")
