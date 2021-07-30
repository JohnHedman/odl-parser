
# Mapping ODL/PVL to Context Free Grammar
Link: https://en.wikipedia.org/wiki/Context-free_grammar

A -> BE | E

B -> GhB | KB | λ

G -> gB

K -> ksv

E -> `END`

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

# Creating a Recursive Descent Parser from Context FreeGrammar
