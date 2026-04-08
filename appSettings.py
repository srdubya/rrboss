import pathlib
import threading
from functools import wraps
from pydantic import BaseModel, ConfigDict, ValidationError


def debounce_trailing(wait_seconds):
    def decorator(fn):
        lock = threading.Lock()
        timer = None
        last_args = None
        last_kwargs = None

        @wraps(fn)
        def wrapper(*args, **kwargs):
            nonlocal timer, last_args, last_kwargs
            with lock:
                last_args = args
                last_kwargs = kwargs
                if timer:
                    timer.cancel()
                timer = threading.Timer(wait_seconds, lambda: fn(*last_args, **last_kwargs))
                timer.daemon = True
                timer.start()
        return wrapper
    return decorator

class Settings(BaseModel):
    app_height: int = 500
    app_width: int = 600
    saved_contacts: dict[str, list[str]] = {}

    # name: str = 'Jane De'

    @staticmethod
    def from_file(filename) -> Settings:
        model_str = pathlib.Path(filename).read_text()
        try:
            return Settings.model_validate_json(model_str)
        except ValidationError as e:
            print(e)
            return Settings()

    @debounce_trailing(0.5)
    def to_file(self, filename):
        print("Saving", filename)
        text = self.model_dump_json(indent=2)
        pathlib.Path(filename).write_text(text)

    def save_contacts(self, key: str, values: list[str]):
        self.saved_contacts[key] = values
