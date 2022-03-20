# regex
Experimental implementation of regex;
construct NFA/DFA from regex.

### Example
Construct NFA/DFA for the regex `(a|b)*`
```python
import regex

a = regex.NFA.char('a') # construct NFA of regex 'a'
b = regex.NFA.char('b') # construct NFA of regex 'b'
union = a.union(b) # construct NFA of regex 'a|b'
closure = union.closure() # construct NFA of regex '(a|b)*' (kleene closure)

print(closure.to_graphviz()) 
```

**Output**:
```dot
Digraph G {
        node [shape=circle]
        rankdir = LR
        0 [shape=plaintext, label="start"]
        3 [shape=doublecircle]

        0 -> 6
        1 ->  2 [label = " ε"]
        2 ->  3 [label = " ε"]
        4 ->  5 [label = " ε"]
        6 ->  3 [label = " ε"]
        2 ->  4 [label = " ε"]
        7 ->  1 [label = " b"]
        6 ->  4 [label = " ε"]
        8 ->  2 [label = " ε"]
        4 ->  7 [label = " ε"]
        5 ->  8 [label = " a"]
}
```
**NFA**:

![1](https://user-images.githubusercontent.com/31496021/159165960-727eab00-30af-4758-b810-eb210a4434d3.svg)


```python
dfa = regex.subset_construction(nfa)
print(dfa.to_graphviz())
```
**Output**:

```dot
Digraph G {
        node [shape=circle]
        rankdir = LR
        0 [shape=plaintext, label="start"]
        3 [shape=doublecircle]
        2 [shape=doublecircle]
        1 [shape=doublecircle]

        0 -> 1
        1 ->  2 [label = " a"]
        3 ->  3 [label = " b"]
        3 ->  2 [label = " a"]
        2 ->  2 [label = " a"]
        2 ->  3 [label = " b"]
        1 ->  3 [label = " b"]
}
```


**DFA**:

![2](https://user-images.githubusercontent.com/31496021/159165974-eb2c6b49-96ed-4c7c-9a8d-0b6b3c0bfe01.svg)


```python
min_dfa = regex.dfa_minimize(dfa)
print(min_dfa.to_graphviz())
```

**Output**:
```dot
Digraph G {
        node [shape=circle]
        rankdir = LR
        0 [shape=plaintext, label="start"]
        1 [shape=doublecircle]

        0 -> 1
        1 ->  1 [label = " b"]
        1 ->  1 [label = " a"]
}
```

**Minimal DFA**:

![3](https://user-images.githubusercontent.com/31496021/159165979-437ca3fa-f83d-43e0-b8e3-49cd0692d87b.svg)


Utility function is provided to simplify the construction of NFA, escape ('\') and extensions ('[]^?') not supported, use carefully:
```python
# Build NFA from regex
nfa = regex.parse('(a|b)*')
```
