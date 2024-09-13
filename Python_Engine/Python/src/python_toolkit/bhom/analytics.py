"""BHoM analytics decorator."""
# pylint: disable=E0401
import inspect
import json
import sys
import uuid
from functools import wraps
from typing import Any, Callable

# pylint: enable=E0401

from .logging import ANALYTICS_LOGGER
from .util import csharp_ticks
from . import BHOM_VERSION, TOOLKIT_NAME


def bhom_analytics() -> Callable:
    """Decorator for capturing usage data.

    Returns
    -------
    Callable
        The decorated function.
    """

    def decorator(function: Callable):
        """A decorator to capture usage data for called methods/functions.

        Arguments
        ---------
        function : Callable
            The function to decorate.

        Returns
        -------
        Callable
            The decorated function.
        """

        @wraps(function)
        def wrapper(*args, **kwargs) -> Any:
            """A wrapper around the function that captures usage analytics."""

            _id = uuid.uuid4()

            # get the data being passed to the function, expected dtype and return type
            argspec = inspect.getfullargspec(function)[-1]
            argspec.pop("return", None)

            _args = [f'{{"_t": "{argspec[k]}", "Name": "{k}"}}' for k in argspec.keys()]

            exec_metadata = {
                "BHoMVersion": BHOM_VERSION,
                "BHoM_Guid": _id,
                "CallerName": function.__name__,
                "ComponentId": _id,
                "CustomData": {"interpreter", sys.executable},
                "Errors": [],
                "FileId": "",
                "FileName": "",
                "Fragments": [],
                "Name": "",
                # TODO - get project properties from another function/logging
                # method (or from BHoM DLL analytics capture ...)
                "ProjectID": "",
                "SelectedItem": {
                    "MethodName": function.__name__,
                    "Parameters": _args,
                    "TypeName": f"{function.__module__}.{function.__qualname__}",
                    "_bhomVersion": BHOM_VERSION,
                    "_t": "Python",
                },
                "Time": {
                    "$date": csharp_ticks(short=True),
                },
                "UI": "Python",
                "UiVersion": TOOLKIT_NAME,
                "_t": "BH.oM.UI.UsageLogEntry",
            }

            try:
                result = function(*args, **kwargs)
            except Exception as exc:  # pylint: disable=broad-except
                exec_metadata["Errors"].extend(sys.exc_info())
                raise exc
            finally:
                ANALYTICS_LOGGER.info(
                    json.dumps(exec_metadata, default=str, indent=None)
                )

            return result

        return wrapper

    return decorator
