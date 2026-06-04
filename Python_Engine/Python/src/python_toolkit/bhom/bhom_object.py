from base64 import decode
import copy
from ctypes import ArgumentError
from json import encoder
from pathlib import Path
import uuid
import re
from typing import Any, List, Dict, Union
import json
from json import JSONEncoder, JSONDecoder
from .logging import CONSOLE_LOGGER
from . import BHOM_VERSION
import pandas as pd
import numpy as np

BHOM_SHORT_VERSION = ".".join(BHOM_VERSION.split(".")[0:2])

def convert_pascal_to_camel(s: str):
    """Converts a string to camel_case."""
    sections = re.split("(?<=.)(?=[A-Z])", s) #zero-length match before capitals, skipping capital at the 0th index
    parts = []
    for sec in sections:
        parts.append(sec.lower())

    return "_".join(parts)

def convert_camel_to_pascal(s: str):
    """Converts a string to PascalCase, ignoring _ if it is the first character."""
    sections = re.split(r'(?<=.)_', s) #match all `_` except if it is the first character.

    parts = []
    for sec in sections: #capitalise each section unless the section is empty (in which case, append an underscore) or the section starts with an underscore (first section can begin with _)
        if sec == "":
            parts.append("_")
            continue
        elif sec.startswith("_"):
            parts.append(sec)

        parts.append(sec.capitalize())

    return  ''.join(parts)

class BHoMJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, d):
        if "_t" not in d:
            CONSOLE_LOGGER.debug(f"BHoMJSONDecoder could not convert the following dictionary into a BHoMObject due to a missing '_t' property. Falling back to dictionary: {d}")
            return self.deserialise_unknown(d)
            
        props = {
            "_t": d.pop("_t"),
            "_bhom_version": d.pop("_bhomVersion", BHOM_SHORT_VERSION)
        }

        if (props["_bhom_version"] is not None) and (props["_bhom_version"] != BHOM_SHORT_VERSION):
            CONSOLE_LOGGER.warning(f"The bhom version specified in the encoded json ({props['_bhom_version']}) is different from the BHoM version that python_toolkit was installed with ({BHOM_SHORT_VERSION}). There may be versioning issues with this object. Consider deserialising and then serialising again with the BHoM serialiser to get the correct version, or update BHoM to the correct version.")

        if d.get("BHoM_Guid", None) is not None:
            #deserialise as BHoM Object

            #get default BHoMObject properties and replace with defaults if not present
            props["name"] = d.pop("Name", "")
            props["bhom_guid"] = uuid.UUID(d.pop("BHoM_Guid"))
            props["tags"] = d.pop("Tags", [])
            props["fragments"] = d.pop("Fragments", [])
            props["custom_data"] = d.pop("CustomData", {})

            #convert all other properties to camel_case as python users expect
            for prop_name in d:
                props[convert_pascal_to_camel(prop_name)] = d[prop_name]

            return self.deserialise_unknown(BHoMObject(**props))
        else:
            if props["_t"].startswith("System.Collections.Generic.List"): #this handles when the BHoM serialiser makes generic lists from CustomObject list properties, which get converted to a dictionary. The BHoM serialiser does recognise lists if it can find the object definition via reflection.
                return d["_v"]

            #deserialise as IObject
            for prop_name in d:
                props[convert_pascal_to_camel(prop_name)] = d[prop_name]

            return self.deserialise_unknown(IObject(**props))

    def deserialise_unknown(self, obj: Union['IObject', 'BHoMObject', dict]):
        """Override this method in a subclass to add extra object hook on top of the existing method. If the object is an object serialised by the BHoM serialiser, the output object will be a BHoMObject or IObject, so use isinstance() to select."""
        return obj


class BHoMJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, BHoMObject):
            #initialise special BHoMObject properties

            props = {
                "Name": o.name,
                "BHoM_Guid": str(o.bhom_guid),
                "_t": o._t
            }

            if len(o.tags) > 0:
                props["Tags"] = o.tags

            if len(o.fragments) > 0:
                props["Fragments"] = o.fragments

            if len(o.custom_data) > 0:
                props["CustomData"] = o.custom_data

            if o._bhom_version is not None:
                props["_bhomVersion"] = o._bhom_version

            #get property names with reflection and convert all properties to PascalCase as the BHoM serialiser expects
            for prop_name, value in vars(o).copy().items():
                if prop_name in ["name", "bhom_guid", "tags", "fragments", "custom_data", "_t", "_bhom_version"]:
                    continue

                props[convert_camel_to_pascal(prop_name)] = value

            return props
        elif isinstance(o, IObject):
            props = {
                "_t": o._t
            }

            if o._bhom_version is not None:
                props["_bhomVersion"] = o._bhom_version

            for prop_name, value in vars(o).copy().items():
                if prop_name in ["_t", "_bhom_version"]:
                    continue

                props[convert_camel_to_pascal(prop_name)] = value

            return props
        #handle common non-serialisable types
        elif isinstance(o, uuid.UUID): #UUID object is not json serialisable by default
            return str(o)
        elif isinstance(o, pd.DatetimeIndex):
            return [date.isoformat() for date in o]
        elif isinstance(o, np.ndarray):
            return o.tolist()
        elif isinstance(o, pd.Timestamp):
            return o.isoformat()
        elif isinstance(o, pd.Series):
            return dict(zip(o.index.astype(str), o))
        elif isinstance(o, Path):
            return { "FileName": str(o.name), "Directory": str(o.parent), "_t": "BH.oM.Adapter.FileSettings", "BHoM_Guid": str(uuid.uuid4()) }

        return self.serialise_unknown(o) #if the object is unknown at this point, call serialise_unknown to allow subclasses to add their own serialisation logic.

    def serialise_unknown(self, obj: Any) -> Union[Dict[str, str], str, List[str], Any]:
        """
        This is called by the BHoMJSONEncoder to serialise unknown objects so that the BHoM can handle them if they exist as BHoM Objects in c# but not in python (i.e. an object from an external library).

        Override this method in a sub class with its own logic, and call super().serialise_unknown(obj) for objects that are unknown, or do not wish to serialise.
        The following objects won't be passed to this method: BHoMObject, IObject, uuid.UUID, pandas.DatetimeIndex, numpy.ndarray, pandas.Timestamp, pandas.Series, pathlib.Path
        """
        return super(type(self), self).default(obj) #fallback to default json decoder (ValueError) if object is not a BHoMObject or common serialisable type.

    
