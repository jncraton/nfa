from string import ascii_lowercase as lower, digits
from collections import ChainMap
import graphviz

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
    """
    self.transitions = transitions

    # Set of states Q
    self.Q = set([i[0] for i in transitions] + [i[2] for i in transitions])

    # Symbol alphabet Σ
    self.Σ = set(sum([[c for c in i[1]] for i in transitions], []))

    # Transition function relating state and symbol to another state 
    # δ: Q × Σ → Q
    self.δ = dict(ChainMap(*[{(i[0], char): i[2] for char in i[1]} for i in transitions]))

    # Start state q0
    self.q0 = transitions[0][0]
    
    # Accept states F
    self.F = accept or transitions[-1][2]


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
      next = self.δ[(state,input[0])]
    except KeyError:
      return state in self.F
  
    # Recurse using our next state and the rest of our input
    return self.accept(input[1:], next)
    
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
        ( ids[t[0][0]], ids[t[1]], t[0][1] ) 
        for t in self.δ.items()
      ] + 
      ['</automaton></structure>']
    )

  def to_png(self, filename):
    g = graphviz.Digraph(format='png')
    
    for state in self.Q:
      g.attr('node', shape='doublecircle' if state in self.F else 'circle')
      g.node(state)
      
    for e in self.transitions:
      g.edge(e[0], e[2], e[1])
    
    # Add arrow to start state
    g.attr('node', shape='none')
    g.node("")
    g.edge("", self.q0)
    
    g.render(filename)

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
    
if __name__ == '__main__':
  ev = DFA.email_validator()
  with open('ev.jff','w') as jff:
    jff.write(ev.to_xml())
  
  ev.to_png('ev')