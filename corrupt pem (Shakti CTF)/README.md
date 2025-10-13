# Lost-PEM RSA (ShaktiCTF) – Write-up

> Recover a corrupted RSA private key from partial data, rebuild the full PEM, and decrypt the ciphertext to get the flag.

---

## 🧾 Starting files

- `private_key.pem` – a corrupted/partial RSA private key (still contains useful CRT components like `p`, `d`, and `qInv`).
- `ciphertext.txt` – a base-10 integer `c` (the RSA ciphertext).

---

## 🔍 High-level approach

1. **What was known/extractable from the corrupted key**
   - Public exponent `e = 65537`.
   - Private exponent `d`.
   - Prime `p`.
   - The inverse `qInv = q^{-1} mod p` (a.k.a. `iqmp` in OpenSSL dumps).
   - The low bits of the modulus: `lower_n = n mod 2^L` (provided by the challenge / derivable from leaked structure).

2. **Recovering `q` with CRT**
   - From `lower_n` and `p`, we get a **low-bits constraint** on `q`:
     
     q ≡ (lower_n · p^{-1}) (mod 2^L)

   - From `qInv = q^{-1} mod p`, we get a **mod-`p` constraint**:
     
     q ≡ (qInv)^{-1} (mod p)

   - Combine the two congruences with **CRT** (moduli `p` and `2^L` are coprime) → unique `q` in `[0, p·2^L)`.

3. **Rebuild the full key**
   - Compute `n = p·q`, `dp = d mod (p−1)`, `dq = d mod (q−1)`, and recompute `qInv = q^{-1} mod p` for the final `(p,q)` order.
   - Encode a **PKCS#1** `RSA PRIVATE KEY` (ASN.1 DER) and write it as a PEM.

4. **Decrypt the ciphertext**
   - Decrypt `m = c^d mod n`.
   - This challenge used **textbook RSA (no PKCS#1 v1.5 padding)**, so OpenSSL must be told `rsa_padding_mode:none` (otherwise you’ll see *“padding check failed”*).
   - The plaintext is:
     ```
     Here is you reward, for you have earned it !!!! shaktictf{y0u_discov3r3d_th3_l0st_p3m}
     ```
     → **Flag**: `shaktictf{y0u_discov3r3d_th3_l0st_p3m}`

---

## 🧪 Repo layout

```
.
├─ README.md                 # this file
├─ write_pem.py              # reconstruct full PKCS#1 RSA private key (PEM)
└─ decrypt.py                # decrypt c using the recovered key; prints plaintext + flag
```

---

## ⚙️ Prereqs

- Python 3.8+
- OpenSSL (3.x preferred; 1.1.1 also works)

---

## ▶️ Usage

### 1) Rebuild the RSA private key (PEM)

```bash
python3 write_pem.py recovered_rsa_private_key.pem
```

Validate:

```bash
openssl pkey -in recovered_rsa_private_key.pem -text -noout | head
```

### 2) Decrypt the ciphertext

Using the Python helper:

```bash
python3 decrypt.py
```

Or a **one-liner** with OpenSSL (textbook RSA → **no padding**):

```bash
# Replace 512 if your modulus byte length differs (4096-bit => 512 bytes)
openssl pkeyutl -decrypt   -inkey recovered_rsa_private_key.pem   -pkeyopt rsa_padding_mode:none   -in <(python3 -c 'c=int(open("ciphertext.txt").read().strip());import sys;sys.stdout.buffer.write(c.to_bytes(512,"big"))')   -out -
```

> If your modulus is not exactly 4096-bit, replace `512` with `ceil(bitlen(n)/8)`.

---

## 🧠 How it works (math notes)

Let `L = bitlen(lower_n)` and `M = 2^L`. We know `n ≡ lower_n (mod M)` and `n = p·q`.

- Therefore `p·q ≡ lower_n (mod M)` → `q ≡ lower_n · p^{-1} (mod M)`.
- Also `qInv = q^{-1} (mod p)` → `q ≡ qInv^{-1} (mod p)`.

Solve the system via Chinese Remainder Theorem:

```
q ≡ a (mod p)         with  a = qInv^{-1} mod p
q ≡ b (mod 2^L)       with  b = (lower_n · p^{-1} mod 2^L)
```

Once `q` is found, rebuild `n, dp, dq, qInv` and encode the PKCS#1 PEM.

---

## 🧯 Troubleshooting

- **“pkcs decoding error / padding check failed”**  
  Use `rsa_padding_mode:none` — this challenge used textbook RSA (no padding).

- **OpenSSL refuses the key**  
  Ensure `p > q` (many toolchains expect sorted primes). Recompute `qInv` after ordering.

- **Byte length mismatch**  
  When converting the decimal ciphertext to bytes, use the key size in bytes (e.g., `512` for ~4096-bit).

---

## ✅ Result

- Recovered full RSA private key (PEM).
- Decrypted plaintext:
  ```
  Here is you reward, for you have earned it !!!! shaktictf{y0u_discov3r3d_th3_l0st_p3m}
  ```
- **Flag**: `shaktictf{y0u_discov3r3d_th3_l0st_p3m}`

Happy pwning! 🛠️🔐