class IObject:
    """More generic version of BHoMObject, for non-native objects serialised by the BHoM serialiser, but do not inherit from BHoMObject."""
    _t: str
    _bhom_version: str

    def __init__(
        self,
        _t: str,
        _bhom_version: str = None,
        **kwargs
    ) -> 'IObject':
        self._t = _t
        self._bhom_version = _bhom_version
        
        #set properties with reflection.
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    def __repr__(self) -> str:
        return f"{type(self).__name__} of type {self._t}, version: '{getattr(self, '_bhom_version', 'Unknown')}'"

    def __eq__(self, other) -> bool:
        if not isinstance(other, IObject):
            return False

        if self._t != other._t:
            return False
            
        vself = vars(self).copy()
        vother = vars(other).copy()

        #ignore these properties when comparing by property.
        ignore = ["_bhom_version"]
        _ = [(vself.pop(p, None), vother.pop(p, None)) for p in ignore]

        return vself == vother

    @classmethod
    def from_json(cls, j: str, decoder_class: type = BHoMJSONDecoder) -> 'IObject':
        obj = json.loads(j, cls=decoder_class)

        if not isinstance(obj, cls): #this only tests that the top level object was deserialised correctly, if there are problems with deep properties, change the CONSOLE_LOGGER log level to debug.
            raise TypeError("The object provided does not deserialise to a valid BHoM object.")

        return obj
    
    def to_json(self, encoder_class: type = BHoMJSONEncoder) -> str:
        return json.dumps(self, cls=encoder_class)

    @classmethod
    def from_dict(cls, d: dict) -> 'IObject':
        try:
            return cls(**d) #should be valid as long as the dictionary has all necessary entries.
        except ArgumentError as ae:
            raise ArgumentError("Input dictionary was missing some required arguments, see traceback for more information.") from ae

    def to_dict(self, encoder_class: type = BHoMJSONEncoder) -> dict:
        """Convert this IObject to a dictionary via deep copying vars(self)."""
        return copy.deepcopy(vars(self))

class BHoMObject(IObject):
    name: str
    bhom_guid: uuid.UUID
    tags: List[str]
    fragments: List[Dict[str, object]]
    custom_data: Dict[str, object]

    def __init__(
        self,
        _t: str, #don't make default, as subclasses of this class should set this with super().__init__
        name: str = "",
        bhom_guid: uuid.UUID = uuid.uuid4(),
        tags: List[str] = [],
        fragments: List[Dict[str, object]] = [],
        custom_data: Dict[str, object] = {},
        _bhom_version: str = None,
        **kwargs
    ) -> 'BHoMObject':
        self._t = _t
        self.name = name
        self.bhom_guid = bhom_guid
        self.fragments = fragments
        self.tags = tags
        self.custom_data = custom_data
        self._bhom_version = _bhom_version

        #set non-CustomData properties with reflection.
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])

    def __repr__(self) -> str:
        return f"{type(self).__name__} of type {self._t}, name: '{self.name}', version: '{getattr(self, '_bhom_version', 'Unknown')}', id: '{self.bhom_guid}'"

    def __eq__(self, other) -> bool:
        if not isinstance(other, BHoMObject):
            return False

        if self._t != other._t:
            return False

        vself = vars(self).copy()
        vother = vars(other).copy()

        #ignore these properties when comparing by property.
        ignore = ["bhom_guid", "_bhom_version"]
        _ = [(vself.pop(p, None), vother.pop(p, None)) for p in ignore]

        return vself == vother

    @classmethod
    def from_json(cls, j: str, decoder_class: type = BHoMJSONDecoder):
        obj = json.loads(j, cls=decoder_class)

        if isinstance(obj, list):
            CONSOLE_LOGGER.warning("The root element of the JSON provided was a list, assuming that the first item is the desired object. If you intended to deserialise a list, please use the `<cls>.from_json_array(j)` method instead.")
            obj = obj[0]

        if issubclass(cls, BHoMObject) and cls != BHoMObject:
            obj = cls._from_bhom_object(obj)

        if not isinstance(obj, cls): #this only tests that the top level object was deserialised correctly, if there are problems with deep properties, change the CONSOLE_LOGGER log level to debug.
            raise TypeError("The object provided does not deserialise to a valid BHoM object.")

        return obj
    
    @classmethod
    def from_json_array(cls, j: str, decoder_class: type = BHoMJSONDecoder):
        objs = json.loads(j, cls=decoder_class)

        if not isinstance(objs, list):
            raise TypeError("The root element of the JSON provided was not a JSON array. Perhaps you intended to use `<cls>.from_json(j)` instead?")

        out = []
        for obj in objs:
            if issubclass(cls, BHoMObject) and cls != BHoMObject:
                out.append(cls._from_bhom_object(obj))
                continue
            out.append(obj)

        return out

    @classmethod
    def _from_bhom_object(cls, o: 'BHoMObject'):
        return cls(**vars(o).copy()) #assuming that the sub class is correctly set up, then this should work