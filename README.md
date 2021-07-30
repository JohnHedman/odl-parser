# odl-parser
This tool is designed to read ODL (Object Description Language) metadata files and interpret them as a python dictionary.  
There is already a mature tool for reading pvl files: https://github.com/planetarypy/pvl  
The odl-parser differs from the pvl tool by attempting to parse invalid values from key/value pairs in metadata files. 

**Quick Example:**  
Invalid odl/pvl key/value:
```
horizontalCoordSysProj4 = +proj=utm +zone=10 +datum=WGS84 +units=m +no_defs;
END;
```
Attempted JSON key/value conversion:
```json
{
    "horizontalCoordSysProj4": "+proj=utm +zone=10 +datum=WGS84 +units=m +no_defs",
}
```

**Real World Examples:**  
Invalid odl/pvl key/value:              https://github.com/JohnHedman/odl-parser/blob/main/examples/odl/smallsats.txt#L89  
JSON conversion for the same key/value: https://github.com/JohnHedman/odl-parser/blob/main/examples/json/smallsats.json#L90

# Mapping ODL/PVL to a Context-free Grammar
[What is a Context-free Grammar?](https://en.wikipedia.org/wiki/Context-free_grammar)  

## Context-free Grammar Rules
A -> Be | e

B -> GhB | KB | λ

G -> gB

K -> ksv

e -> `END`

g -> `(BEGIN_)?GROUP[ ]+=[ ]+[^;\n]+`  
Examples:  
  - "GROUP = PRODUCT_CONTENTS"  
  - "BEGIN_GROUP = PRODUCT CONTENTS."

h -> `END_GROUP[ ]+=[ ]+[^;\n]+`  
Examples:  
  - "END_GROUP = PRODUCT_CONTENTS"  
  - "END_GROUP = PRODUCT CONTENTS."

k -> `\w.`

s -> `[ ]+=[ ]+`

v -> `string` | `number` | `date` | `list`

# Creating a Recursive Descent Parser from the Context-free Grammar
[What is a Recursive Decent Parser?](https://en.wikipedia.org/wiki/Recursive_descent_parser)  
This tool emulates a Recursive Descent Parser by implementing the Context-free Grammar rules with a class that has methods that follow the same patterns as the rules (and are recursive by the nature of CFG rules).

**Examples:**  
The CFG rule:   
`B -> GhB | KB | λ`  
Maps to the following method:
```python
def _B(self, object_dictionary):
        self._get_next_statement()
        if self.current_statement == "END":
            return object_dictionary
        else:
            key, value = self._get_statement_key_value(self.current_statement)

            if key in ["GROUP", "BEGIN_GROUP"]:
                object_dictionary = self._group_begin(value, object_dictionary)
                self._group_end(value)
            elif key == "END_GROUP":
                return object_dictionary
            else:
                object_dictionary[key] = self._convert_value(value)

        return self._B(object_dictionary)
```

It might be difficult to see how the rules are being followed by this function from a quick glance. Let's try to break it down by rule and see the path through the method for each rule.

## `B -> GhB`
If we were to follow this rule we would go down the following path:  
```python
def _B(self, object_dictionary):
        self._get_next_statement()
        # if self.current_statement == "END":
            # return object_dictionary
        else:
            key, value = self._get_statement_key_value(self.current_statement)

            if key in ["GROUP", "BEGIN_GROUP"]:
                object_dictionary = self._group_begin(value, object_dictionary)
                self._group_end(value)
            # elif key == "END_GROUP":
                 # return object_dictionary
            # else:
                # object_dictionary[key] = self._convert_value(value)

        return self._B(object_dictionary)
```
*Ignore the `_get_next_statement()` & `_get_statement_key_value()` method calls, it is needed for the parser to work but doesn't matter for CFG rules.*  

From following the path you can see that we end up calling the methods `_group_begins()`, `_group_ends()`, and `_B()` in that
exact order.  The method `_group_begins()` actually implements rule `G` as does `_group_ends()` with rule `h`. These methods
were given descriptive names to help for code practices/readability.  So this path ends up following the rules for `B -> GhB`.

The if statement `if key in ["GROUP", "BEGIN_GROUP"]:` should make sense because the rule `G` maps to `G -> gB` and
the rule `g` maps to `g -> (BEGIN_)?GROUP[ ]+=[ ]+[^;\n]+`. So this path (and only this path) ends up creating the
string `GROUP` or `BEGIN_GROUP`. That means if our program reads a `key` with the values `GROUP` or `BEGIN_GROUP` we should
follow the `B -> GhB` rule.  Now you can see how our program (emulating Recursive Descent Parser) follows the Context-free
grammar that we created which follows the specifications for pvl/odl.

*Note: All lowercase rules map to regular expressions, thus creating only terminal symbols (terminal symbols are the actual characters in our string we are reading).*

## `B -> KB`
If we were to follow this rule we would go down the following path:  
```python
def _B(self, object_dictionary):
        self._get_next_statement()
        # if self.current_statement == "END":
            # return object_dictionary
        else:
            key, value = self._get_statement_key_value(self.current_statement)

            # if key in ["GROUP", "BEGIN_GROUP"]:
                # object_dictionary = self._group_begin(value, object_dictionary)
                # self._group_end(value)
            # elif key == "END_GROUP":
                # return object_dictionary
            else:
                object_dictionary[key] = self._convert_value(value)

        return self._B(object_dictionary)
```
*Ignore the `_get_next_statement()` & `_get_statement_key_value()` method calls, it is needed for the parser to work but doesn't matter for CFG rules.*  

The path ends up executing the code `object_dictionary[key] = self._convert_value(value)` which is actually the implementation of
the `K` rule inside of the program. The method `_B()` is also recursively called inside of this path.  Since we ended up
implementing the `K` rule and invoking the method that implements the `B` rule, we have successfully implemented the
`B -> KB` rule inside of this method by following the path.

## `B -> λ`
This rule is a little bit different in that there are multiple paths that follow this rule.
The most simple path is:
```python
def _B(self, object_dictionary):
        self._get_next_statement()
        if self.current_statement == "END":
            return object_dictionary
        # else:
            # key, value = self._get_statement_key_value(self.current_statement)

            # if key in ["GROUP", "BEGIN_GROUP"]:
                # object_dictionary = self._group_begin(value, object_dictionary)
                # self._group_end(value)
            # elif key == "END_GROUP":
                 # return object_dictionary
            # else:
                # object_dictionary[key] = self._convert_value(value)

        # return self._B(object_dictionary)
```
*Ignore the `_get_next_statement()` & `_get_statement_key_value()` method calls, it is needed for the parser to work but doesn't matter for CFG rules.*   

Here you can see that we encountered the string `END` which means we are at the end of our acceptable input.
The only rule that implements the `END` string is the rule `e -> END`.  The only rule that invokes the `e` rule is
`A -> Be | e` and `A` is the starting symbol. This means that `B` was called from the rule `A` and the method `_B()` should return without invoking any other methods, thus implementing `B -> λ`. 

The next path is when the `END_GROUP` reserved word is encountered:
```python
def _B(self, object_dictionary):
        self._get_next_statement()
        # if self.current_statement == "END":
            # return object_dictionary
        else:
            key, value = self._get_statement_key_value(self.current_statement)

            # if key in ["GROUP", "BEGIN_GROUP"]:
                # object_dictionary = self._group_begin(value, object_dictionary)
                # self._group_end(value)
            lif key == "END_GROUP":
                return object_dictionary
            # else:
                # object_dictionary[key] = self._convert_value(value)
```
*Ignore the `_get_next_statement()` & `_get_statement_key_value()` method calls, it is needed for the parser to work but doesn't matter for CFG rules.*  

Since the `END_GROUP` key was encountered and the only rule that produces that string is `h` which maps to `h -> END_GROUP[ ]+=[ ]+[^;\n]+`, we should try to get to the method `h` is implemented inside of.  From our rules we can see that `h` is only invoked inside the rule `B -> GhB` but also that the `G` rule is invoked before h, though. Digging into the rule `G` we can see it
maps to `G -> gB`. By combining the two previous rules we can get `B -> gBhB`.  We can assume that for this string to match our rules, we must be inside of the first `B` in the combined rule.  This means that in order to get to the method that
implements the `h` rule, we must return from inside our `_B()` method without invoking any other methods, thus implementing `B -> λ`.
