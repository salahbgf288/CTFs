# 🔐 Blitz CTF - Custom RSA? - Revenge

[![CTF](https://img.shields.io/badge/CTF-crypto-blue)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green)](#)
[![RSA](https://img.shields.io/badge/Algorithm-RSA-orange)](#)
[![Markdown](https://img.shields.io/badge/README-md-lightgrey)](#)

A short, practical write-up + code for a custom RSA challenge where the only real trick is identifying the public exponent **`e`** using a **fully factored** value  
`mod_phi` $=(p-1)(q-1)(e-1)$

Once `e` is known, the rest is just classic RSA:
- compute \(\varphi = \dfrac{\texttt{mod\_phi}}{e-1}\),
- compute the private exponent \(d \equiv e^{-1} \pmod{\varphi}\),
- and decrypt \(m \equiv c^d \bmod n\).

---

## 🧭 TL;DR

> **Flag:** `Blitz{Cust0m_RSA_OMGGG}` ✅

---

## 🧩 Problem Overview

- We’re given an RSA modulus \(n = pq\) and the value  
  \(\texttt{mod\_phi} = (p-1)(q-1)(e-1)\).
- The only difficulty is identifying `e`. Knowing `e` lets us compute `phi` and then `d`.
- Crucially, **`mod_phi` is easy to factor**, making `e` easy to determine.

We used **dCode’s integer factorization** tool to factor `mod_phi`:  
🔗 https://www.dcode.fr/decomposition-nombres-premiers

### Factorization provided

```
mod_phi = 2^3 × 3^2 × 67 × 673 × 3181 × 252401 × 23896409 × 145028189 ×
          79561224974873 × 308026511504069 × 4509599821882817 ×
          9907158782085681344183 × 38588687064594940957905160665643
```

> With our solver, this leads directly to:
>
> ```
> e = 308776508606152118670230312260475727067
> ```

---

## 🧮 Recovering φ, d, and m

Once `e` is known:

```python
# Given:
#   mod_phi = (p-1)*(q-1)*(e-1)
#   n       = modulus from the challenge
#   c       = ciphertext from the challenge

e = 308776508606152118670230312260475727067
mod_phi = 381679521901481226602014060495892168161810654344421566396411258375972593287031851626446898065545609421743932153327689119440405912

phi = mod_phi // (e - 1)               # φ = (p-1)(q-1)
d   = pow(e, -1, phi)                  # d = e^{-1} mod φ
m   = pow(c, d, n)                     # plaintext integer

# 🔎 Decode hex(m) to the ASCII flag (demo with known result)
hex_m = "0x426c69747a7b43757374306d5f5253415f4f4d4747477d"
flag = bytes.fromhex(hex_m[2:] if hex_m.startswith("0x") else hex_m).decode()
print("hex(m) =", hex_m)
print("flag   =", flag)
```

### ✅ Our results

- `phi = mod_phi // (e - 1)`  
- `d = pow(e, -1, phi)`  
- `m = pow(c, d, n)`  
- **Hex(m)** = `0x426c69747a7b43757374306d5f5253415f4f4d4747477d`  
- **Decoded** → `Blitz{Cust0m_RSA_OMGGG}`

---

## 🛠️ How the identification of `e` works (intuition)

- Since `mod_phi = (p-1)(q-1)(e-1)` is **fully factored**, its divisor structure makes it easy to isolate `e-1` once you can determine \((p-1)(q-1)\) or otherwise leverage the factorization to split \(n\).
- In our solver, we use the factorization to **induce orders** that help split \(n\) (e.g., via \(\gcd(a^k-1, n)\) tricks), recover \(p, q\), and compute  
  \(\varphi(n) = (p-1)(q-1)\).  
  Then \(e-1 = \dfrac{\texttt{mod\_phi}}{\varphi(n)}\) → **`e`**.

---

## 🧪 Reproduce (minimal script)

If you only need to turn the provided numbers into the flag:

```bash
python3 - << 'PY'
e = 308776508606152118670230312260475727067
mod_phi = 381679521901481226602014060495892168161810654344421566396411258375972593287031851626446898065545609421743932153327689119440405912

phi = mod_phi // (e - 1)
d   = pow(e, -1, phi)

# Fill in your challenge values for c and n:
# n = ...
# c = ...
# m = pow(c, d, n)
# print(hex(m))

# For the solved instance we obtained (and decode it to print the flag):
hex_m = "0x426c69747a7b43757374306d5f5253415f4f4d4747477d"
flag = bytes.fromhex(hex_m[2:]).decode()
print("hex(m) =", hex_m)
print("flag   =", flag)
PY
```

---

## 🧠 Notes & Takeaways

- If a challenge exposes \(\texttt{mod\_phi}=(p-1)(q-1)(e-1)\) **and it factors cleanly**, then `e` is **not secret** at all.
- Once `e` is recovered, everything else (φ, d, and the message) follows from standard RSA math.
- Protecting any function of \(\varphi(n)\) (or close relatives) is as important as protecting \(p\) and \(q\).

---

## 📎 Appendix (numbers)

<details>
<summary>Challenge constants used in our solve</summary>

- `e = 308776508606152118670230312260475727067`  
- `mod_phi = 381679521901481226602014060495892168161810654344421566396411258375972593287031851626446898065545609421743932153327689119440405912`  
- `hex(m) = 0x426c69747a7b43757374306d5f5253415f4f4d4747477d` → `Blitz{Cust0m_RSA_OMGGG}`
</details>

<details>
<summary>Factorization source</summary>

We used dCode’s prime decomposition tool:  
https://www.dcode.fr/decomposition-nombres-premiers
</details>

---

## 🏁 Credits

- Solver + write-up by the team (thanks for the tidy factorization!).
- Factorization helper: **dCode**.

