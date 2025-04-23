# Laboratory Work #5: Chomsky Normal Form
### Course: Formal Languages & Finite Automata
### Author: Isacescu Maxim, FAF-231
### Professors: Cretu Dumitru, Irina Cojuhari

## Theory
In formal language theory, Chomsky Normal Form (CNF) is a standardized representation of context-free grammars (CFGs) where every production rule strictly conforms to one of two formats: either a non-terminal producing exactly two non-terminals (e.g., `A → B C`), or a non-terminal producing a single terminal (e.g., `A → a`). This restricted form simplifies parsing algorithms, such as the CYK algorithm, and facilitates formal analysis of languages. Converting a general CFG into CNF requires a sequence of transformations to eliminate ε-productions (productions that generate the empty string), unit productions (e.g., `A → B`), and useless symbols, followed by restructuring rules into the required binary or terminal forms.

## Objectives
1. Learn about Chomsky Normal Form (CNF).
2. Get familiar with the approaches of normalizing a grammar.
3. Implement a method for normalizing an input grammar by the rules of CNF. The implementation needs to be encapsulated in a method with an appropriate signature (also ideally in an appropriate class/type). The implemented functionality needs executed and tested.

## Implementation
The implementation centers around the conversion of a context-free grammar (CFG) into Chomsky Normal Form (CNF). The main functionality is encapsulated in the Grammar class, where the method `to_cnf()` orchestrates the entire normalization process. This method invokes several internal helpers: `remove_null_productions()`, `remove_unit_productions()`, `remove_useless_symbols()`, and `convert_to_cnf_format()`—each responsible for transforming the grammar to fit CNF constraints.

The first step, handled by `remove_null_productions()`, eliminates ε-productions (rules that derive the empty string). It does so by computing a set of nullable variables and then generating new production combinations by omitting these nullable symbols. While this step doesn't modify your grammar—since it contains no ε-productions—it ensures broader compatibility for any input grammar.

Next, `remove_unit_productions()` addresses unit rules like `A → B`, where both sides are non-terminals. The method constructs a set of unit pairs using a set comprehension:
```python
unit_pairs = {(var, rule[0]) for var in self.variables for rule in self.productions[var] if len(rule) == 1 and rule[0] in self.variables}
```

It then replaces each unit production by recursively adding the target non-terminal’s rules into the source non-terminal, thereby removing indirect dependencies.

The third step, `remove_useless_symbols()`, cleans the grammar by eliminating non-generating and unreachable variables. It first determines which non-terminals can derive terminal strings by analyzing production rules recursively. Then, it filters out those unreachable from the start symbol by building a reachability graph from the start symbol through valid transitions.

The most critical step is convert_to_cnf_format(), which ensures all remaining rules conform strictly to CNF’s structure: either a single terminal (`A → a`) or a pair of non-terminals (`A → B C`). This involves two main transformations. First, it replaces terminal symbols in multi-symbol rules with new intermediate non-terminals, using mappings like:
```python
if sym not in term_map:
    new_var = f"T_{sym.upper()}"
    term_map[sym] = new_var
    new_productions[new_var] = [(sym,)]
```

Second, it converts productions with more than two symbols into binary rules. This is done by introducing new variables recursively:
```python
while len(new_rule) > 2:
    new_var = f"X{len(new_vars)}"
    new_productions[new_var] = [(new_rule[0], new_rule[1])]
    new_rule = [new_var] + new_rule[2:]
```
By applying these transformations sequentially, the grammar is transformed into a valid CNF grammar. This process guarantees that all productions meet CNF requirements, ensuring compatibility with CNF-based parsers and algorithms.



## Results


Input (V18):
<img src="input.png">

Output:
<img src="output.png">


## Conclusions
Converting a context-free grammar to Chomsky Normal Form is a fundamental step in formal language processing, enabling efficient parsing and analysis by standard algorithms. By systematically eliminating null, unit, and useless productions and restructuring rules into binary or terminal forms, any valid grammar can be normalized into CNF. This structured approach not only simplifies the grammar's structure but also lays the groundwork for further computational applications like syntax analysis, parsing, and automaton construction.

