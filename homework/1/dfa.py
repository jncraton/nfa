from string import ascii_lowercase as lower, digits
from collections import ChainMap
import graphviz
import random

from IPython.display import display_html

# http://ethanschoonover.com/solarized
BASE01 = '#586e75'
BASE00 = '#657b83'
BASE0 = '#839496'
BASE3 = '#fdf6e3'
BASE3 = '#f5f5f5'

YELLOW = '#b58900'
ORANGE = '#cb4b16'
VIOLET = '#6c71c4'
RED = '#dc323f'
BLUE = '#268bd2'
MAGENTA = '#d33682'
CYAN = '#2aa198'
GREEN = '#859900'

ACCENTS = [YELLOW, ORANGE, VIOLET, RED, BLUE, MAGENTA, CYAN, GREEN]

class DFA:
  """
  Implements a Deterministic Finite Automaton
  """
  
  def __init__(self, transitions, accept=None):
    """
    The DFA is constructed by a list of transitions of the form
            [
                (initial state, symbols, next state),
                (initial state, symbols, next state),
                ...
            ]
      
    The 5 formal attributes of the DFA 5-tuple are built from this.
    
    An optional set of accept states may be provided. If omitted, the
    last state listed is assumed to be the one and only accept state.

    >>> dfa = DFA([('q0','b','q0'),('q0','a','q1')])
    >>> dfa.accept('a')
    True
    >>> dfa.accept('bba')
    True
    >>> dfa.accept('b')
    False
    """

    # Set of states Q
    self.Q = set([i[0] for i in transitions] + [i[2] for i in transitions])

    # Symbol alphabet Σ
    self.Σ = set(sum([[c for c in i[1]] for i in transitions], []))

    # Transition function relating state and symbol to another state 
    # δ: Q × Σ → P(Q)
    # This could just use a dict for DFAs, but that doesn't work for NFAs
    # We store the set of all transitions, and implement a method δ
    # to return the set of next states
    self.transitions = [(i[0], char, i[2]) for i in transitions for char in i[1]]

    # Start state q0
    self.q0 = transitions[0][0]
    
    # Accept states F
    self.F = accept or (transitions[-1][2],)

  def δ(self, current, input):
    """
    Transition functions δ

    Returns a set of next states for a given current state and input
    """

    return [i[2] for i in self.transitions if i[0] == current and i[1] == input]

  def accept(self, input, state=None):
    """
    Recursively check input for acceptance one symbol at a time
  
    Returns True when halted at a state in F, and False otherwise
    """

    # Begin at the start state if we aren't called with a state
    state = state or self.q0

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
    # It's worth noting that the search walk for an NFA take exponential
    # time, while the conversion to DFA would include an exponential
    # number of states. It's a time/memory tradeoff.
    for n in next:
      a = self.accept(input[1:], n)
      # We accept if any path results in acceptance
      if a:
        return True

    return False
    
  def to_xml(self):
    """
    Converts the DFA to xml as used by JFLAP.
    
    I do not expect any bonus points for the readability of this method.
    
    >>> ev = DFA.email_validator()
    >>> len(ev.to_xml())
    19339
    """
    ids = {s: i for (i, s) in enumerate(self.Q)}

    return '\n'.join(
      ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '<structure><type>fa</type><automaton>'] +
      [
        '<state id="%d" name="%s"><x>0</x><y>0</y>%s</state>' %
        ( ids[name], name, '<initial/>' if name == self.q0 else '<final/>' if name in self.F else '' ) 
        for name in self.Q
      ] + [
        '<transition><from>%d</from><to>%d</to><read>%s</read></transition>' % 
        ( ids[t[0]], ids[t[2]], t[1] ) 
        for t in self.transitions
      ] + 
      ['</automaton></structure>']
    )

  def to_graphviz(self):
    g = graphviz.Digraph(format='png', engine='dot', graph_attr={'rankdir': 'LR', 'packmode':'graph', 'bgcolor': BASE3, 'overlap': 'scale', 'concentrate': 'true', 'splines':'true'})
    
    for state in self.Q:
      g.attr('node', shape='doublecircle' if state in self.F else 'circle')
      g.attr('node', style='bold')
      g.attr('node', color=VIOLET if state in self.F else ORANGE)
      g.attr('node', fontcolor=BASE01)
      g.node(state)
      
    for e in self.transitions:
      g.attr('edge', style='bold')
      g.attr('edge', color=GREEN)
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

    >>> dfa = DFA([('q0','a','q0'),('q0','b','q1'),('q1','ab','q1')])
    >>> dfa.test(accept=['b','ba','ab'],reject=['a','aaa'])
    """
    
    for a in accept:
      assert(self.accept(a))

    for r in reject:
      assert(self.accept(r) == False)

  def union(self, b):
    """
    Merges another DFA as a union to this one
    
    >>> a = DFA([('q0','a','q0'),('q0','b','q1')])
    >>> b = DFA([('q0','b','q0'),('q0','a','q1')])
    >>> a.union(b)
    >>> a.test(accept=['bba','ba','ab'],reject=['aa','bb','a','b'])
    """
    transitions = []

    for t in self.transitions:
      for bq in b.Q:
        transitions.append(("%s-%s" % (t[0], bq), t[1], "%s-%s" % (t[2], bq)))

    for bt in b.transitions:
      for q in b.Q:
        transitions.append(("%s-%s" % (q, bt[0]), bt[1], "%s-%s" % (q, bt[2])))

    self.transitions = set(transitions)

    self.F = set(['%s-%s' % (af, bf) for af in self.F for bf in b.F])
    self.Q = set(['%s-%s' % (aq, bq) for aq in self.Q for bq in b.Q])
    self.q0 = '%s-%s' % (self.q0, b.q0)

  @classmethod
  def email_validator(cls):
    """
    Builds a DFA instance that operates as a simple email address validator.
    
    >>> ev = DFA.email_validator()
    >>> ev.accept('abc@dsu.edu')
    True
    >>> ev.accept('abc@pluto.dsu.edu')
    True
    >>> ev.accept('11@123.com')
    True
    >>> ev.accept('a.b.ab')
    False
    >>> ev.accept('ab@ab')
    False
    >>> ev.accept('ab@ab.abcd')
    False
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

