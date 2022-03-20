import regex

a = regex.NFA.char('a')  # construct NFA of regex 'a'
b = regex.NFA.char('b')  # construct NFA of regex 'b'
union = a.union(b)  # construct NFA of regex 'a|b'
closure = union.closure()  # construct NFA or regex '(a|b)*'

nfa = closure
print(nfa.to_graphviz())

dfa = regex.subset_construction(nfa)
print(dfa.to_graphviz())

min_dfa = regex.dfa_minimize(dfa)
print(min_dfa.to_graphviz())

print(regex.parse('(a|b)*').to_graphviz())

print(min_dfa.match(''))
print(min_dfa.match('a'))
print(min_dfa.match('b'))
print(min_dfa.match('ababababbababa'))
print(min_dfa.match('baabaablackship'))
