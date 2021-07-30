
# Mapping ODL/PVL to Context Free Grammar
Link: https://en.wikipedia.org/wiki/Context-free_grammar

A -> BE
     E
     λ

B -> GhB
     KB
     λ

G -> gB

K -> ksv

g -> r"(BEGIN_)?GROUP[ ]+=[ ]+[^;\n]+"
Examples:
  "GROUP = PRODUCT_CONTENTS"
  "BEGIN_GROUP = PRODUCT CONTENTS."

h -> r"END_GROUP[ ]+=[ ]+[^;\n]+"
  "END_GROUP = PRODUCT_CONTENTS"
  "END_GROUP = PRODUCT CONTENTS."

k -> \w.

s -> [ ]+=[ ]+

v -> string | number | date | list