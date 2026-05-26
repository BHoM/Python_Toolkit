from python_toolkit.bhom.bhom_object import convert_pascal_to_camel, convert_camel_to_pascal, BHoMObject, BHoMJSONDecoder, BHoMJSONEncoder
import json

SERIALISED_BHOM_OBJECT = '{"_t": "BH.oM.Base.BHoMObject", "Name": "test_object"}' #TODO: use the BHoM serialiser to make a BHoMObject json string, and use that here.
DESERIALISED_BHOM_OBJECT = BHoMObject(name = "test_object") #TODO: make equivalent BHoMObject here identical to the one above.

def test_case_convert():
	"""Test that the camel and pascal converters are working correctly by using expected outputs and a round trip both ways."""

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

def test_serialise_bhom_object()
	"""Test that bhom objects serialise correctly to a format that the c# bhom serialiser accepts as valid, and with the correct property case."""

	serialised = json.dumps(DESERIALISED_BHOM_OBJECT, encoder=BHoMJSONEncoder)
	serialised_bhom_object_to_json = DESERIALISED_BHOM_OBJECT.to_json()
	round_trip = BHoMObject.from_json(serialised)

	assert serialised == serialised_bhom_object_to_json, f"Direct serialisation to json differed to BHoMObject to_json method."
	assert round_trip == DESERIALISED_BHOM_OBJECT, f"BHoMObject round trip failed for serialisation -> deserialisation." #this is the only direction the round trip can be tested without directly inspecting each dictionary entry, as it is not guaranteed that the other direction will produce identical order for json strings.

def test_deserialise_bhom_object()
	"""Test that bhom objects deserialise correctly with no errors with expected properties with correct case."""

	obj = json.loads(SERIALISED_BHOM_OBJECT, decoder=BHoMJSONDecoder)
	obj_bhom_object_from_json = BHoMObject.from_json(SERIALISED_BHOM_OBJECT)

	assert isinstance(obj, BHoMObject), "JSON decoded an object of the wrong type"
	assert obj == DESERIALISED_BHOM_OBJECT, f"Actual deserialised object ({obj}) was not identical to expected deserialised object ({DESERIALISED_BHOM_OBJECT})."
	assert obj_bhom_object_from_json == obj, f"Direct deserialisation from json differed to BHoMObject from_json method."