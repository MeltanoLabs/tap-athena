from singer_sdk.typing import DateTimeType, IntegerType, NumberType, StringType, BooleanType
from typing import Any, Dict, Generic, List, Tuple, Type, TypeVar, Union, cast


def to_jsonschema_type(from_type: Union[str, Type]) -> dict:
    """Return the JSON Schema dict that describes the sql type (str) or Python type."""
    sqltype_lookup: Dict[str, dict] = {
        # NOTE: This is an ordered mapping, with earlier mappings taking precedence.
        #       If the SQL-provided type contains the type name on the left, the mapping
        #       will return the respective singer type.
        "timestamp": DateTimeType.type_dict,
        "datetime": DateTimeType.type_dict,
        "date": DateTimeType.type_dict,
        "int": IntegerType.type_dict,
        "number": NumberType.type_dict,
        "decimal": NumberType.type_dict,
        "double": NumberType.type_dict,
        "float": NumberType.type_dict,
        "string": StringType.type_dict,
        "text": StringType.type_dict,
        "char": StringType.type_dict,
        "bool": BooleanType.type_dict,
        "variant": StringType.type_dict,
    }

    if isinstance(from_type, str):
        for sqltype, jsonschema_type in sqltype_lookup.items():
            if sqltype.lower() in from_type.lower():
                return jsonschema_type

        return sqltype_lookup["string"]  # safe failover to str

    if from_type is int:
        return sqltype_lookup["int"]

    if from_type is float:
        return sqltype_lookup["double"]

    return sqltype_lookup["string"]  # safe failover to str
