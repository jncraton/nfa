from string import ascii_lowercase as lower, digits

from IPython.display import display_html
import graphviz

class NFA:
  """
  Implements a nondeterministic finite automaton

  This can used for DFAs as well becuase a DFA is just a special case
  of an NFA.
  """
  
  def __init__(self, transitions, F=None, q0=None):
    """
    The DFA is constructed by a list of transitions of the form:
    
        [
          (initial state, symbols, next state),
          (initial state, symbols, next state),
          ...
        ]
      
    The 5 formal attributes of the DFA 5-tuple are built from this.
    
    An optional set of accept states may be provided. If omitted, the
    last state listed is assumed to be the one and only accept state.

    An optional start state can also be provided. If omitted, the start
    state is assumed to be the first state listed.

    >>> dfa = NFA([('q0','b','q0'),('q0','a','q1')])
    >>> dfa.accept('a')
    True
    >>> dfa.accept('bba')
    True
    >>> dfa.accept('b')
    False
    """

    self.transitions = [(i[0], char, i[2]) for i in set(transitions) for char in i[1]]

    # Start state q0
    self.q0 = q0 or transitions[0][0]
    
    # Accept states F
    self.F = F or set([transitions[-1][2]])

  def Σ(self):
    """
    Returns the symbol alphabet Σ
    """
    return set(sum([[c for c in i[1] if c != 'ε'] for i in self.transitions], []))

  def δ(self, current, input=None):
    """
    Transition function relating state and symbol to another state 

    δ: Q × Σ → P(Q)

    Returns a set of next states for a given current state and input

    We store the set of all transitions, and implement a method δ
    to return the set of next states

    Epsilon transitions are returned only if explicitly requested by
    calling without input.
    """

    if input:
      return sorted([i[2] for i in self.transitions if i[0] == current and i[1] == input])
    else:
      return sorted([i[2] for i in self.transitions if i[0] == current and i[1] == 'ε'])

  def Q(self):
    """
    Returns the set of states Q
    """
    return set([i[0] for i in self.transitions] + [i[2] for i in self.transitions])

  def accept(self, input, state=None):
    """
    Recursively check input for acceptance one symbol at a time
  
    Returns True when halted at a state in F, and False otherwise
    """

    # Begin at the start state if we aren't called with a state
    state = state or self.q0

    # Handle epsilon case
    for n in self.δ(state,input=None):
      a = self.accept(input, n)
      if a:
        return True

    # Return our acceptance status when we're out of input
    if len(input) == 0:
      return state in self.F

    # Get the next state or return our acceptance status if we're stuck
    try:
      next = self.δ(state,input[0])
    except KeyError:
      return state in self.F
  
    # Recurse using all possible next states and the rest of our input
    #
    # It's worth noting that the search walk for an NFA takes exponential
    # time, while the conversion to DFA would include an exponential
    # number of states. It's a time/memory tradeoff.
    for n in next:
      a = self.accept(input[1:], n)
      # We accept if any path results in acceptance
      if a:
        return True

    return False

  def rename(self):
    """ 
    Shortens state names 

    Some of the other methods concatenate state names for easy debugging,
    and it can be helpful to shorten them back down.

    >>> n = NFA([('big','a','names')])
    >>> n.rename()
    >>> n.transitions
    [('0', 'a', '1')]
    """

    ids = {s: str(i) for (i, s) in enumerate(sorted(list(self.Q())))}

    self.transitions = [(ids[t[0]], t[1], ids[t[2]]) for t in self.transitions]
    self.F = [ids[f] for f in self.F]
    self.q0 = ids[self.q0]
    
  def to_xml(self):
    """
    Converts the DFA to xml as used by JFLAP.
    
    I do not expect any bonus points for the readability of this method.
    
    >>> ev = NFA.email_validator()
    >>> len(ev.to_xml())
    19339
    """
    ids = {s: i for (i, s) in enumerate(self.Q())}

    return '\n'.join(
      ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '<structure><type>fa</type><automaton>'] +
      [
        '<state id="%d" name="%s"><x>0</x><y>0</y>%s</state>' %
        ( ids[name], name, '<initial/>' if name == self.q0 else '<final/>' if name in self.F else '' ) 
        for name in self.Q()
      ] + [
        '<transition><from>%d</from><to>%d</to><read>%s</read></transition>' % 
        ( ids[t[0]], ids[t[2]], t[1] ) 
        for t in self.transitions
      ] + 
      ['</automaton></structure>']
    )

  def to_graphviz(self):
    """ Converts to a graphviz object for graphical display """

    # http://ethanschoonover.com/solarized
    BASE01 = '#586e75'
    ORANGE = '#cb4b16'
    VIOLET = '#6c71c4'
    BGCOLOR = '#f5f5f5'

    g = graphviz.Digraph(format='png', engine='dot', graph_attr={'rankdir': 'LR', 'packmode':'graph', 'bgcolor': BGCOLOR, 'overlap': 'scale', 'concentrate': 'true', 'splines':'true'})
    
    for state in self.Q():
      g.attr('node', shape='doublecircle' if state in self.F else 'circle')
      g.attr('node', style='bold')
      g.attr('node', color=VIOLET if state in self.F else ORANGE)
      g.attr('node', fontcolor=BASE01)
      g.node(state)
      
    for e in self.transitions:
      g.attr('edge', color=BASE01)
      g.attr('edge', fontcolor=BASE01)
      g.edge(e[0], e[2], e[1])
    
    # Add arrow to start state
    g.attr('node', shape='none')
    g.node("")
    g.edge("", self.q0)

    return g

  def show(self):
    display_html('<pre>' + self.to_graphviz()._repr_svg_() + '</pre>', raw=True)

  def test(self, accept, reject):
    """
    Tests the DFA against a list of strings expected to be accepted 
    and a list expected to be rejected.

    Returns nothing, but raises an AssertionError on failure.

    >>> dfa = NFA([('q0','a','q0'),('q0','b','q1'),('q1','ab','q1')])
    >>> dfa.test(accept=['b','ba','ab'],reject=['a','aaa'])
    """
    
    for a in accept:
      assert self.accept(a), "Failed to accept %s for %s" % (a, sorted(list(self.transitions)))

    for r in reject:
      assert self.accept(r) == False, "Failed to reject %s for %s" % (r, sorted(list(self.transitions)))

  def to_dfa(self):
    """
    Convert NFA to DFA in place

    >>> a = NFA([('0a','a','1a'),('0a','ba','0a'),('1a','ab','1a')])
    >>> a.test(['aba','a'],['b','bbb'])
    >>> a.to_dfa()
    >>> a.test(['aba','a'],['b','bbb'])
    """
    self.ε_elimination()

    self.transitions = set(self.transitions)

    for q in self.Q():
      for i in self.Σ():
        if len(self.δ(q,i)) > 1:
          states = self.δ(q,i)
          state = "{%s}" % ','.join(states)

          # Add transitions pointing from substates
          self.transitions.update(set([(state if t[0] in states else t[0],t[1],t[2]) for t in self.transitions]))

          # Move transition targets to new state
          self.transitions = set([(t[0],t[1],state if t[0] == q and t[1] == i else t[2]) for t in self.transitions])

          # Adjust recursive transitions
          self.transitions = set([(t[0],t[1],state if t[2] in states and t[0] == state else t[2]) for t in self.transitions])

          # Copy accept state
          for s in states:
            if s in self.F:
              self.F.add(state)

          return self.to_dfa()

  def ε_elimination(self):
    """
    Removes any ε (empty string) transitions from the NFA

    ε doesn't increase the power of an NFA, but can be a useful
    conveinience.

    Removing ε transitions involves merging states that are connected
    via ε transitions and properly handling the transitions from the
    old states.

    >>> n = NFA([(0,'a',1),(0,'ba',0),(1,'ab',1),(0,'ε',1),(1,'b',2)])
    >>> d = NFA.ε_elimination(n)
    >>> len(n.transitions)
    3
    >>> n.test(['b','aaab','ababababb'], ['a','ababababa','aaaaa'])
    """

    while True:
      εtransitions = [t for t in self.transitions if t[1] == 'ε']

      if len(εtransitions) == 0:
        return

      for t in εtransitions:
        us = t[0]
        them = t[2]
            
        # Remove the ε transition
        self.transitions.remove(t)
          
        # Move their transitions to ourself
        self.transitions = set([(us if t[0] == them else t[0],t[1],t[2]) for t in self.transitions])
        self.transitions = set([(t[0],t[1],us if t[2] == them else t[2]) for t in self.transitions])
  
        # Inherit their other properties
        self.q0 = us if self.q0 == them else self.q0
        self.F = set(self.F)
        if them in self.F:
          self.F.remove(them)
          self.F.add(us)
  
        break

  @classmethod
  def intersection(cls, a, b):
    """
    Merges two FAs and return their intersection

    In essense, this means both FAs must reach their accept state.
    
    >>> a = NFA([('0a','a','1a'),('0a','b','0a'),('1a','ab','1a')])
    >>> b = NFA([('0b','b','1b'),('0b','a','0b'),('1b','ab','1b')])
    >>> u = NFA.intersection(a, b)
    >>> u.test(accept=['bba','ba','ab'],reject=['aa','bb','a','b'])
    """
    transitions = []

    for at in a.transitions:
      for bq in b.Q():
        transitions.append(("{%s,%s}" % (at[0], bq), at[1], "{%s,%s}" % (at[2], bq)))

    for bt in b.transitions:
      for aq in a.Q():
        transitions.append(("{%s,%s}" % (aq, bt[0]), bt[1], "{%s,%s}" % (aq, bt[2])))

    F = set(["{%s,%s}" % (af, bf) for af in a.F for bf in b.F])
    
    u = cls(transitions, F, "{%s,%s}" % (a.q0, b.q0))

    # Prune reflexive transitions that add no information
    u.transitions = [t for t in u.transitions 
      if t[0] != t[2] or # Non-reflexive transitions
      len(u.δ(t[0], t[1])) == 1
    ]

    return u

  @classmethod
  def union(cls, a, b):
    """
    Merges two FAs and return their union

    This means that either FA must reach its accept state
    
    >>> a = NFA([('0a','a','1a'),('0a','b','0a'),('1a','ab','1a')])
    >>> b = NFA([('0b','b','1b'),('0b','a','0b'),('1b','ab','1b')])
    >>> u = NFA.union(a, b)
    >>> u.test(accept=['a','b'],reject=[''])
    """

    # Start with ε transitions to start states
    transitions = [
      ('0','ε','a'+a.q0),
      ('0','ε','b'+b.q0),
    ]

    # Add all transitions
    transitions += [('a'+t[0],t[1],'a'+t[2]) for t in a.transitions]
    transitions += [('b'+t[0],t[1],'b'+t[2]) for t in b.transitions]

    F =  ['a'+f for f in a.F]
    F += ['b'+f for f in b.F]

    return cls(transitions, F, q0='0')

  @classmethod
  def concat(cls, a, b):
    """
    Merges two FAs and return their concatenation
    
    >>> a = NFA([('0a','a','1a')])
    >>> b = NFA([('0b','b','1b')])
    >>> c = NFA.concat(a, b)
    >>> c.test(accept=['ab'],reject=['a','b'])
    >>> a = NFA([('0a','a','1a'),('1a','a','2a')])
    >>> b = NFA([('0b','b','1b')])
    >>> c = NFA.concat(a, b)
    >>> c.test(accept=['aab'],reject=['a','b'])
    >>> a = NFA([('0a','a','1a'),('0a','b','1b')],F=['1a','1b'])
    >>> b = NFA([('0c','c','1c')])
    >>> c = NFA.concat(a, b)
    >>> c.test(accept=['ac','bc'],reject=['a','b','cc'])
    """
    transitions = []

    transitions += [('a'+t[0], t[1], 'a'+t[2]) for t in a.transitions]
    F = []

    # Every accept state in a becomes a copy of b
    for f in a.F:
      f = 'a' + f
      transitions += [(f+'b'+t[0] if t[0] != b.q0 else f, t[1], f+'b'+t[2] if t[2] != b.q0 else f) for t in b.transitions]

      # Accept states are accept states of b
      F += [f+'b'+s for s in b.F]

    return cls(transitions, F=F, q0='a'+a.q0)

  @classmethod
  def kleene(cls, nfa):
    """
    Returns `nfa` wrapped in a Kleene star construction

    The new NFA will accept any number of copies of the language that 
    the original nfa accepts, including zero.
    
    >>> n = NFA.kleene(NFA([('0','a','1')]))
    >>> n.test(['a','aa','aaa',''],['b'])
    >>> n = NFA.kleene(NFA([('0','a','1'),('1','b','2')]))
    >>> n.test(['ab','abab','abab',''],['b','a','aaba'])
    """
    return cls([
          ('kq0','ε',nfa.q0),
        ('kq0','ε','kf'),
      ] + nfa.transitions +
        [(f, 'ε', nfa.q0) for f in nfa.F] +
        [(f, 'ε', 'kf') for f in nfa.F]
      )

  @classmethod
  def from_re(cls, re):
    """
    Builds an NFA instance from a regular expression

    Regular expressions are of the form recognized by JFLAP.

    Some examples:

    a+b+c = {a, b, c}
    abc = {abc}
    (!+a)bc = {bc, abc}
    ab* = {a, ab, abb, abbb, ...}
    (ab)* = (λ, ab, abab, ababab, ...)
    (a+b)* = (λ, a, b, aa, ab, ba, bb, aaa, ...)
    a+b* = (a, λ, b, bb, bbb, ...)
    a+!* = (a, λ)
    (a+!)* = (λ, a, aa, aaa, aaaa, ...)

    While regular expressions represent a regular language, they are 
    themselves context-free, so they can't be processed using an NFA.

    The RE is conceptualized as a string with the following grammar:

    S → ExpOp
    Exp → a
    Exp → Open a Close
    Open → (
    Close → )
    Op → o

    Where a is a printable character not in o and o is one of:

    - '*' is the Kleene star
    - '+' is the union operator
    - '!' is used to represent the empty string
    - The empty string representing concatination

    '(' and ')' are literal parenthesis.

    The basic algorithm used to convert the RE to an NFA is Thompson's
    construction.

    The RE is an LL(1) grammar, so parsing is very straightforward and
    only requires looking ahead 1 byte at a time.
    
    >>> NFA.from_re('').test([''],['a'])
    >>> NFA.from_re('a').test(['a'],['','aa'])
    >>> NFA.from_re('ab').test(['ab'],['','abc','a'])
    >>> NFA.from_re('a+b').test(['a', 'b'],['','abc', 'ab'])
    >>> NFA.from_re('(a)b').test(['ab'],['','a', 'b'])
    >>> NFA.from_re('(a)(b)').test(['ab'],['','a', 'b'])
    >>> NFA.from_re('(a+b)c').test(['ac','bc'],['','a', 'b','aa'])
    >>> NFA.from_re('(!+a)bc').test(['bc','abc'],['','a','aa','bbc'])
    >>> NFA.from_re('a(b+c)d').test(['abd','acd'],['','a', 'b','abc'])
    >>> NFA.from_re('a*').test(['','a','aaaaa'],['b'])
    >>> NFA.from_re('a*b').test(['b','ab','aaaab'],['aaa','a'])
    >>> NFA.from_re('(ab)*').test(['','ab','ababab'],['b','aab','aba'])
    """
    
    def concat_re(re, nfa=cls([('0','ε','1')], F=[])):
      """ 
      Concatentates an RE to an NFA
      """
      if len(re) == 0 or re[0] == ')':
        return nfa

      if len(re) == 1:
        return cls([('0',re[0],'1')])

      # Consume the left hand side element. This may be a single char or an
      # expression wrapped in parens. It should not be an operator.
      if re[0] == '(':
        open = 0
        i = 0
        while True:
          if re[i] == '(':
            open += 1
          if re[i] == ')':
            open -= 1
          i += 1
          if open == 0 or i > len(re):  
            break
        lhs = NFA.concat(nfa, cls.from_re(re[1:i-1]))
        re = re[i-1:]
      else:
        lhs = cls.from_re(re[0] if re[0] != '!' else 'ε')

      # Perform the requested operation on the operator and concatenate
      # the result to the NFA that we've been building
      if len(re) > 1 and re[1] == '*':
        return cls.concat(NFA.concat(nfa, cls.kleene(lhs)), cls.from_re(re[2:]))
      elif len(re) > 1 and re[1] == '+':
        return NFA.concat(nfa, NFA.union(lhs, cls.from_re(re[2:])))
      else:
        return NFA.concat(nfa, NFA.concat(lhs, cls.from_re(re[1:])))

    n = concat_re(re)
    n.rename()
    return n

  @classmethod
  def email_validator(cls):
    """
    Builds a DFA instance that operates as a simple email address validator.
    
    >>> ev = NFA.email_validator()
    >>> ev.test(['abc@dsu.edu','abc@pluto.dsu.edu','11@123.com'],
    ...         ['a.b.ab','ab@ab','ab@ab.abcd'])
    """
    
    return cls([
      ('start', lower+digits, 'username'),
      ('username', lower+digits, 'username'),
      ('username', '@', '@'),
      ('@', lower+digits, 'domain'),
      ('domain', lower+digits, 'domain'),
      ('domain', '.', 'tld length 0'),
      ('tld length 0', lower+digits, 'tld length 1'),
      ('tld length 1', lower+digits, 'tld length 2'),
      ('tld length 1', '.', 'tld length 0'),
      ('tld length 2', lower+digits, 'tld length 3'),
      ('tld length 2', '.', 'tld length 0'),
      ('tld length 3', lower+digits, 'domain'),
      ('tld length 3', '.', 'tld length 0'),
    ], ['tld length 2', 'tld length 3'])

DFA = NFA