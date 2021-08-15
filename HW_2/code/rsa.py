from sage.all import *
from Crypto.Util.number import long_to_bytes
from itertools import count
import sys

n = 22001778874542774315484392481115711539281104740723517828461360611903057304469869336789715900703500619163822273767393143914615001907123143200486464636351989898613180095341102875678204218769723325121832871221496816486100959384589443689594053640486953989205859492780929786509801664036223045197702752965199575588498118481259145703054094713019549136875163271600746675338534685099132138833920166786918380439074398183268612427028138632848870032333985485970488955991639327
c = 1067382668222320523824132555613324239857438151855225316282176402453660987952614935478188752664288189856467574123997124118639803436040589761488611318906877644244524931837804614243835412551576647161461088877884786181205274671088951504353502973964810690277238868854693198170257109413583371510824777614377906808757366142801309478368968340750993831416162099183649651151826983793949933939474873893278527484810417812120138131555544749220438456366110721231219155629863865
e = 65537

x = PolynomialRing(IntegerRing(), 'x').gen()

for e1_p_e2 in count(0):
    found = False
    for e1 in range(e1_p_e2 + 1):
        e2 = e1_p_e2 - e1
        f = x * (2 * x + e1) * (3 * (2 * x + e1) + e2) - n
        roots = f.roots()
        if (len(roots) != 0):
            found = True
            break
    if found:
        break
    
p = int(roots[0][0])
#p = 12239363968862301655032671889408678336365197765290722249588768227649140689948872816725306416825242592654590826028443535297344717808724316145004300860420999
q1 = 2 * p + e1
q2 = 3 * q1 + e2
assert p * q1 * q2 == n
phi = (p - 1) * (q1 - 1) * (q2 - 1)
d = pow(e, -1, phi)
m = pow(c, d, n)
flag = long_to_bytes(m)
print(flag)
