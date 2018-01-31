from string import ascii_lowercase, digits
from collections import ChainMap

# This is a relatively human-readable defintion of the DFA as
# (initial state, characters to match, next state)
# This will be used to build the formal definition
dfa = [
  ('start', ascii_lowercase+digits, 'username'),
  ('username', ascii_lowercase+digits, 'username'),
  ('username', '@', '@'),
  ('@', ascii_lowercase+digits, 'domain'),
  ('domain', ascii_lowercase+digits, 'domain'),
  ('domain', '.', 'tld length 0'),
  ('tld length 0', ascii_lowercase+digits, 'tld length 1'),
  ('tld length 1', ascii_lowercase+digits, 'tld length 2'),
  ('tld length 1', '.', 'tld length 0'),
  ('tld length 2', ascii_lowercase+digits, 'tld length 3'),
  ('tld length 2', '.', 'tld length 0'),
  ('tld length 3', ascii_lowercase+digits, 'domain'),
  ('tld length 3', '.', 'tld length 0'),
]

Q = set([i[0] for i in dfa] + [i[2] for i in dfa])
Σ = set(sum([[c for c in i[1]] for i in dfa], []))
δ = dict(ChainMap(*[{(i[0], char): i[2] for char in i[1]} for i in dfa]))
q0 = dfa[0][0]
F = ['tld length 2', 'tld length 3']

def check_input(input, state=q0):
  """
  Recursively check input one character at a time

  Returns True when halted in a state in F, and False otherwise

  >>> check_input('abc@dsu.edu')
  True
  >>> check_input('abc@pluto.dsu.edu')
  True
  >>> check_input('11@123.com')
  True
  >>> check_input('a.b.ab')
  False
  >>> check_input('ab@ab')
  False
  >>> check_input('ab@ab.abcd')
  False
  """

  #print(state, input)

  # If we have no more input, return our result
  if len(input) == 0:
    return state in F

  # Use our transition function to get the next state
  try:
    next = δ[(state,input[0])]
  except KeyError:
    return state in F

  # Recurse using our input less the character we just processed and our next state
  return check_input(input[1:], next)