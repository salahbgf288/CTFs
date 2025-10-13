"""
So you were able to break the last RSA implementation of mine.... but this time i've made it more difficult. Try breaking this one!! Haha!

Author: 5h1kh4r

"""
from Cryptodome.Util.number import long_to_bytes, getPrime, bytes_to_long

m = b"Blitz{REDACTED}"

p = getPrime(150)
q = getPrime(150)
e = getPrime(128)
n = p*q
mod_phi = (p-1)*(q-1)*(e-1)
d = pow(e, -1, mod_phi)

print(mod_phi)
print(n)
c = pow(bytes_to_long(m), e, n)
print(c)
