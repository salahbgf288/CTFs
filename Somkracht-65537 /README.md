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

- RSA Attacks: Common Modulus — InfosecWriteups (article referenced in this challenge):  
  https://infosecwriteups.com/rsa-attacks-common-modulus-7bdb34f331a5
- Textbook references on **Euler’s theorem** and the **Extended Euclidean Algorithm**.
