#
# This file is part of the Buildings and Habitats object Model (BHoM)
# Copyright (c) 2015 - 2026, the respective contributors. All rights reserved.
#
# Each contributor holds copyright over their respective contributions.
# The project versioning (Git) records all such contribution source information.
#
#
# The BHoM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3.0 of the License, or
# (at your option) any later version.
#
# The BHoM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this code. If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.
#

import json
from typing import Any, Callable, Union, Dict
from functools import wraps
from ..bhom_object import CONSOLE_LOGGER, BHoMJSONDecoder, BHoMJSONEncoder, BHoMObject, IObject

class _BHoMWrapper:
    _registered_methods: Dict[str, Callable] = {}

    def bhom_callable(self, identifier: str, argument_types:Dict[str, type] = {}, encoder_cls: type = BHoMJSONEncoder, decoder_cls: type = BHoMJSONDecoder):
        """Decorator for functions to be made callable from BHoM C# methods/adapters.

        Note: methods that this wraps must not have "__input_json__" as a default kwarg, as this is used internally to allow BHoM adapters to call the method.

        when __input_json__ is set, this will cause the method to always output BHoM style json (using the encoder_cls provided to this decorator)
    
        Args:
            identifier (str): The unique name C# uses to call the method through run_wrapped.

            argument_types (dict[str, type]): this is a dictionary that is used to map the argument names to types (specifically BHoMObject types) to subclasses of BHoMObjects.
                For example, if you have a class that is a subclass of BHoMObject, the default serialiser will only deserialise json to a BHoMObject.
                To go the extra step to get your class, you must provide the type in this dictionary to allow the wrapper to convert the BHoMObject type to your desired type.

            encoder_cls (JSONEncoder): A JSONEncoder (ideally one that is a subclass of BHoMJSONEncoder). Mainly this is for if a custom encoder has been implemented for a specific toolkit.

            decoder_cls (JSONDecoder): same as encoder_cls but for JSONDecoder.
        """
        def decorator(function: Callable):

            @wraps(function)
            def wrapper(*args, **kwargs) -> Union[str, Any]:

                do_wrap:bool = False

                if "__input_json__" in kwargs and len(args) == 0:
                    do_wrap = True
                
                    #get dictionary from input as file path or json like string.
                    input_json = kwargs.pop("__input_json__")

                    if not input_json.startswith("{"): #assume it's a path
                        with open(input_json, "r") as f:
                            input_json = f.read()

                    try:
                        json_kwargs: Union[dict, IObject] = json.loads(input_json, cls=decoder_cls)
                        if isinstance(json_kwargs, IObject):
                            json_kwargs = json_kwargs.to_dict()
                    except:
                        CONSOLE_LOGGER.error("Could not load JSON from file or string due to invalid JSON. Attempting to run with given args and kwargs.", exc_info=1)

                    #update kwargs with json
                    for kwarg_name in json_kwargs:
                        val = json_kwargs[kwarg_name]

                        if kwarg_name in argument_types:
                            t = argument_types[kwarg_name]

                            if issubclass(t, BHoMObject) and type(json_kwargs[kwarg_name]) is BHoMObject:
                                val = t._from_bhom_object(json_kwargs[kwarg_name])

                        kwargs[kwarg_name] = val

                rtn = function(*args, **kwargs)

                if do_wrap:
                    #don't bother serialising if the method already returns a string.
                    if isinstance(rtn, str):
                        return rtn

                    json_rtn = json.dumps(rtn, cls=encoder_cls)

                    return json_rtn
            
                return rtn

            self._registered_methods[identifier] = wrapper
            return wrapper

        return decorator

    def get_registered_method(self, method_identifier: str):
        method = self._registered_methods.get(method_identifier, None)

        if method is None:
            raise NotImplementedError(f"The requested method {method_identifier} is not implemented or could not be found.")

        return method

#the registered methods are stored as a class attribute, so this isn't actually needed
#but this is easier to use, otherwise a new instance must be created every time a method needs to be wrapped
bhom_wrapper = _BHoMWrapper()