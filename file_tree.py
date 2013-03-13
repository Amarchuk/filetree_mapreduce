#!/usr/bin/env python 
import mincemeat
import sys
from tree import *
from node import *

def mapfn(k, v):
    x = v.split()
    yield x[0], (x[1].split("/")[1:-1], x[2])

def reducefn(k, vs):
    tree = Tree()
    tree.create_node("source", k)
    for v in vs:
        add_file(v[0], v[1], tree)
    tree.show()

s = mincemeat.Server() 

s.map_input = mincemeat.FileMapInputLineByLine(sys.argv[1]) 
s.mapfn = mapfn
s.reducefn = reducefn

results = s.run_server(password="changeme") 
for key, value in sorted(results.items()):
    print "%s: %s" % (key, value) 
