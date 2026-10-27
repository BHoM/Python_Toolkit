from .decorators import bhom_wrapper
from . import wrapped

def run_wrapped(identifier: str, json: str):
    method = bhom_wrapper.get_registered_method(identifier)

    print(method(__input_json__ = json))