# Gotam Solver — Legendre‑symbol bit extraction (Goldwasser–Micali)

This repo contains a tiny solver for the **Gotam** CTF challenge. The service encrypts each bit of the secret using a quadratic‑(non)residue trick over an RSA modulus; once you **factor `n`**, every bit can be recovered with a single Legendre‑symbol check. This is exactly the Goldwasser–Micali (GM) cryptosystem.

---

## TL;DR

- Challenge publishes `n` and a special element `t`.
- It streams many ciphertext limbs `c_i` that each encode one plaintext bit.
- If you know a factor of `n`, you can test each `c_i` with the **Legendre symbol** to decide if it's a square (bit `0`) or a square times `t` (bit `1`).
- We factored `n` with an online factoring site and recovered the flag in one pass.

Final flag:
```
b'ASIS{Priv4te_c0mpari5oN_iZ_fundAm3ntaL_7O_s3cuRe_mult1pArtY_cOmpuTatIons!}'
```

---

## How the challenge works

- The server generates primes `p, q` and publishes `n = p·q` plus a parameter `t` that is a **quadratic non‑residue modulo both `p` and `q`**.
- To encrypt a bit `b ∈ {0,1}`, it samples a random `r` and outputs
  ```text
  c = (t^b · r^2) mod n
  ```
  So when `b = 0` the limb is a square modulo `n`, and when `b = 1` the limb is that same square multiplied by `t`.

This is precisely the *Goldwasser–Micali* (GM) bit‑encryption pattern.

---

## Why the attack works

For an odd prime `p`, the **Legendre symbol** of `x` modulo `p` is
```
x^((p−1)/2) mod p →  +1  if x is a quadratic residue (a square)
                    −1  if x is a non‑residue
                     0  if x ≡ 0 (mod p)
```
Squares stay squares when multiplied by another square, so `r^2` is always a residue, while `t·r^2` is a non‑residue **provided `t` is itself a non‑residue**. Therefore, if you know *either* factor `p` or `q`, you can evaluate the Legendre symbol of each ciphertext limb and map `+1 → 0`, `−1 → 1` to recover the bits independently.

Corner case: if a limb is `0 mod p` the test yields `0`; the solver just **falls back to the other prime `q`**. (This is extremely rare and cannot happen for both primes unless the value is `0 mod n`, which legitimate limbs are not.)

---

## Where the data came from (netcat transcript)

All big numbers were copied straight from the challenge service via **netcat**:
```bash
nc 65.109.194.34 13131
```

The service prints a banner and a tiny menu. Choosing **`[P]ublic data`** dumps `n` and `t`:
```
n, t =  0x46444050a1b4bfe70f30f48e18a977ad4c5eee5f52c7bb218c305b86f82dff3f, 0x452c1d18be589c479bca68eceade3260abb3e1217ba23627f26ffe3422e53d8d
```

Choosing **`[E]ncrypt flag`** streams a lot of ciphertext limbs (one per bit), e.g.:
```
hex(e) = '0x29bcab7058d4ff2d2333524a4aac214b93fb9e9c0adf829b21594a1323324464'
hex(e) = '0xfbc464e588a813f0b8616dd399b6b614c59954b4e32e4805aeb775f51e0b7c0'
hex(e) = '0xc1c76e0a5abde139c7f6af4c787a147a0cf9275d8817c1bb75c2312f62634f3'
…
```
Paste those hex strings into the solver to reproduce our run.

---

## Factoring `n`

To make the Legendre test possible, we first **factorised the modulus `n`** to obtain `p` and `q`.  
For speed we used an online advanced factoring site (e.g., *dcode.fr → Prime Number Decomposition*). Any reliable factorisation tool works; the important bit is getting **one** prime factor so we can compute Legendre symbols.

> Without `p` or `q`, distinguishing squares from non‑squares modulo the composite `n` is believed hard (Quadratic Residuosity Assumption), which is why GM is secure against passive adversaries.

---

## What the solver does

1. **Loads `p` and `q`** (the factors of the provided `n`).  
2. Implements `bit_from_legendre(c, prime)` that returns `0` for residues and `1` for non‑residues.  
3. For each limb `c_i`, tries the test modulo `p`; if it returns `0`, retries modulo `q`.  
4. Concatenates the bits, converts the big binary string to bytes, and strips any leading `0x00` introduced by fixed‑length padding on the server.  
5. Prints the recovered bytes — the flag above.

---

## Usage

1. **Dependencies** (only for `long_to_bytes` helper):
   ```bash
   python3 -m pip install pycryptodome
   ```

2. **Put the captured limbs** (from `nc`, see above) into the `E = [...]` list inside `gotam_solver.py`.

3. **Run the solver**:
   ```bash
   python3 gotam_solver.py
   ```

   Expected output:
   ```
   b'ASIS{Priv4te_c0mpari5oN_iZ_fundAm3ntaL_7O_s3cuRe_mult1pArtY_cOmpuTatIons!}'
   ```

---

## Repo layout

- `gotam.py` — Minimal client / helper to interact with the service and collect limbs.
- `gotam_solver.py` — Offline decoder using Legendre symbols with the recovered `p, q`.

---

## References

- Goldwasser–Micali public‑key cryptosystem (quadratic residuosity based). Any crypto text (e.g., Katz & Lindell) will have a good treatment.
