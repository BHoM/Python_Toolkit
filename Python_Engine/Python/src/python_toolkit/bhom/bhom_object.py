import uuid
from typing import List, Dict
from json import JSONEEncoder, JSONDecoder
from .. import TOOLKIT_NAME


class BHoMJSONDecoder(JSONDecoder):
	
class BHoMJSONEncoder(JSONEncoder):
	def default(self, o):
		return o.__dict__
	

class BHoMObject:
	def __init__(
		self,
		name: str = "",
		bhom_guid: uuid.UUID = uuid.uuid4(),
		tags: List[str] = [],
		fragments: Dict[type, object] = {},
		custom_data: Dict[str, object] = {}
	) -> BHoMObject:

		self.name = name
		self.bhom_guid = bhom_guid
		self.fragments = fragments
		self.tags = tags
		self.custom_data = custom_data

	@property
	def namespace(self):
		return "BH.oM.Python"
		
	@property
	def _t(self):
		return namespace + "." + type(self).__name__