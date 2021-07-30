import re
import json
import odl_expressions


class OdlParserError(Exception):
    pass


class OdlParser():
    """ODL Parser Class"""
    def __init__(self, odl_string, statement_termination_symbol="\n"):
        self.odl_string = odl_string
        self.statement_termination_symbol = statement_termination_symbol
        self.object_stack = []

        self._get_odl_statements()

    def _get_odl_statements(self):
        temp = self.odl_string.replace(";", "\n").split(
            self.statement_termination_symbol
        )

        self.odl_statements = list(filter(
            lambda x: x != "",
            list(map(
                lambda x: x.strip(),
                temp
            ))
        ))

    def convert_to_json(self):
        self._A()

    def _A(self):
        odl_dictionary = self._B({})
        self._End(odl_dictionary)

    def _B(self, object_dictionary):
        self._get_next_statement()
        if self.current_statement == "END":
            return object_dictionary
        else:
            key, value = self._get_statement_key_value(self.current_statement)

            if key in ["GROUP", "BEGIN_GROUP"]:
                object_dictionary = self._group_begin(value, object_dictionary)
            elif key == "END_GROUP":
                self._group_end(value)
                return object_dictionary
            else:
                object_dictionary[key] = self._convert_value(value)

        return self._B(object_dictionary)

    def _group_begin(self, object_name, object_dictionary):
        self.object_stack.append(object_name)
        object_dictionary[object_name] = self._B({})
        return object_dictionary

    def _group_end(self, object_name):
        if not self.object_stack:
            raise OdlParserError()
        if self.object_stack[-1] != object_name:
            raise OdlParserError()
        self.object_stack.pop()

    def _convert_value(self, value):
        number_match = self.check_number_value(value)
        if number_match is not None:
            return number_match

        string_match = self.check_string_value(value)
        if string_match is not None:
            return string_match

        datetime_match = self.check_datetime_value(value)
        if datetime_match is not None:
            return datetime_match

        return value
        # raise OdlParserError(f"Could not match value '{value}' to a valid json type!")

    def _End(self, odl_dictionary):
        # If there are objects that have not been terminated (END_GROUP = OBJECT_NAME)
        # before the "END" symbol, then we raise an error.
        # TODO: Put error checking in for statements after "END" statement.
        if self.object_stack:
            raise OdlParserError()
        # If there aren't any errors, finalize by
        # creating an attribute on the object.
        self.odl_dictionary = odl_dictionary

    def _get_next_statement(self):
        self.current_statement = self.odl_statements.pop(0)

    def _get_statement_key_value(self, statement):
        m = re.match(odl_expressions.key_value_expression, statement)
        return m.groupdict()["key"], m.groupdict()["value"]

    @classmethod
    def check_number_value(self, value):
        m = re.match(odl_expressions.number_expression, value)
        if m:
            m_dict = m.groupdict()
            if m_dict["decimal"] or m_dict["power"]:
                return float(f'{m_dict["sign"] if m_dict["sign"] else ""}{m_dict["integer"] if m_dict["integer"] else ""}{m_dict["decimal"] if m_dict["decimal"] else ""}{m_dict["power"] if m_dict["power"] else ""}')  # noqa: E501
            if m_dict["integer"]:
                return int(f'{m_dict["sign"] if m_dict["sign"] else ""}{m_dict["integer"]}')  # noqa: E501
            # Only zero remains.
            else:
                return 0
        else:
            return None

    @classmethod
    def check_string_value(self, value):
        for expression in odl_expressions.string_expressions:
            m = re.match(expression, value)
            if m:
                return m.groupdict()["string_content"]
        return None

    @classmethod
    def check_datetime_value(self, value):
        for expression in odl_expressions.datetime_expressions:
            m = re.match(expression, value)
            if m:
                return value
        return None


def convert_to_dict(odl_string):
    parser = OdlParser(odl_string)
    parser.convert_to_json()
    return parser.odl_dictionary


if __name__ == "__main__":
    test_file = "./examples/odl/simple_test.txt"
    with open(test_file, 'r') as input_file:
        odl_dictionary = convert_to_dict(input_file.read())
    with open("./converted.json", "w") as output_file:
        json.dump(odl_dictionary, output_file, indent=4)
