# 🔓 RSA — Common Modulus (Mixed Exponents) Attack

This write‑up explains a neat twist on the **Common Modulus** attack.  
You are given two ciphertexts of the **same message** under the **same modulus** `N` but with **different exponents**:

- `ct1 = m^e  mod N`
- `ct2 = m^(p+q)  mod N`

The trick is to notice the identity:

```
phi(N) = (p-1)(q-1) = N - (p+q) + 1   ⇒   p+q = N + 1 − phi(N)
```

Using Euler’s theorem (`m^phi(N) ≡ 1 (mod N)` when gcd(m, N)=1), we get:

```
m^(p+q) ≡ m^(N+1−phi(N)) ≡ m^(N+1) (mod N)
```

So **your second ciphertext is effectively using exponent `N+1`**:
```
ct2 = m^(p+q) ≡ m^(N+1) (mod N)
```

From here, this becomes a **two-exponent Common Modulus** problem with exponents `e` and `N+1`.

---

## 🧠 Core idea (Extended Euclid)

If `gcd(e, N+1) = 1`, there exist integers `a, b` such that
```
a·e + b·(N+1) = 1
```
By exponent laws modulo `N`:

```
m^(a·e + b·(N+1)) ≡ m^1 (mod N)
⇒ m ≡ (m^e)^a · (m^(N+1))^b (mod N)
⇒ m ≡ (ct1)^a · (ct2)^b (mod N)
```

If an exponent is negative, use the **modular inverse** (e.g., `(ct1)^(-3) = inv(ct1)^3 mod N`).

This lets you recover `m` **without factoring `N`**.

> The probability that `gcd(e, N+1) ≠ 1` for random `N` is negligible with standard `e=65537` (but handle it just in case — see notes below).

---

## ✅ Reference implementation (drop‑in)

Paste your `N`, `ct1`, `ct2`, `e` below. This script:
- verifies the consistency `pow(ct1, N+1, N) == pow(ct2, e, N)`,  
- computes `a, b` with extended Euclid,  
- handles negative exponents via modular inverses,  
- recovers and prints the plaintext bytes.

```python
from math import gcd
from Crypto.Util.number import long_to_bytes

# === paste your instance here ===
N  = ...  # modulus
ct1 = ... # m^e mod N
ct2 = ... # m^(p+q) mod N  (≡ m^(N+1) mod N)
e  = 65537

def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

# (m^e)^(N+1) ?= (m^(N+1))^e   — both equal m^(e·(N+1))
assert pow(ct1, N+1, N) == pow(ct2, e, N), "Inputs inconsistent: not same message/modulus"

g, a, b = egcd(e, N + 1)  # a*e + b*(N+1) = g
if g != 1:
    raise SystemExit(f"Requirement failed: gcd(e, N+1) must be 1 (got {g}). Try another exponent pair or instance.")

def modexp_signed(base, exp, mod):
    if exp >= 0:
        return pow(base, exp, mod)
    inv = pow(base, -1, mod)  # modular inverse
    return pow(inv, -exp, mod)

m = (modexp_signed(ct1, a, N) * modexp_signed(ct2, b, N)) % N
pt = long_to_bytes(m)
print(pt)
```

---

## 🧪 Why it works (quick proof)

We use two facts:
1. **Structure of `phi(N)`** for RSA with `N = p·q`:
   ```
   phi(N) = (p-1)(q-1) = N - (p+q) + 1  ⇒  p+q = N + 1 − phi(N)
   ```
2. **Euler’s theorem** (for gcd(m, N)=1): `m^phi(N) ≡ 1 (mod N)`

Therefore,
```
m^(p+q) = m^(N+1−phi(N)) ≡ m^(N+1) · (m^phi(N))^(−1) ≡ m^(N+1) (mod N)
```
so the second ciphertext behaves like an encryption with exponent `N+1`.

Finally, with `gcd(e, N+1)=1`, Extended Euclid gives integers `a,b` s.t. `a·e + b·(N+1)=1`, hence:
```
m ≡ (m^e)^a (m^(N+1))^b ≡ (ct1)^a (ct2)^b (mod N)
```

---

## ⚠️ Edge cases & notes

- **Coprimality**: The derivation needs `gcd(m, N)=1` for Euler’s theorem. Random RSA plaintexts satisfy this with overwhelming probability. If not, the message shares a factor with `N` and you can usually **factor N directly** via `gcd(m, N)` (or detect via side effects).
- **When gcd(e, N+1) ≠ 1**: The extended‑Euclid step fails. This is rare with `e=65537`. If it happens, you’d need a different second exponent (or a new instance) that is coprime with `e`.
- **Consistency check**: `pow(ct1, N+1, N) == pow(ct2, e, N)` must hold; it’s a quick sanity test that both ciphertexts indeed correspond to the *same* message under the *same* modulus.

---

## 🏁 Result

For the provided instance, the recovered flag is:

```
flag{31470335203860e47f0c3b1dd50e1da9}
```

---

## 📚 Further reading

- “RSA Attacks: Common Modulus” — overview article and examples.
- Textbook references on **Euler’s theorem** and the **Extended Euclidean Algorithm**.
