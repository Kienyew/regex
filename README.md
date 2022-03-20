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

        0 -> 7
        1 ->  2 [label = " ε"]
        2 ->  3 [label = " ε"]
        4 ->  2 [label = " ε"]
        5 ->  6 [label = " ε"]
        7 ->  5 [label = " ε"]
        8 ->  4 [label = " b"]
        2 ->  5 [label = " ε"]
        6 ->  1 [label = " a"]
        5 ->  8 [label = " ε"]
        7 ->  3 [label = " ε"]
}
```
**NFA**:

![1](https://user-images.githubusercontent.com/31496021/159161023-d9d68a5a-add8-44af-b901-5009879cd82d.svg)

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
        4 [shape=doublecircle]
        2 [shape=doublecircle]
        1 [shape=doublecircle]
        3 [shape=doublecircle]
        5 [shape=doublecircle]

        0 -> 1
        1 ->  2 [label = " a"]
        3 ->  4 [label = " ε"]
        1 ->  5 [label = " b"]
        6 ->  5 [label = " b"]
        2 ->  2 [label = " a"]
        4 ->  2 [label = " a"]
        4 ->  6 [label = " ε"]
        5 ->  5 [label = " b"]
        3 ->  2 [label = " a"]
        2 ->  5 [label = " b"]
        1 ->  4 [label = " ε"]
        4 ->  5 [label = " b"]
        2 ->  3 [label = " ε"]
        5 ->  2 [label = " a"]
        3 ->  5 [label = " b"]
        5 ->  3 [label = " ε"]
        6 ->  2 [label = " a"]
}
```


**DFA**:

![2](https://user-images.githubusercontent.com/31496021/159161126-5560afd8-2b89-4bde-a90d-9809c888497d.svg)


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
        2 [shape=doublecircle]

        0 -> 2
        1 ->  2 [label = " a"]
        2 ->  2 [label = " ε"]
        2 ->  2 [label = " b"]
        2 ->  2 [label = " a"]
        2 ->  1 [label = " ε"]
        1 ->  2 [label = " b"]
}
```

**Minimal DFA**:

![3](https://user-images.githubusercontent.com/31496021/159161193-0d3e4630-dddf-408d-8528-cb755238790c.svg)

Utility function is provided to simplify the construction of NFA, escape ('\') and extensions ('[]^?') not supported use carefully:
```python
nfa = regex.parse('(a|b)*')
```
