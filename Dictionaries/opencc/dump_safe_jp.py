#!/usr/bin/env python
# coding: utf8
# 2/5/2015 jichi
# Print JP variant characters and line numbers to keep
t = open("TSCharacters.txt", 'r').read().decode('utf8')
s = open("STCharacters.txt", 'r').read().decode('utf8')

for i, line in enumerate(open("JPVariants.txt", 'r')):
  line = line.decode('utf8')
  if line and line[0] != '#':
    ch = line[0]
    if ch in t or ch in s:
      print line[:-1]
      #print i+1, ch

# EOF
