from grammar import Grammar

# V18
my_variables = {"S", "A", "B", "C", "D"}
my_terminals = {"a", "b"}
my_start = "S"
my_productions = {
    "S": [("A", "C")],
    "A": [("a",), ("A",), ("S",), ("C",), ("a", "D"), ("b", "A", "B"), ("ε",)],
    "B": [("a",), ("b", "S")],
    "C": [("A", "B")],
    "D": [("B", "B")]
}

g = Grammar(my_variables, my_terminals, my_start, my_productions)
g.to_cnf()
g.print_grammar()
