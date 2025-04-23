class Grammar:
    def __init__(self, variables, terminals, start_symbol, productions):
        self.variables = set(variables)
        self.terminals = set(terminals)
        self.start_symbol = start_symbol
        self.productions = productions  # dict with variable as key, list of RHS tuples

    def to_cnf(self):
        self.remove_null_productions()
        self.remove_unit_productions()
        self.remove_useless_symbols()
        self.convert_to_cnf_format()

    def remove_null_productions(self):
        # Find nullable variables (those that produce epsilon)
        nullable = {var for var in self.variables if () in self.productions.get(var, [])}
        changed = True
        while changed:
            changed = False
            for var in self.variables:
                for rule in self.productions.get(var, []):
                    if all(sym in nullable for sym in rule) and var not in nullable:
                        nullable.add(var)
                        changed = True

        # Rebuild rules to exclude nullable symbols in all combinations
        new_productions = {}
        for var in self.variables:
            rules = self.productions.get(var, [])
            new_rules = set()
            for rule in rules:
                positions = [i for i, sym in enumerate(rule) if sym in nullable]
                for i in range(1 << len(positions)):
                    new_rule = list(rule)
                    for j, pos in enumerate(positions):
                        if (i >> j) & 1:
                            new_rule[pos] = None
                    filtered = tuple(sym for sym in new_rule if sym is not None)
                    if filtered:
                        new_rules.add(filtered)
            new_productions[var] = list(new_rules)
        self.productions = new_productions

    def remove_unit_productions(self):
        # Identify all unit productions (A → B)
        unit_pairs = {(var, rule[0]) for var in self.variables for rule in self.productions[var]
                      if len(rule) == 1 and rule[0] in self.variables}

        # Compute the transitive closure of unit pairs
        while True:
            new_pairs = unit_pairs.copy()
            for a, b in unit_pairs:
                for c, d in unit_pairs:
                    if b == c:
                        new_pairs.add((a, d))
            if new_pairs == unit_pairs:
                break
            unit_pairs = new_pairs

        # Remove unit productions from the original rules
        new_productions = {var: [] for var in self.variables}
        for var in self.variables:
            for rule in self.productions[var]:
                if not (len(rule) == 1 and rule[0] in self.variables):
                    new_productions[var].append(rule)

        # Add rules from unit-pair targets
        for a, b in unit_pairs:
            for rule in self.productions.get(b, []):
                if not (len(rule) == 1 and rule[0] in self.variables):
                    if rule not in new_productions[a]:
                        new_productions[a].append(rule)

        self.productions = new_productions

    def remove_useless_symbols(self):
        # Keep only generating symbols (those that can eventually produce terminals)
        generating = {var for var in self.variables if any(all(sym in self.terminals for sym in rule)
                                                           for rule in self.productions.get(var, []))}
        changed = True
        while changed:
            changed = False
            for var in self.variables:
                if var in generating:
                    continue
                for rule in self.productions.get(var, []):
                    if all(sym in generating or sym in self.terminals for sym in rule):
                        generating.add(var)
                        changed = True

        # Keep only reachable symbols (those accessible from the start symbol)
        reachable = set()
        queue = [self.start_symbol]
        while queue:
            current = queue.pop()
            reachable.add(current)
            for rule in self.productions.get(current, []):
                for sym in rule:
                    if sym in self.variables and sym not in reachable:
                        queue.append(sym)

        # Remove symbols that are not both generating and reachable
        self.variables = self.variables & generating & reachable
        self.productions = {
            var: [rule for rule in rules if all(sym in self.variables or sym in self.terminals for sym in rule)]
            for var, rules in self.productions.items() if var in self.variables
        }

    def convert_to_cnf_format(self):
        new_productions = {}
        new_vars = []
        term_map = {}

        for var in self.variables:
            new_productions[var] = []
            for rule in self.productions[var]:
                # case: A → a (already CNF compliant)
                if len(rule) == 1 and rule[0] in self.terminals:
                    new_productions[var].append(rule)
                else:
                    new_rule = []
                    # Replace terminals in longer rules with new variables (T_a → a)
                    for sym in rule:
                        if sym in self.terminals:
                            if sym not in term_map:
                                new_var = f"T_{sym.upper()}"
                                while new_var in self.variables or new_var in new_vars:
                                    new_var += "_"
                                term_map[sym] = new_var
                                new_vars.append(new_var)
                                new_productions[new_var] = [(sym,)]
                            new_rule.append(term_map[sym])
                        else:
                            new_rule.append(sym)

                    # Break down rules with >2 symbols using new variables
                    while len(new_rule) > 2:
                        new_var = f"X{len(new_vars)}"
                        new_vars.append(new_var)
                        new_productions[new_var] = [(new_rule[0], new_rule[1])]
                        new_rule = [new_var] + new_rule[2:]

                    # Final rule after all replacements and reductions
                    new_productions[var].append(tuple(new_rule))

        # Update the grammar with new variables and CNF-compliant rules
        self.variables.update(new_vars)
        self.productions = new_productions

    def print_grammar(self):
        print(f"Variables: {sorted(self.variables)}")
        print(f"Terminals: {sorted(self.terminals)}")
        print(f"Start Symbol: {self.start_symbol}")
        print("Productions:")
        for var, rules in self.productions.items():
            for rule in rules:
                print(f"  {var} → {' '.join(rule)}")
