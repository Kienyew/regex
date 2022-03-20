from typing import Set, Tuple, Iterator
from collections import defaultdict
import pprint
import itertools


epsilon = 'ε'


class State:
    pass


class StateSet:
    def __init__(self, inner=[]):
        self.states: Set[State] = set(inner)

    def add(self, state: State):
        self.states.add(state)

    def __iter__(self) -> Iterator[State]:
        yield from self.states

    def __contains__(self, x: State) -> bool:
        return x in self.states

    def __hash__(self) -> int:
        value = 0
        for state in self.states:
            # hopefully xor is commutative
            value ^= hash(state)

        return value

    def __len__(self) -> int:
        return len(self.states)

    def __eq__(self, other: 'StateSet') -> int:
        return len(self.states) == len(other.states) \
            and all(s in other.states for s in self.states)

    def __sub__(self, other: 'StateSet') -> 'StateSet':
        return StateSet(self.states - other.states)


class FA:
    # base class for NFA and DFA
    def transition_from(self, s):
        return self._transition_from[s]

    def add_transition(self, left: State, char: str, right: State):
        self.transitions.add((left, char, right))

    def states(self) -> StateSet:
        # compute all the states involved in this FA
        S = StateSet()
        for a, _, b in self.transitions:
            S.add(a)
            S.add(b)

        return S

    def chars(self) -> Set[str]:
        # compute Σ*
        return {c for _, c, _ in self.transitions}


class NFA(FA):
    # define a Nondeterministic Finite Automata
    def __init__(self, start: State, accept: State):
        self.start: State = start
        self.accept: State = accept  # NFA has only one accepting state

        # {(left, c, right)...} such that δ(left, c) = right
        self.transitions: Set[Tuple[State, str, State]] = set()
        self._transition_from = defaultdict(lambda: defaultdict(StateSet))

    def add_transition(self, left: State, char: str, right: State):
        self.transitions.add((left, char, right))

    def compute_transition(self):
        for left, c, right in self.transitions:
            self._transition_from[left][c].add(right)

    def to_graphviz(self) -> str:
        counter = 0

        def next_name():
            nonlocal counter
            counter += 1
            return counter

        names = defaultdict(next_name)
        counter = 0
        transitions = []
        for left, c, right in self.transitions:
            transitions.append(
                f'\t{names[left]} ->  {names[right]} [label = " {c}"]')

        ts = '\n'.join(transitions)

        accepts = f'\t{names[self.accept]} [shape=doublecircle]\n'

        return f"""
Digraph G {{
\tnode [shape=circle]
\trankdir = LR
\t0 [shape=plaintext, label="start"]
{accepts}
\t0 -> {names[self.start]}
{ts}
}}
"""

    def char(x) -> 'NFA':
        s0 = State()
        s1 = State()
        nfa = NFA(s0, {s1})
        nfa.add_transition(s0, x, s1)
        nfa.accept = s1

        return nfa

    def union(self, b: 'NFA') -> 'NFA':
        # build an NFA representation of a | b
        if self.start is None:
            raise ValueError('badly constructed NFA')

        s0, s1 = State(), State()
        nfa = NFA(s0, s1)
        nfa.transitions |= self.transitions
        nfa.transitions |= b.transitions
        nfa.add_transition(s0, epsilon, self.start)
        nfa.add_transition(s0, epsilon, b.start)
        nfa.add_transition(self.accept, epsilon, s1)
        nfa.add_transition(b.accept, epsilon, s1)
        return nfa

    def join(self, b: 'NFA') -> 'NFA':
        # build an NFA representation of a b
        if self.start is None:
            return b

        nfa = NFA(self.start, b.accept)
        nfa.transitions |= self.transitions
        nfa.transitions |= b.transitions
        nfa.add_transition(self.accept, epsilon, b.start)
        return nfa

    def closure(self) -> 'NFA':
        # build and NFA representation of a*
        if self.start is None:
            raise ValueError('badly constructed NFA')

        s0, s1 = State(), State()
        nfa = NFA(s0, s1)
        nfa.transitions |= self.transitions
        nfa.add_transition(s0, epsilon, self.start)
        nfa.add_transition(s0, epsilon, s1)
        nfa.add_transition(self.accept, epsilon, self.start)
        nfa.add_transition(self.accept, epsilon, s1)
        return nfa

    def __repr__(self):
        return f'NFA(start={self.start}, {pprint.pformat(self.transitions)},\naccept={self.accept})'


class DFA(FA):
    # define a Deterministic Finite Automata
    def __init__(self, start: State, accepts: StateSet):
        self.start: State = start
        self.accepts = accepts
        self.transitions: Set[Tuple[State, str, State]] = set()
        self._transition_from = defaultdict(dict)

    def add_transition(self, left: State, char: str, right: State):
        self.transitions.add((left, char, right))

    def compute_transition(self):
        for left, c, right in self.transitions:
            self._transition_from[left][c] = right

    def to_graphviz(self) -> str:
        counter = 0

        def next_name():
            nonlocal counter
            counter += 1
            return counter

        names = defaultdict(next_name)
        transitions = []
        for left, c, right in self.transitions:
            transitions.append(
                f'\t{names[left]} ->  {names[right]} [label = " {c}"]')
        ts = '\n'.join(transitions)

        accepts = ''
        for a in self.accepts:
            accepts += '\t' + f'{names[a]} [shape=doublecircle]' + '\n'

        return f"""
Digraph G {{
\tnode [shape=circle]
\trankdir = LR
\t0 [shape=plaintext, label="start"]
{accepts}
\t0 -> {names[self.start]}
{ts}
}}
"""

    def __repr__(self):
        return f'DFA(start={self.start}, {pprint.pformat(self.transitions)},\naccept={self.accepts})'


