# Gotam Solver — Legendre-symbol bit extraction (a.k.a. Goldwasser–Micali)

This repo contains a tiny solver for the **Gotam** challenge. The challenge encrypts each bit of the secret using a quadratic-(non)residue trick over an RSA modulus. If you know the prime factors of the modulus, you can recover each bit with a single Legendre symbol — which is exactly what the solver does.

---

## How the challenge works (high level)

- The server generates two 128‑bit primes `p, q` and publishes `n = p·q`.
- It also picks an element `t` that is a **quadratic non‑residue modulo _both_** `p` and `q`.
- To encrypt a bit `b ∈ {0,1}`, it chooses a random `r` and outputs
  
  ```text
  c = (t^b · r^2) mod n
  ```

  so `c = r^2 (mod n)` when `b = 0`, and `c = t·r^2 (mod n)` when `b = 1`.

- The challenge encodes the whole message as a **1024‑bit** binary string and emits one ciphertext limb per bit.

This is precisely the *Goldwasser–Micali* (GM) encryption pattern.

---

## Why the attack works (math in one paragraph)

For an odd prime `p`, the **Legendre symbol** of `x` modulo `p` is `x^{(p−1)/2} (mod p)`, which equals `+1` if `x` is a quadratic residue and `−1` otherwise. Squares remain squares after multiplying by a square, so `r^2` is a residue (Legendre `+1`), while `t·r^2` is a non‑residue (Legendre `−1`) **provided `t` itself is a non‑residue**. Therefore, if you know a factor of `n` (either `p` or `q`), you can evaluate the Legendre symbol of each ciphertext limb and map `+1 → bit 0`, `−1 → bit 1` to recover the plaintext bits independently.

Corner case: If a limb happens to be divisible by `p`, the Legendre symbol returns `0`. The solver just **falls back to the other prime** `q`. (The event that a random square equals `0 mod p` is negligible; it also cannot be `0 mod p` *and* `0 mod q` unless it is `0 mod n`, which never happens with the challenge’s sampling.)

---

## What the solver does

1. **Hard‑codes `p` and `q`** (the factorization used for the provided instance).
2. Defines `bit_from_legendre(c, prime)` that returns `0` for residues and `1` for non‑residues.
3. Runs that test on every ciphertext limb, falling back to `q` if the residue test is `0` modulo `p`.
4. Stitches the recovered bits into a binary string and converts to bytes. The challenge left‑pads the bitstring to 1024 bits, so the solver strips leading `0x00` bytes after conversion.

---

## File layout

- `gotam.py` — the challenge service (generates keys, encrypts bit‑by‑bit).
- `gotam_solver.py` — the offline solver (recovers the plaintext from the printed ciphertext limbs).

---

## Usage

1. **Install dependencies** (only needed for `long_to_bytes` helper):
   ```bash
   python3 -m pip install pycryptodome
   ```

2. **Collect the ciphertext limbs** from the challenge (`[E]ncrypt flag` option). Paste the printed hex values into the `E = [...]` list in `gotam_solver.py`.

3. **Run the solver**:
   ```bash
   python3 gotam_solver.py
   ```

   You should see the plaintext bytes printed (the flag).

---

## Code excerpts (for orientation)

### Legendre‑symbol bit test

```python
def bit_from_legendre(c, prime):
    s = pow(c % prime, (prime - 1)//2, prime)
    if s == 1: return 0      # residue ⇒ bit 0
    if s == prime - 1: return 1  # non-residue ⇒ bit 1
    raise ZeroDivisionError   # rare: c ≡ 0 (mod prime)
```

### Recover all bits with p / q fallback

```python
def recover_bits(E):
    bits = []
    for c in E:
        try:
            bits.append(bit_from_legendre(c, p))
        except ZeroDivisionError:
            bits.append(bit_from_legendre(c, q))
    return bits
```

### Reassemble the message

```python
bits = recover_bits(E)
M = ''.join(map(str, bits))
pt = long_to_bytes(int(M, 2)).lstrip(b'\\x00')
print(pt)
```

> Note: The `lstrip(b'\\x00')` is needed because the challenge pads the bitstring to a **fixed 1024 bits** before encrypting; removing leading zero bytes restores the original message length.

---

## Security note

Without `p` or `q`, distinguishing residues from non‑residues **modulo the composite `n`** is believed hard (quadratic residuosity assumption). That’s why GM is semantically secure under factoring. This solver only succeeds because it is aimed at a specific instance whose factorization is known.

---

## License

MIT

## Where the data came from (nc transcript)

All the big numbers in `gotam_solver.py` came straight from the challenge service over **netcat**.

I connected to the remote with:

```bash
nc <host> <port>
```

After connecting, the service printed a banner and a tiny menu like this (trimmed):

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Unlock Gotam's tailored encryption—can you outsmart this custom asymmetric enigma? ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┃ Options: 
┃   [E]ncrypt flag 
┃   [P]ublic data 
┃   [Q]uit
```

- Choosing **`[P]ublic data`** dumped the RSA-like modulus and a parameter `t`:
  ```text
  n, t =  0x46444050a1b4bfe70f30f48e18a977ad4c5eee5f52c7bb218c305b86f82dff3f, 0x452c1d18be589c479bca68eceade3260abb3e1217ba23627f26ffe3422e53d8d
  ```
- Choosing **`[E]ncrypt flag`** caused the service to stream hundreds of lines like:
  ```text
  hex(e) = '0x29bcab7058d4ff2d2333524a4aac214b93fb9e9c0adf829b21594a1323324464'
  hex(e) = '0x0fbc464e588a813f0b8616dd399b6b614c59954b4e32e4805aeb775f51e0b7c0'
  ... (many more)
  ```

Those are exactly the values I copied into `gotam_solver.py` under the variables `n`, `t`, and the long list `E`.

## Why factorising `n` was necessary (and how I did it)

To make sense of the transcript and be able to decrypt/recover the flag offline, I first **factorised the modulus `n`** into its two primes `p` and `q`.  
For speed, I used an **online advanced factoring website** (e.g. Alpertron ECM or FactorDB): I pasted the hex value of `n` and retrieved `p` and `q`. These prime factors are then hard‑coded in `gotam_solver.py` so the script can work without internet access.

Once `p` and `q` are known, the rest of the solver follows the math implemented in `gotam.py` (Chinese Remainder Theorem steps and per‑bit recovery based on the stream of `hex(e)` values). In short:

1. Read `n`, `t`, and all the `hex(e)` lines from the nc session.
2. Factor `n` via an advanced factoring site to get `p` and `q`.
3. Run `python gotam_solver.py` to reconstruct the flag using those values.

> Note: I didn’t brute‑force or guess the primes. The only “external help” was the public factoring website to split `n`; everything else is derived from the service output.


