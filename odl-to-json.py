import re
import ast


class OdlParser():
    """ODL Parser Class"""
    def __init__(self, odl_string, statement_termination_symbol="\n"):
        self.odl_string = odl_string
        self.statement_termination_symbol = statement_termination_symbol
        self.object_stack = []

        self._get_odl_statements()

    def convert_to_json(self):
        self._A()

    # FIXME: There is definetly a better way to do this without using temp.
    def _get_odl_statements(self):
        temp = self.odl_string.split(
            self.statement_termination_symbol
        )
        temp = list(map(
            lambda x: x.strip(),
            temp
        ))
        self.odl_statements = list(filter(
            lambda x: x != "",
            temp
        ))
        print(f"ODL Statements: {self.odl_statements}")

    def _get_next_statement(self):
        self.current_statement = self.odl_statements.pop(0)

    def _get_statement_key_value(self, statement):
        m = re.match(r"^(?P<key>\w+)[ ]+=[ ]+(?P<value>.+)$", statement)
        return m.groupdict()["key"], m.groupdict()["value"]

    def _A(self, object_dictionary):
        self._B({})
        self._End()

    def _B(self, object_dictionary):
        self._get_next_statement()
        if self.current_statement == "END":
            return object_dictionary
        else:
            key, value = self._get_statement_key_value(self.current_statement)
            print(f"KEY: '{key}', VALUE: '{value}'")

            if key == "GROUP":
                self._G(value)
            elif key == "END_GROUP":
                return object_dictionary
            else:
                object_dictionary[key] = self._K(value)

        return self._B(object_dictionary)

    def _G(self, object_name):
        self.object_stack.append(object_name)
        object_dictionary = self._A()
        if self.object_stack[-1] != object_name:
            raise ValueError()
        else:
            self.object_stack.pop()
            return object_dictionary

    def _K(self, value):
        # Not sure if ast is the right library to convert strings to
        # different kinds of values (strings, integers, lists)
        return ast.literal_eval(value)

    def _End(self):
        # If there are objects that have not been terminated (END_GROUP = OBJECT_NAME)
        # before the "END" symbol, then we raise an error.
        if not self.object_stack:
            raise ValueError()


def convert(odl_input):
    pass


if __name__ == "__main__":
    with open("./examples/odl/simple_test.txt", 'r') as test_file:
        parser = OdlParser(test_file.read())
        parser.convert_to_json()
