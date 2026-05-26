import uuid
import re
from typing import List, Dict
import json
from json import JSONEEncoder, JSONDecoder
from .logging import CONSOLE_LOGGER

def convert_pascal_to_camel(s: str):
	"""Converts a string to camel_case."""
	sections = re.split("(?<=.)(?=[A-Z])", s) #zero-length match before capitals, skipping capital at the 0th index
	parts = []
	for sec in sections:
		parts.append(sec.lower())

	return parts.join("_")

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
		super().__init__(self, object_hook=self.object_hook, *args, **kwargs)

	def object_hook(self, d):
		if "_t" not in d:
			CONSOLE_LOGGER.debug(f"BHoMJSONDecoder could not convert the following dictionary into a BHoMObject due to a missing '_t' property. Falling back to dictionary: {d}")
			return d

		#get default BHoMObject properties and replace with defaults if not present
		name = d.pop("Name", "")
		bhom_guid = d.pop("BHoM_Guid", uuid.uuid4())
		tags = d.pop("Tags", [])
		fragments = d.pop("Fragments", {})
		custom_data = d.pop("CustomData", {})
		_t = d.pop("_t")

		#convert all properties to camel_case as python users expect
		props = {}
		for prop_name in d:
			props[convert_pascal_to_camel(prop_name)] = d[prop_name]

		return BHoMObject(name, bhom_guid, tags, fragments, custom_data, _t, **props)

class BHoMJSONEncoder(JSONEncoder):
	def default(self, o):
		if isinstance(o, BHoMObject):
			#initialise special BHoMObject properties
			props = {
				"Name": o.name,
				"BHoM_Guid": o.bhom_guid,
				"Tags": o.tags,
				"Fragments": o.fragments,
				"CustomData": o.custom_data,
				"_t": o._t
			}

			#get property names with reflection and convert all properties to PascalCase as the BHoM serialiser expects
			for prop_name, value in vars(o).items():
				if prop_name in ["name", "bhom_guid", "tags", "fragments", "custom_data", "_t"]
					continue
				props[convert_camel_to_pascal(prop_name)] = value

			return props
			
		return super(BHoMJSONDecoder, self).default(o) #fallback to default json decoder if object is not a BHoMObject (don't convert property case).
	
class BHoMObject:
	name: str
	bhom_guid: uuid.UUID
	tags: List[str]
	fragments: Dict[type, object]
	custom_data: Dict[str, object]
	_t: str

	def __init__(
		self,
		name: str = "",
		bhom_guid: uuid.UUID = uuid.uuid4(),
		tags: List[str] = [],
		fragments: Dict[type, object] = {},
		custom_data: Dict[str, object] = {},
		_t: str = "BH.oM.Base.BHoMObject"
		**kwargs
	) -> BHoMObject:

		self.name = name
		self.bhom_guid = bhom_guid
		self.fragments = fragments
		self.tags = tags
		self.custom_data = custom_data
		self._t = _t

		#set non-CustomData properties with reflection.
		for kwarg in kwargs:
			setattr(self, kwarg, kwargs[kwarg])

	@classmethod
	def from_json(j: str) -> 'BHoMObject':
		obj = json.loads(json, decoder=BHoMJSONDecoder)

		if not isinstance(obj, BHoMObject): #this only tests that the top level object was deserialised correctly, if there are problems with deep properties, change the CONSOLE_LOGGER log level to debug.
			raise TypeError("The object provided does not deserialise to a valid BHoM object.")

		return obj
	
	def to_json(self) -> str:
		s = json.dumps(self, encoder=BHoMJSONEncoder)
		return s