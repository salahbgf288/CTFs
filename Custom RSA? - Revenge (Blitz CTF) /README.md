# 🔐 Blitz CTF — Custom RSA? - Revenge

[![CTF](https://img.shields.io/badge/CTF-crypto-blue)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green)](#)
[![RSA](https://img.shields.io/badge/Algorithm-RSA-orange)](#)
[![SymPy](https://img.shields.io/badge/dep-sympy-important)](#)

This repo documents a clean way to recover the RSA public exponent **`e`** and decrypt a ciphertext when you’re given a fully factored value
`mod_phi = (p-1)(q-1)(e-1)`. We never need to factor `n` or explicitly compute `p` and `q`.

> **Key idea:** since `e - 1` divides `mod_phi`, enumerate divisors and keep only those that pass the five filters below. This reduces to a tiny candidate set—often a single `e`—and then decryption is straightforward.

---

## 🧭 TL;DR

- Factor `mod_phi` (we used dCode): https://www.dcode.fr/decomposition-nombres-premiers  
- Enumerate divisors `d` of `mod_phi` and set `e = d + 1`.
- Keep `e` only if it passes **all five filters** below.
- Compute `phi = mod_phi // (e - 1)`, `d = pow(e, -1, phi)`, `m = pow(c, d, n)`.
- For our instance, we get: **`Blitz{Cust0m_RSA_OMGGG}`**.

  <img width="828" height="424" alt="factor_custom" src="https://github.com/user-attachments/assets/3ce05fba-1cd4-406a-b525-afd2c58ed9d2" />


---

## 🧩 Problem setup

- Known:
  - RSA modulus `n`
  - The value `mod_phi = (p-1)(q-1)(e-1)` and its **prime factorization**
  - A ciphertext `c` to decrypt
- Goal: recover `e` (a **128‑bit prime**) and decrypt without recovering `p` or `q`.

> GitHub-safe equation formatting:
>
> ```text
> mod_phi = (p-1)(q-1)(e-1)
> phi     = mod_phi / (e-1)
> ```

### Example `mod_phi` factorization (given)

```
mod_phi = 2^3 × 3^2 × 67 × 673 × 3181 × 252401 × 23896409 × 145028189 ×
          79561224974873 × 308026511504069 × 4509599821882817 ×
          9907158782085681344183 × 38588687064594940957905160665643
```

---

## ✅ Five filters to eliminate false candidates

When iterating over divisors `d = e-1` of `mod_phi`, accept **only** if:

1. **Bit-length & parity:** `d` is **128-bit** and **even** (so `e = d+1` is odd).  
2. **Primality of `e`:** `e = d + 1` is a **128-bit prime** (use `sympy.isprime`).  
3. **Coprimality (cheap):** `mod_phi % e != 0`.  
   - Since `mod_phi = phi * (e-1)` and `gcd(e, e-1) = 1`, this enforces `gcd(e, phi) = 1`.  
4. **Discriminant is a perfect square:** with `phi = mod_phi / (e-1)`, define
   `S = n - phi + 1` and `Δ = S^2 - 4n`. Require `Δ ≥ 0` and **`Δ` is a perfect square**.  
   - Reason: `Δ = (p - q)^2`. If it’s not a square, no primes `p,q` exist for that `phi`.  
5. **Parity of `phi`:** `phi % 4 == 0` (holds for odd RSA primes `p,q`).

These five checks prune bad `e` **without** factoring `n` or computing `p,q`.

---

## 🛠️ Script

> Install once:
>
> ```bash
> pip install sympy
> ```

```python
#!/usr/bin/env python3
# Recover e from mod_phi using five filters, then decrypt.
# Inputs: n, mod_phi factorization, ciphertext c.

from itertools import product
from math import isqrt

# ---- Inputs ----
n = int("1236102848705753437579242450812782858653671889829265508760569425093229541662967763302228061")
mod_phi = int("381679521901481226602014060495892168161810654344421566396411258375972593287031851626446898065545609421743932153327689119440405912")

# Enter ciphertext c at runtime (decimal or 0x...):
c_str = input("Enter ciphertext c (decimal or 0x...): ").strip()
c = int(c_str, 0)

# Prime factorization of mod_phi:
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

# Primality (known library)
from sympy import isprime as is_prime

# Helpers
def prod(vals):
    r = 1
    for v in vals: r *= v
    return r

def is_square(x: int) -> bool:
    if x < 0: return False
    r = isqrt(x)
    return r*r == x

def int_to_bytes(x: int) -> bytes:
    if x == 0: return b"\x00"
    return x.to_bytes((x.bit_length() + 7) // 8, "big")

def printable_ascii(b: bytes) -> bool:
    return all((32 <= t <= 126) or t in (9,10,13) for t in b)

# Sanity check: factorization multiplies back
if prod(p**k for p,k in factors) != mod_phi:
    raise SystemExit("Factorization does not multiply back to mod_phi.")

# Build divisor basis and apply all five filters
basis = [[p**i for i in range(k+1)] for p,k in factors]
candidates = []  # (e, phi)

for parts in product(*basis):
    d = prod(parts)                # d = e - 1
    # (1) 128-bit even d
    if d.bit_length() != 128 or (d & 1) != 0:
        continue
    e = d + 1
    # (2) 128-bit prime e
    if e.bit_length() != 128 or not is_prime(e):
        continue
    # (3) mod_phi % e != 0
    if mod_phi % e == 0:
        continue
    # Compute phi
    phi = mod_phi // d
    # (5) phi % 4 == 0
    if (phi & 3) != 0:
        continue
    # (4) discriminant must be a perfect square
    S = n - phi + 1
    Δ = S*S - 4*n
    if not is_square(Δ):
        continue
    candidates.append((e, phi))

if not candidates:
    raise SystemExit("No viable e found using filters (1)-(5).")

print(f"[i] Candidates after (1)-(5): {len(candidates)}")
for idx, (e, phi) in enumerate(candidates, 1):
    print(f"  [{idx}] e = {e}")

# Try decrypt with each candidate (stop when printable/flag-like)
for idx, (e, phi) in enumerate(candidates, 1):
    try:
        d_priv = pow(e, -1, phi)
    except ValueError:
        print(f"[{idx}] e={e}: no modular inverse mod phi")
        continue
    m = pow(c, d_priv, n)
    m_hex = hex(m)
    m_bytes = int_to_bytes(m)
    print(f"\n[{idx}] e = {e}")
    print(f"     hex(m) = {m_hex}")
    if printable_ascii(m_bytes):
        try:
            s = m_bytes.decode("utf-8")
            print(f"     ascii  = {s!r}")
            if "{" in s and "}" in s:
                print("\n[✓] Plausible flag detected.")
                break
        except UnicodeDecodeError:
            print("     ascii  = <not UTF-8>")
    else:
        print("     ascii  = <non-printable>")
else:
    print("\n[!] No flag-like ASCII detected. Verify inputs.")
```

---

## 📌 Result for this challenge

For the provided instance (with the known ciphertext), the script finds:

- `e = 308776508606152118670230312260475727067` (128‑bit prime)  
- Decryption yields:
  - `hex(m) = 0x426c69747a7b43757374306d5f5253415f4f4d4747477d`  
  - `ascii  = 'Blitz{Cust0m_RSA_OMGGG}'` ✅

---

## 🧠 Notes
- The discriminant check (4) is a **mathematical consistency** test: `Δ = (p-q)^2` must be a perfect square for any integers `p,q` with product `n`. It lets us reject bad `phi` **without** factoring `n`.
- Condition (3) (`mod_phi % e != 0`) cheaply enforces `gcd(e, phi) = 1` because `mod_phi = phi * (e-1)` and `gcd(e, e-1) = 1`.

---

## 🏁 Credits
- Factorization helper: **dCode**.
- Thanks to the challenge authors for the tidy structure that makes divisor pruning effective.