def epsilon_closure(nfa: NFA, states: StateSet) -> StateSet:
    # compute the epsilon closure of `states` in `nfa`
    def one_closure(s) -> StateSet:
        # epsilon closure of one state
        closure = [s]
        Q = [s]
        while len(Q) != 0:
            q = Q.pop()
            for right in nfa.transition_from(q)[epsilon]:
                if right not in closure:
                    Q.append(right)
                    closure.append(right)

        return closure

    S = StateSet()
    for state in itertools.chain(*map(one_closure, states)):
        S.add(state)

    return S


def delta(nfa: NFA, q: StateSet, c: str) -> StateSet:
    # compute all states that can be reached by states in `q` through character `c`
    rights = StateSet()
    for left, x, right in nfa.transitions:
        if x == c and left in q:
            rights.add(right)

    return rights


def subset_construction(nfa: NFA) -> DFA:
    # compute dfa from nfa via subset construction
    nfa.compute_transition()
    q0 = epsilon_closure(nfa, StateSet([nfa.start]))
    Q = [q0]
    worklist = [q0]
    T = []
    chars = nfa.chars()
    while len(worklist) > 0:
        q = worklist.pop()
        for c in chars:
            t = epsilon_closure(nfa, delta(nfa, q, c))
            if len(t) == 0:
                continue

            T.append((q, c, t))
            if t not in Q:
                Q.append(t)
                worklist.append(t)

    Q2D = defaultdict(State)
    accepts = StateSet({Q2D[q] for q in Q if nfa.accept in q})
    print(q0.states)
    dfa = DFA(Q2D[q0], accepts)
    for q, c, t in T:
        dfa.add_transition(Q2D[q], c, Q2D[t])

    return dfa


def dfa_minimize(dfa: DFA) -> DFA:
    # minimize a dfa via Hopcroft's algorithm
    dfa.compute_transition()
    P = [dfa.accepts, dfa.states() - dfa.accepts]
    P = list(filter(lambda p: len(p) != 0, P))  # remove empty set
    N = len(dfa.states())

    def same_partition(a: State, b: State) -> bool:
        # is states `a` and `b` in the same partition?
        for p in P:
            if a in p and b in p:
                return True
        return False

    def split(S: StateSet):
        S = list(S)
        key = S.pop()
        L, R = {key}, set()
        chars = dfa.chars()
        while S:
            for c in chars:
                if c not in dfa.transition_from(S[-1]) and c not in dfa.transition_from(key):
                    # skip this character as both states have no transition on this character
                    to_split = False
                elif c in dfa.transition_from(S[-1]) and c in dfa.transition_from(key):
                    to_split = not same_partition(dfa.transition_from(
                        S[-1])[c], dfa.transition_from(key)[c])
                else:
                    # one of the state has transition from `c`, but another doesn't
                    to_split = True

                if to_split:
                    R.add(S.pop())
                    break
            else:
                L.add(S.pop())

        if len(R) == 0:
            # nothing to split
            return False, False
        else:
            return L, R

    while True:
        for i in range(N):
            p = P[-1]
            s1, s2 = split(p)
            P.pop()
            if (s1, s2) == (False, False):
                P.append(p)
            else:
                P.append(s1)
                P.append(s2)
                break
        else:
            break

    start = None
    accepts = StateSet()
    D = StateSet([State() for _ in range(len(P))])
    for p, d in zip(P, D):
        if dfa.start in p:
            start = d

        if next(s for s in p) in dfa.accepts:
            accepts.add(d)

    new_dfa = DFA(start, set(accepts))
    for left, c, right in dfa.transitions:
        for p, d in zip(P, D):
            if left in p:
                new_left = d
            if right in p:
                new_right = d

        new_dfa.add_transition(new_left, c, new_right)
    return new_dfa


def parse(regex: str) -> NFA:
    # Generate an NFA from regular expression.
    # No extenstion supported (eg. [] ? [^.] .), also, no escape '\' supported.
    # Use 'ε' character if want to represent empty character transition.

    # expr -> term '|' expr
    # expr -> term
    # term -> factor term
    # term -> factor
    # term -> factor *
    # factor -> chars
    # factor -> ( expr )
    # chars -> any valid characters

    i = 0

    def advance(k):
        nonlocal i
        i += k

    def top():
        return regex[i]

    def eof():
        return i >= len(regex)

    def expr():
        s, nfa = term()
        if eof():
            return s, nfa

        elif top() == '|':
            s += '|'
            advance(1)
            ss, nnfa = expr()
            s += ss
            nfa = nfa.union(nnfa)

        return s, nfa

    def term():
        s, nfa = factor()
        if eof():
            return s, nfa

        if top() == '*':
            s += '*'
            nfa = nfa.closure()
            advance(1)

        if eof():
            return s, nfa

        if top() not in '|)':
            ss, nnfa = term()
            s += ss
            nfa = nfa.join(nnfa)

        return s, nfa

    def factor():
        s = ''
        if top() == '(':
            s += top()
            advance(1)
            ss, nfa = expr()
            s += ss
            advance(1)  # expect ')'
            s += ')'
        else:
            ss, nfa = chars()
            s += ss

        return s, nfa

    def chars():
        nfa = NFA(None, {})
        s = ''
        while not eof() and top() not in '()|*':
            s += top()
            nfa = nfa.join(NFA.char(top()))
            advance(1)

        return s, nfa

    s, nfa = expr()
    return nfa
