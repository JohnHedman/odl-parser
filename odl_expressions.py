key_value_expression = r"^(?P<key>\w+)[ ]+=[ ]+(?P<value>.+)$"

number_expression = r"^(?P<sign>[+\-])?(?P<leading_zeros>0*)?(?P<integer>[1-9]\d*)?(?P<decimal>\.\d*)?(?P<power>[e|E][+\-]?\d+)?$"  # noqa: E501

datetime_expressions = [
    # examples that this re will match: 2020-10-29T11:30:51.000000Z, 2019-05-14
    r"^(\d{4}-\d{2}-\d{2})(T|-)?(\d{2}(:\d{2}){0,2}(\.\d*)?(Z)?)?$",
    # examples that this re will match: 10-29-2020T11:30:51.000000Z, 05-14-2019
    r"^(\d{2}-\d{2}-\d{4})(T|-)?(\d{2}(:\d{2}){0,2}(\.\d*)?(Z)?)?$",
]

string_expressions = [
    r"^\"(?P<string_content>[^\"]*)\"$",
    r"^'(?P<string_content>[^']*)'$"
]
