from python_toolkit.bhom.bhom_object import convert_pascal_to_camel, convert_camel_to_pascal, BHoMObject, IObject, BHoMJSONDecoder, BHoMJSONEncoder
import uuid
import json

SERIALISED_BHOM_OBJECT = '{ "_t" : "BH.oM.Adapter.FileSettings", "FileName" : "test.txt", "Directory" : "path/to/file", "BHoM_Guid" : "f428e614-bda1-4228-882e-21d0f318a322", "Name" : "", "_bhomVersion" : "9.2" }' #TODO: use the BHoM serialiser to make a BHoMObject json string, and use that here.
DESERIALISED_BHOM_OBJECT = BHoMObject(_t = "BH.oM.Adapter.FileSettings", bhom_guid = uuid.UUID("f428e614-bda1-4228-882e-21d0f318a322"), file_name = "test.txt", directory = "path/to/file", _bhom_version = "9.2") #TODO: make equivalent BHoMObject here identical to the one above.

SERIALISED_IOBJECT = '{ "_t" : "BH.oM.Geometry.Point", "X" : 0.10000000000000001, "Y" : 0.10000000000000001, "Z" : 0.10000000000000001, "_bhomVersion" : "9.2" }'
DESERIALISED_IOBJECT = IObject(_t = "BH.oM.Geometry.Point", x = 0.10000000000000001, y = 0.10000000000000001, z = 0.10000000000000001, _bhom_version = "9.2")

def test_case_convert():
	"""Test that the camel and pascal converters are working correctly by using expected outputs and a round trip both ways."""
	#TODO: find edge cases within bhom to see if round trip converters work properly.
	#arrange
	test_pascal_str = "ThisIsAPascalCaseString"
	test_camel_str = "this_is_a_camel_case_string"
	expected_pascal_out = "this_is_a_pascal_case_string"
	expected_camel_out = "ThisIsACamelCaseString"

	#act
	pascal_out = convert_pascal_to_camel(test_pascal_str)
	pascal_round_trip = convert_camel_to_pascal(pascal_out)

	camel_out = convert_camel_to_pascal(test_camel_str)
	camel_round_trip = convert_pascal_to_camel(camel_out)

	#assert
	assert pascal_out == expected_pascal_out, f"pascal conversion got '{pascal_out}' but expected '{expected_pascal_out}'."
	assert camel_out == expected_camel_out, f"camel conversion got '{camel_out}' but expected '{expected_camel_out}'."
	assert pascal_round_trip == test_pascal_str, f"pascal round trip got '{pascal_round_trip}' but expected '{test_pascal_str}'."
	assert camel_round_trip == test_camel_str, f"camel round trip got '{camel_round_trip}' but expected '{test_camel_str}'."

def test_serialise_bhom_object():
	"""Test that bhom objects serialise correctly to a format that the c# bhom serialiser accepts as valid, and with the correct property case."""
	#act
	serialised = json.dumps(DESERIALISED_BHOM_OBJECT, cls=BHoMJSONEncoder)
	serialised_bhom_object_to_json = DESERIALISED_BHOM_OBJECT.to_json()
	round_trip = BHoMObject.from_json(serialised)

	#assert
	assert serialised == serialised_bhom_object_to_json, f"Direct serialisation to json differed to BHoMObject to_json method."
	assert round_trip == DESERIALISED_BHOM_OBJECT, f"BHoMObject round trip failed for serialisation -> deserialisation." #this is the only direction the round trip can be tested without directly inspecting each dictionary entry, as it is not guaranteed that the other direction will produce identical order for json strings.

def test_serialise_iobject():
	#act
	serialised = json.dumps(DESERIALISED_IOBJECT, cls=BHoMJSONEncoder)
	serialised_iobject_to_json = DESERIALISED_IOBJECT.to_json()
	round_trip = IObject.from_json(serialised)

	#assert
	assert serialised == serialised_iobject_to_json, f"Direct serialisation to json differed to IObject to_json method."
	assert round_trip == DESERIALISED_IOBJECT, f"IObject round trip failed for serialisation -> deserialisation." #this is the only direction the round trip can be tested without directly inspecting each dictionary entry, as it is not guaranteed that the other direction will produce identical order for json strings.

def test_deserialise_bhom_object():
	"""Test that bhom objects deserialise correctly with no errors with expected properties with correct case."""
	#act
	obj = json.loads(SERIALISED_BHOM_OBJECT, cls=BHoMJSONDecoder)
	obj_bhom_object_from_json = BHoMObject.from_json(SERIALISED_BHOM_OBJECT)

	#assert
	assert isinstance(obj, BHoMObject), "JSON decoded an object of the wrong type"
	assert obj == DESERIALISED_BHOM_OBJECT, f"Actual deserialised object ({obj}) was not identical to expected deserialised object ({DESERIALISED_BHOM_OBJECT})."
	assert obj_bhom_object_from_json == obj, f"Direct deserialisation from json differed to BHoMObject from_json method."

def test_deserialise_iobject():
	"""Test that bhom objects deserialise correctly with no errors with expected properties with correct case."""
	#act
	obj = json.loads(SERIALISED_IOBJECT, cls=BHoMJSONDecoder)
	obj_iobject_from_json = IObject.from_json(SERIALISED_IOBJECT)

	#assert
	assert isinstance(obj, IObject), "JSON decoded an object of the wrong type"
	assert obj == DESERIALISED_IOBJECT, f"Actual deserialised object ({obj}) was not identical to expected deserialised object ({DESERIALISED_IOBJECT})."
	assert obj_iobject_from_json == obj, f"Direct deserialisation from json differed to IObject from_json method."

def test_subclass():
	#arrange
	class TestSubClass(BHoMObject):
		_t: str = "BH.oM.Base.CustomObject"
		some_other_data: str

		def __init__(self, some_other_data, **kwargs):
			self.some_other_data = some_other_data
			_t = kwargs.pop("_t", self._t)
			super().__init__(_t, **kwargs)

	#act
	test_object = TestSubClass("this is some test data")
	test_object_json = test_object.to_json()
	test_object_round_trip = TestSubClass.from_json(test_object_json)

	#assert
	assert test_object == test_object_round_trip
	assert test_object.some_other_data == "this is some test data"
	assert test_object._t == "BH.oM.Base.CustomObject"