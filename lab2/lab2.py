import random

class Grammar:
    def __init__(self, VN, VT, P, start_symbol="S"):
        self.VN = VN
        self.VT = VT
        self.P = P
        self.start_symbol = start_symbol

    def classify_grammar(self):
        is_type_3_right = True  # Right-linear Regular
        is_type_3_left = True  # Left-linear Regular
        is_type_2 = True  # Context-Free
        is_type_1 = True  # Context-Sensitive
        
        # Check if S -> ε is the only empty production
        has_empty_production = False
        for lhs, rules in self.P.items():
            for rule in rules:
                if rule == "":  # Empty string (epsilon)
                    if lhs != self.start_symbol or has_empty_production:
                        is_type_1 = False  # Multiple empty productions not allowed in CSG
                    has_empty_production = True

        for lhs, rules in self.P.items():
            # Check if LHS is a single non-terminal
            if len(lhs) != 1 or lhs not in self.VN:
                is_type_2 = is_type_3_right = is_type_3_left = False
                
            for rule in rules:
                if rule == "":  # Skip empty production for type 3 check
                    is_type_3_right = is_type_3_left = False
                    continue
                    
                # Check right-linear: all symbols are terminals except possibly the last one
                if any(c in self.VN for c in rule[:-1]):
                    is_type_3_right = False
                
                # Check left-linear: first symbol may be non-terminal, rest must be terminals
                if len(rule) > 1 and (rule[0] not in self.VN or any(c in self.VN for c in rule[1:])):
                    is_type_3_left = False
                
                # For Type 1 (Context-Sensitive), |LHS| <= |RHS| except S -> ε
                if len(rule) < len(lhs) and not (lhs == self.start_symbol and rule == ""):
                    is_type_1 = False

        if is_type_3_right or is_type_3_left:
            return "Type 3: Regular Grammar"
        if is_type_2:
            return "Type 2: Context-Free Grammar"
        if is_type_1:
            return "Type 1: Context-Sensitive Grammar"
        return "Type 0: Unrestricted Grammar"

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

    def print_grammar(self):
        vn_str = "VN = {" + ", ".join(f"'{symbol}'" for symbol in self.VN) + "}"
        vt_str = "VT = {" + ", ".join(f"'{symbol}'" for symbol in self.VT) + "}"
        
        p_str = "P = {\n"
        for lhs, rules in self.P.items():
            rules_str = ", ".join(f"'{rule}'" if rule else "'ε'" for rule in rules)
            p_str += f"    '{lhs}': [{rules_str}],\n"
        p_str += "}"

        start_str = f"Start Symbol = '{self.start_symbol}'"
        grammar_str = f"{vn_str}\n{vt_str}\n{p_str}\n{start_str}"
        print(grammar_str)

class FiniteAutomata:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

        self.full_transitions = {}
        for key, value in transitions.items():
            self.full_transitions[key] = set(value)

    def string_validation(self, input_string):
        current_states = {self.start_state}
        
        for symbol in input_string:
            if symbol not in self.alphabet:
                return False
                
            next_states = set()
            for state in current_states:
                # Add all possible next states for this state and symbol
                if (state, symbol) in self.full_transitions:
                    next_states.update(self.full_transitions[(state, symbol)])

            if not next_states:
                return False
        return bool(current_states & self.final_states)

    def is_deterministic(self):
        # Check if any state lacks a transition for any alphabet symbol
        for state in self.states:
            for symbol in self.alphabet:
                if isinstance(state, frozenset):
                    # For DFA with composite states
                    if (state, symbol) not in self.transitions:
                        continue  # Missing transitions are allowed
                    if len(self.transitions[(state, symbol)]) != 1:
                        return False
                else:
                    # For original FA
                    if (state, symbol) not in self.transitions:
                        continue  # Missing transitions are allowed
                    if len(self.transitions[(state, symbol)]) > 1:
                        return False
        return True

    def convert_to_dfa(self):
        dfa_states = set()
        dfa_transitions = {}
        dfa_final_states = set()
        
        # Start with the start state
        start_state_set = frozenset([self.start_state])
        unmarked_states = [start_state_set]
        dfa_states.add(start_state_set)
        
        # Process all unmarked state sets
        while unmarked_states:
            current_state_set = unmarked_states.pop(0)
            
            # Check if this is a final state
            if any(state in self.final_states for state in current_state_set):
                dfa_final_states.add(current_state_set)
            
            # For each symbol in the alphabet
            for symbol in self.alphabet:
                next_state_set = set()
                for state in current_state_set:
                    if (state, symbol) in self.full_transitions:
                        next_state_set.update(self.full_transitions[(state, symbol)])
                next_state_set = frozenset(next_state_set)

                if not next_state_set:
                    continue  # No transition for this symbol
                
                # Add the transition
                dfa_transitions[(current_state_set, symbol)] = {next_state_set}
                
                # If this is a new state, add it to be processed
                if next_state_set not in dfa_states:
                    dfa_states.add(next_state_set)
                    unmarked_states.append(next_state_set)

        return FiniteAutomata(
            dfa_states,
            self.alphabet,
            dfa_transitions,
            start_state_set,
            dfa_final_states
        )

    def convert_to_grammar(self):
        Vn = self.alphabet
        Vt = self.states
        S = self.start_state
        P = {}

        for key, values in self.transitions.items():
            for value in values:
                if key[0] not in P.keys():
                    P[key[0]] = [key[1] + value]
                else:
                    if key[0] in self.final_states:
                        P[key[0]].append(key[1])
                    P[key[0]].append(key[1] + value)

        return Grammar(
        VN = Vn,
        VT = Vt,
        P = P,
        start_symbol= S
        )
    
    def print_transitions(self):
        print("Transitions:")
        for (state, symbol), next_states in sorted(self.transitions.items()):
            print(f"  δ({state}, {symbol}) = {next_states}")

if __name__ == "__main__":
    # Varianta 18 lab1 input
    VN = {"S", "A", "B", "C"}
    VT = {"a", "b"}
    P = {
        "S": ["aA", "aB"],
        "A": ["bS"],
        "B": ["aC"],
        "C": ["a", "bS"]
    }

    # Lab2 task
    grammar = Grammar(VN, VT, P)
    print("Grammar Classification:", grammar.classify_grammar())

    # Varianta 18 lab2 input
    Q = {"q0", "q1", "q2", "q3"}
    Sigma = {"a", "b", "c"}
    F = {"q3"}
    delta = {
        ("q0", "a"): {"q0", "q1"},
        ("q1", "b"): {"q2"},
        ("q2", "a"): {"q2"},
        ("q2", "b"): {"q3"},
        ("q3", "a"): {"q3"}
    }

    fa = FiniteAutomata(Q, Sigma, delta, "q0", F)
    print("Is DFA:", fa.is_deterministic())

    if not fa.is_deterministic():
        print("\nConverting to DFA...")
        dfa = fa.convert_to_dfa()
        print("Is DFA:", dfa.is_deterministic())

    print("\nConverting to Regular Grammar:")
    rg = fa.convert_to_grammar()
    rg.print_grammar()
