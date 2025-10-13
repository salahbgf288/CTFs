#!/usr/bin/env python3
# Find e from mod_phi using:
# (1) 128-bit even d = e-1 divisor of mod_phi
# (2) 128-bit PRIME e = d+1  (sympy.isprime)
# (3) mod_phi % e != 0   (ensures gcd(e, φ(n)) = 1 since mod_phi = φ(n)*(e-1))
# (4) Discriminant check: with φ = mod_phi/(e-1), S = n - φ + 1 and Δ = S^2 - 4n must be a non-negative perfect square
# (5) φ % 4 == 0  (odd p,q)
# Then decrypt and print the plaintext.

from itertools import product
from math import gcd, isqrt

# ---- Inputs ----
n = int("1236102848705753437579242450812782858653671889829265508760569425093229541662967763302228061")
mod_phi = int("381679521901481226602014060495892168161810654344421566396411258375972593287031851626446898065545609421743932153327689119440405912")

c = 337624956533508120294617117960499986227311117648449203609049153277315646351029821010820258

# Prime factorization of mod_phi:
# 2^3 × 3^2 × 67 × 673 × 3181 × 252401 × 23896409 × 145028189 ×
# 79561224974873 × 308026511504069 × 4509599821882817 ×
# 9907158782085681344183 × 38588687064594940957905160665643
factors = [
    (2,3),
    (3,2),
    (67,1),
    (673,1),
    (3181,1),
    (252401,1),
    (23896409,1),
    (145028189,1),
    (79561224974873,1),
    (308026511504069,1),
    (4509599821882817,1),
    (9907158782085681344183,1),
    (38588687064594940957905160665643,1),
]

# ---- Primality (known library) ----
from sympy import isprime as is_prime

# ---- Helpers ----
def prod(vals):
    r = 1
    for v in vals: r *= v
    return r

def int_to_bytes(x: int) -> bytes:
    if x == 0: return b"\x00"
    return x.to_bytes((x.bit_length() + 7) // 8, "big")

def printable_ascii(b: bytes) -> bool:
    return all((32 <= t <= 126) or t in (9,10,13) for t in b)

def is_square(x: int) -> bool:
    if x < 0: return False
    r = isqrt(x)
    return r*r == x

# sanity: factorization matches mod_phi
if prod(p**k for p,k in factors) != mod_phi:
    raise SystemExit("Factorization does not multiply back to mod_phi.")

# ---- enumerate divisors d = e-1 and apply ALL (1)–(5) ----
basis = [[p**i for i in range(k+1)] for p,k in factors]
candidates = []

for parts in product(*basis):
    d = prod(parts)  # divisor of mod_phi

    # (1) 128-bit & even
    if d.bit_length() != 128 or (d & 1) != 0:
        continue

    e = d + 1

    # (2) 128-bit prime e
    if e.bit_length() != 128 or not is_prime(e):
        continue

    # (3) ensure gcd(e, φ(n)) = 1 without φ(n): since mod_phi = φ(n)*(e-1),
    #     if mod_phi % e == 0 then e | φ(n) ⇒ reject
    if mod_phi % e == 0:
        continue

    # (5) φ must be divisible by 4 for odd RSA primes
    phi = mod_phi // d
    if (phi & 3) != 0:
        continue

    # (4) discriminant must be a non-negative perfect square:
    #     S = p+q = n - φ + 1, Δ = S^2 - 4n = (p-q)^2
    S = n - phi + 1
    Δ = S*S - 4*n
    if not is_square(Δ):
        continue

    candidates.append((e, phi))

if not candidates:
    raise SystemExit("No viable e found using rules (1)–(5).")

print(f"[i] Candidates after (1)–(5): {len(candidates)}")

# ---- Try decrypt with each candidate ----
for idx, (e, phi) in enumerate(sorted(set(candidates)), 1):
    try:
        dpriv = pow(e, -1, phi)  # modular inverse
    except ValueError:
        print(f"[{idx}] e={e}: no modular inverse mod phi (skipping).")
        continue

    m = pow(c, dpriv, n)
    m_hex = hex(m)
    m_bytes = int_to_bytes(m)

    print(f"\n[{idx}] e = {e}  (128-bit prime)")
    print(f"     hex(m) = {m_hex}")
    if printable_ascii(m_bytes):
        try:
            s = m_bytes.decode("utf-8")
            print(f"     ascii  = {s!r}")
            if "{" in s and "}" in s:
                print("\n[✓] Flag detected.")
                break
        except UnicodeDecodeError:
            print("     ascii  = <not UTF-8>")
    else:
        print("     ascii  = <non-printable>")
else:
    print("\n[!] Tried all candidates; no flag-like ASCII found. Check c/n/mod_phi inputs.")
