
SERIALISED_BHOM_OBJECT = '{}'

from python_toolkit.bhom.bhom_object import convert_pascal_to_camel, convert_camel_to_pascal, BHoMObject, BHoMJSONDecoder, BHoMJSONEncoder

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
	assert False #fail for now as test is not done

def test_deserialise_bhom_object()
	"""Test that bhom objects deserialise correctly with no errors with expected properties with correct case."""
	assert False #fail for now as test is not done