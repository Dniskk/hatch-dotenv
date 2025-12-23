# ruff: noqa: S101, T201
import os

if __name__ == "__main__":
    assert os.getenv("MY_SECRET") == "abcde", f"MY_SECRET is {os.getenv('MY_SECRET')}"
    assert os.getenv("MY_SECOND_SECRET") == "secret", f"MY_SECOND_SECRET is {os.getenv('MY_SECOND_SECRET')}"
    print("Test suite 'happy-test' passed")
