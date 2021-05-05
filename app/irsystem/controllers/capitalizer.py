import re
import string

def capitalizer(s, type):
  if type=='title':
    return str.title(s)
  elif type=='description':
    s = s.capitalize()
    s = re.sub('[! ? .]+([\s])+([a-z]+)', lambda x : x.group(0).title(), s)
    return s
