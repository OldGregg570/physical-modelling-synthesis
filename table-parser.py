import sys

sal_cmd = "play (seq ("

sqfl = lambda fl: float(fl) ** 2
vec_len = lambda line:  '{0:f}'.format((sqfl(line [0]) + sqfl(line [1]) + sqfl(line [2])) ** 0.5)
parse_line = lambda line: { 'freq' : str(line[2]), 'amp' : str(vec_len (line[4:])) }

with open(sys.argv[1]) as f:
    for overtone in [parse_line(line.split()) for line in f.readlines()]:
        sal_cmd += overtone['amp'] + ' * hzosc (' + overtone['freq'] + ') + \n'

print sal_cmd[:-3] + ")~ 4)"
