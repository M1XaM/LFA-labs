import random

class Grammar:
    def __init__(self, VN, VT, P):
        self.VN = VN
        self.VT = VT
        self.P = P
        self.start_symbol = "S"

    def generate_valid_string(self):
        current = self.start_symbol        
        while any(symbol in self.VN for symbol in current):  # while VN exists
            new_string = ""
            for symbol in current:
                if symbol in self.VN:
                    new_string += random.choice(self.P[symbol])  # random production rule
                else:
                    new_string += symbol  # keep terminal symbols
            current = new_string
        return current

    def to_finite_automata(self):
        states = set(self.VN) | {""}
        alphabet = set(self.VT)
        transitions = {}
        start_state = self.start_symbol
        final_states = {""}

        for non_terminal, rules in self.P.items():
            for rule in rules:
                if len(rule) == 1 and rule in self.VT:
                    # If rule produces single terminal, transition to empty string
                    if (non_terminal, rule) not in transitions:
                        transitions[(non_terminal, rule)] = set()
                    transitions[(non_terminal, rule)].add("")
                elif len(rule) >= 1:
                    # For rules with terminal followed by non-terminal
                    first_symbol = rule[0]  # First symbol (terminal)
                    next_state = rule[1:] if len(rule) > 1 else ""  # Rest is next state or empty
                    
                    if (non_terminal, first_symbol) not in transitions:
                        transitions[(non_terminal, first_symbol)] = set()
                    transitions[(non_terminal, first_symbol)].add(next_state)

        return FiniteAutomata(states, alphabet, transitions, start_state, final_states)


class FiniteAutomata:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def string_validation(self, input_string):
        current_states = {self.start_state}
        for symbol in input_string:
            next_states = set()
            for state in current_states:
                if (state, symbol) in self.transitions:
                    next_states.update(self.transitions[(state, symbol)])
            current_states = next_states
            if not current_states:
                return False
        return bool(current_states & self.final_states)


if __name__ == "__main__":
    # Varianta 18
    VN = {"S", "A", "B", "C"}
    VT = {"a", "b"}
    P = {
        "S": ["aA", "aB"],
        "A": ["bS"],
        "B": ["aC"],
        "C": ["a", "bS"]
    }

    grammar = Grammar(VN, VT, P)

    print("Generate already valid strings:")
    generated_strings = [print(grammar.generate_valid_string()) for _ in range(5)]

    print("\nTesting random strings:")
    test_strings = ["aba", "aaba", "ababa", "aaa", "abba", "ababaaa"]
    fa = grammar.to_finite_automata()
    for string in test_strings:
        print(f"{string}:{fa.string_validation(string)}")
    while True:
        user_input = input("Enter any other random string (or empty to end): ")
        if user_input == "":
            print("Exiting")
            break
        print(f"{user_input}: {fa.string_validation(user_input)}\n")