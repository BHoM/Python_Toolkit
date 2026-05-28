import uuid
import re
from typing import List, Dict
import json
from json import JSONEncoder, JSONDecoder
from .logging import CONSOLE_LOGGER

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
            return d
            
        props = {
            "_t": d.pop("_t"),
            "_bhom_version": d.pop("_bhomVersion", None)
        }

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

            return BHoMObject(**props)
        else:
            #deserialise as IObject
            for prop_name in d:
                props[convert_pascal_to_camel(prop_name)] = d[prop_name]

            return IObject(**props)

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
            for prop_name, value in vars(o).items():
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

            for prop_name, value in vars(o).items():
                if prop_name in ["_t", "_bhom_version"]:
                    continue

                props[convert_camel_to_pascal(prop_name)] = value

            return props
        elif isinstance(o, uuid.UUID): #UUID object is not json serialisable by default
            return str(o)
        
        return super(type(self), self).default(o) #fallback to default json decoder if object is not a BHoMObject (don't convert property case).
    
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
        return f"{type(self).__name__} of type {self._t}, version: '{getattr(self, "_bhom_version", "Unknown")}'"

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
    def from_json(cls, j: str) -> 'IObject':
        obj = json.loads(j, cls=BHoMJSONDecoder)

        if not isinstance(obj, cls): #this only tests that the top level object was deserialised correctly, if there are problems with deep properties, change the CONSOLE_LOGGER log level to debug.
            raise TypeError("The object provided does not deserialise to a valid BHoM object.")

        return obj
    
    def to_json(self) -> str:
        return json.dumps(self, cls=BHoMJSONEncoder)

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
        return f"{type(self).__name__} of type {self._t}, name: '{self.name}', version: '{getattr(self, "_bhom_version", "Unknown")}', id: '{self.bhom_guid}'"

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
    def from_json(cls, j: str):
        obj = json.loads(j, cls=BHoMJSONDecoder)

        if issubclass(cls, BHoMObject) and cls != BHoMObject:
            obj = cls._from_bhom_object(obj)

        if not isinstance(obj, cls): #this only tests that the top level object was deserialised correctly, if there are problems with deep properties, change the CONSOLE_LOGGER log level to debug.
            raise TypeError("The object provided does not deserialise to a valid BHoM object.")

        return obj
    
    @classmethod
    def _from_bhom_object(cls, o: 'BHoMObject'):
        return cls(**vars(o).copy()) #assuming that the sub class is correctly set up, then this should work