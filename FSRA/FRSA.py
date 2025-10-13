from Crypto.Util.number import *
from random import *

p = getStrongPrime(1024)
q = getStrongPrime(1024)
n = p*q
e = randrange(2**512,2**1024)

plaintext = open('so_wonderful_work.txt','r').read().lower()
arr = []
for i in plaintext:
	arr.append(pow(ord(i),e,n))
open('wonderful_work.txt','w').write(str(n)+"\n"+str(arr))
