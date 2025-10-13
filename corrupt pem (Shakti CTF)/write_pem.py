#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild q via CRT from the partial RSA data and write a PKCS#1 PEM
('RSA PRIVATE KEY') containing n, e, d, p, q, dp, dq, qInv.

Usage:
  python3 write_pem.py [output_pem_path]
"""

import sys
import base64

def ih(s: str) -> int:
    s = s.strip().lower().replace("\n", "").replace(" ", "")
    if s.startswith("0x"):
        s = s[2:]
    return int(s, 16)

def invmod(a: int, m: int) -> int:
    try:
        return pow(a, -1, m)
    except ValueError:
        # Extended Euclid fallback
        t, nt = 0, 1
        r, nr = m, a % m
        while nr:
            q = r // nr
            t, nt = nt, t - q * nt
            r, nr = nr, r - q * nr
        if r != 1:
            raise ValueError("No inverse exists")
        return t % m

def crt_two(r1: int, m1: int, r2: int, m2: int) -> int:
    """x ≡ r1 (mod m1), x ≡ r2 (mod m2) with coprime m1,m2."""
    inv = invmod(m1 % m2, m2)
    t = ((r2 - r1) % m2) * inv % m2
    return r1 + m1 * t

def der_len(n: int) -> bytes:
    if n < 128:
        return bytes([n])
    lb = n.to_bytes((n.bit_length()+7)//8, 'big')
    return bytes([0x80 | len(lb)]) + lb

def der_int(x: int) -> bytes:
    b = b"\x00" if x == 0 else x.to_bytes((x.bit_length()+7)//8, 'big')
    if b[0] & 0x80:  # keep INTEGER positive
        b = b'\x00' + b
    return b'\x02' + der_len(len(b)) + b

def der_seq(*elts: bytes) -> bytes:
    content = b''.join(elts)
    return b'\x30' + der_len(len(content)) + content

# ===== Provided data =====
lower_n = ih("""
6463395ca1b63be1279cd97694ade51927267ae45c70e736c3f130109c0a0b6e55458eece2ba8fa8e6111a07dd290ca82bbea2a7423232242663d92cab0c75b524a7e32ac602ef42a2f853cc920ef086be259c0674b66bf48deb7d
""")

e = ih("0x010001")

d = ih("""
7b6da188fa79a30e377cf4075b884890481f0456a2da1da02098c6ac1a7a856d93577393abafa57c1ad98347a5d3abc3074cc79da804249d592903e0e5dc2785adcff39f22b742db76e4f4f6acabdb5110594ae45d0f04e60ad138c14ee1595298250193406e91d281f299dc38493e1668cb5ba8806da7429908d3a835eb59f99d9fd4b2bb736ce96aff288958429225b4898f1041e20df2326c0f38873f5c1faee1f9dc9bb11789d1938d657eab65844d42816267804839cdf850a9bd96ece2754b2c860c3918ccd5e458c3763a977771114906e9973e027e83cbfcea431e95e40dc71989587c69ab2fb15238b99bf59abee645785bbea8e916aff0a71bc3e5ac01fac251a938d08a75115058c2791b7cbe330741ced906067332a4f7522ceaa22388623637874008f53fb817f0a759459a7c76980fcf219b8ce0774e9cd83c42296387e6a16f1d36b6ad3b45d7b5f21e0ff3db87667a4668b8df70db920a595c9e84d994f8641446b42cd28b935210a3bb07e5c4d761ad27d9e0f82985f294299e493d7743a27954a27568c35623f9714950e88d44f46f5b018894580e9e4aa53198165f2b22c0578cc5ea26b4590665a2938d637215752cd9419c6e792b18e3c209b1e7bb7e853c27cc0ac4bde5a660e924853b5272ee3625283248385286a55c7c4dce23e8ba21335f6ae20c3b66a32438099ab3e2c908f38fa4f2d4b8ed
""")

p = ih("""
00c58125e91517431fe7cbbdab0b201a9c2d39d9112b27ab2e8d0715129d839261413076917aac66225e6256638843b10b7c4b79c38d9dce4b7ef04b9fae7df651b884f1a524cb9da4af083ecc350b45c19bccedf6f8cf06a362dfc4c214f85a4a3fcc5561851e783713ef79afc8126b8df769419195e304c094fec624157e1b7bbccafe8c627e37cbb210bdf50eeb4852293b2e4e1c7d1710237b9f60c206820b431f3ca983e30cdec56412657d14b478040753d4b861727ad63238a09cb756195995bf0bd68792b42666fd00ddbb82951d6b8a9e9024a68caad139295325389c75dd5a5da7605c110ddeadb79206cddc35a124c92483027b91d205ab47f8992b
""")

upper_q = ih("00a57d38a663751e483eae0d91f89a46e0e3abcfa86ee9370890fe44597e579377ec6b")
lower_q = ih("c91ba6f3713fa6527fc49ca202c4d1c1adebe100b12b917cab89c7dee9f7")

qInv_given = ih("""
6c9005d23c5e5bc8da1f860613623d68080cb8acb717019f485713bb5747f6647e980f161cbbf5457a237597df6d27b60af99fdb6ae52d29ce496bd9e677408b073e553b07aa25ad0d70f3d863a1c58a32f48fb5020972c52a5da0a51f0b159ec5d83c233ec4d2cab6d898d6e3a0344636e1d4113d0249151c797fc4aa79a4e28cf681aea2f602bb7dca6663ba83435bf68c1cc9d5df44fae9755fde9a266a22c879c163c9a04e849ce8dbea75043c9dd3e9b823e4127fe828c010949b91461f4eb37df48861497f6d91079d65ab7cfeaed7095ddeccdf4c8224262ac3688801e3822f872e230d5875ef56bfff70b60142b1f2a8783830d9d2398887a2d7d13b
""")

# ===== Reconstruct q via CRT =====
L = lower_n.bit_length()
mod2L = 1 << L

# q ≡ lower_n * p^{-1} (mod 2^L)
b = (lower_n * invmod(p % mod2L, mod2L)) % mod2L
# q ≡ (qInv_given)^{-1} (mod p)
a = invmod(qInv_given, p)

q = crt_two(a, p, b, mod2L)

# Optional checks (won't stop writing PEM if they fail)
try:
    assert (q & ((1 << lower_q.bit_length()) - 1)) == lower_q
    topU = q >> (q.bit_length() - upper_q.bit_length())
    assert topU == upper_q
    assert (p * q) % mod2L == lower_n
except AssertionError:
    pass

# Ensure usual ordering (some tools expect p > q)
if p < q:
    p, q = q, p

# Recompute qInv for the (p,q) in this order
qInv = invmod(q, p)
n = p * q
dp = d % (p - 1)
dq = d % (q - 1)

# Build PKCS#1 RSAPrivateKey DER
der = der_seq(
    der_int(0),   # version
    der_int(n),
    der_int(e),
    der_int(d),
    der_int(p),
    der_int(q),
    der_int(dp),
    der_int(dq),
    der_int(qInv)
)

pem_body = base64.encodebytes(der).decode().replace("\n", "")
wrapped = "\n".join(pem_body[i:i+64] for i in range(0, len(pem_body), 64))
pem_text = "-----BEGIN RSA PRIVATE KEY-----\n" + wrapped + "\n-----END RSA PRIVATE KEY-----\n"

out_path = sys.argv[1] if len(sys.argv) > 1 else "recovered_rsa_private_key.pem"
with open(out_path, "w") as f:
    f.write(pem_text)

print(f"[+] Wrote PEM → {out_path}")
print(f"[i] Modulus bits: {n.bit_length()}")

