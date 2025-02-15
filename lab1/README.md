# Topic: Intro to formal languages. Regular grammars. Finite Automata.

### Course: Formal Languages & Finite Automata
### Author: Maxim Isacescu

----
## Objectives:
* Understanding formal languages and finite automata.
* Implementing the grammar and finite automata.
* Generating and validating strings based on the grammar.

## Implementation description
All the code is separated in three parts:
* Grammar class, is responsible for interpreting the grammar and generating valid strings.
* FiniteAutomaton class, is validating the input string (in our case some predefined strings and user input).
* The last part, is just the place where we declaring our grammar, calling generation and validation functions in order to test our program.

```python
class Grammar:
    def __init__(self, VN, VT, P):
        pass

    def generate_valid_string(self):
        pass

    def to_finite_automata(self):
        pass

class FiniteAutomata:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        pass

    def string_validation(self, input_string):
        pass

if __name__ == "__main__":
    pass
```

Our output looks like this:

<img src="lab1_output.png">


## Conclusions
In this laboratory, I've successfully implemented given grammar to create finite automata, which demonstrated the practical relationship between formal language theory and computational models. This project highlighted the main principles of automata theory.

## References
1. Lecture notes
