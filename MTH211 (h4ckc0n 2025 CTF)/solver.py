#!/usr/bin/env python3
"""
Usage:
    python solver.py

Options:
    --mem use in-memory dict (faster, higher RAM)
    --disk use sqlite on-disk table (safer for low-RAM machines)

You must edit the constants below (n, gift, cipher) to match the values printed by the challenge.
"""

from math import isqrt
import sys
import argparse
import time
import sqlite3


n=10192317563100435820324883212732654109601026477813807473477878848573139071076450236118688980932037415251346520514542138140609060252895351951720245780911857
gift=9849116110348955789479010194217500434924628821283154420120653296317850482069813955763227679617407203690983933060408814831540731516918111919543171982943742
cipher=5233505605717906572820704125698007884756899600546277154250677229608622104923213916257278306210268480306253062577662108243267456434157595354492257249291619
g=79311846630906367242578569989060951934653320046283047846150092277845194835891


# prime-range for 28-bit primes (change if different)
LOW = 1 << 27 # inclusive
HIGH = 1 << 28 # exclusive

EXP = 13

# implementation details
def small_primes_upto(n):
    """Return list of primes up to n (inclusive) with standard sieve."""
    sieve = bytearray(b"\x01") * (n+1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, isqrt(n)+1):
        if sieve[p]:
            step = p
            start = p*p
            sieve[start:n+1:step] = b"\x00" * (((n - start)//step) + 1)
    return [i for i, v in enumerate(sieve) if v]

def segmented_primes(L, R):
    """Yield primes in interval [L, R). Uses segmented sieve."""
    assert L >= 2 and R > L
    limit = isqrt(R) + 1
    base_primes = small_primes_upto(limit)
    segment_size = R - L
    segment = bytearray(b"\x01") * segment_size
    for p in base_primes:
        start = ((L + p - 1) // p) * p
        if start < p*p:
            start = p*p
        for j in range(start, R, p):
            segment[j - L] = 0
    for i in range(segment_size):
        if segment[i]:
            val = L + i
            if val >= 2:
                yield val

def gen_28bit_primes():
    """Return list of primes in [2**27, 2**28)."""
    return list(segmented_primes(LOW, HIGH))

def run_mem_mode(primes, n, gift):
    """Meet-in-the-middle using in-memory dict."""
    t0 = time.time()
    table = {}
    count = 0
    total = len(primes)
    print(f"[mem] computing p^13 mod n for {total} primes...")
    for p in primes:
        v = pow(p, EXP, n)
        # store first prime that gives v, collisions extremely unlikely but keep list if needed
        if v not in table:
            table[v] = p
        count += 1
        if count % 200000 == 0:
            print(f" processed {count}/{total} primes...")
    print(f"[mem] precompute done in {time.time()-t0:.1f}s, entries: {len(table)}")

    print("[mem] scanning for match with q by computing target = gift * inv(q^13) ...")
    t0 = time.time()
    count = 0
    for q in primes:
        w = pow(q, EXP, n)
        try:
            w_inv = pow(w, -1, n)
        except ValueError:
            # w not invertible mod n (rare), skip
            continue
        target = (gift * w_inv) % n
        if target in table:
            p = table[target]
            print("FOUND match!")
            return p, q
        count += 1
        if count % 200000 == 0:
            print(f" checked {count}/{total} primes...")
    print(f"[mem] scan finished in {time.time()-t0:.1f}s - no match found")
    return None, None

def run_disk_mode(primes, n, gift, dbname="mitm.db"):
    """Meet-in-the-middle using sqlite on-disk mapping value->prime."""
    # remove file if exists
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute("PRAGMA synchronous = OFF")
    cur.execute("PRAGMA journal_mode = MEMORY")
    cur.execute("DROP TABLE IF EXISTS mapping")
    cur.execute("CREATE TABLE mapping(val TEXT PRIMARY KEY, p INT)")
    conn.commit()

    print("[disk] inserting p^13 mod n into sqlite table (this will take some time)...")
    t0 = time.time()
    inserted = 0
    for p in primes:
        v = pow(p, EXP, n)
        cur.execute("INSERT OR IGNORE INTO mapping(val,p) VALUES(?,?)", (format(v, "x"), p))
        inserted += 1
        if inserted % 200000 == 0:
            conn.commit()
            print(f" inserted {inserted}/{len(primes)} primes...")
    conn.commit()
    print(f"[disk] insertion done in {time.time()-t0:.1f}s; rows = {inserted}")

    print("[disk] scanning q values and querying sqlite for match")
    t0 = time.time()
    checked = 0
    for q in primes:
        w = pow(q, EXP, n)
        try:
            w_inv = pow(w, -1, n)
        except ValueError:
            continue
        target = (gift * w_inv) % n
        hex_target = format(target, "x")
        cur.execute("SELECT p FROM mapping WHERE val = ?", (hex_target,))
        row = cur.fetchone()
        if row:
            return row[0], q
        checked += 1
        if checked % 200000 == 0:
            print(f" checked {checked}/{len(primes)} primes...")
    print(f"[disk] scan finished in {time.time()-t0:.1f}s - no match found")
    return None, None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("mem","disk"), default="disk", help="mem (fast) or disk (sqlite) mode")
    args = parser.parse_args()

    print("Generating 28-bit primes in range [2**27,2**28)...")
    t0 = time.time()
    primes = gen_28bit_primes()
    print(f"Generated {len(primes)} primes in {time.time()-t0:.1f}s")

    if args.mode == "mem":
        p, q = run_mem_mode(primes, n, gift)
    else:
        p, q = run_disk_mode(primes, n, gift)

    if p is None:
        print("No factors p1,p2 found. Try switching mode, or ensure constants are correct.")
        return

    K = p * q
    print("Recovered p1:", p)
    print("Recovered p2:", q)
    print("Recovered K:", K)
    # Verify
    print("Verifying pow(K,13,n) == gift ...")
    if pow(K, EXP, n) == gift % n:
        print("Verification OK.")
    else:
        print("Verification FAILED (unexpected).")

    # Now decrypt the cipher: as discussed, the decryption exponent is K
    print("Decrypting cipher with exponent K: m = pow(cipher, K, n) ...")
    K*=g
    m = pow(cipher, K, n)
    # convert to bytes
    try:
        # try to convert to bytes with exact length
        m_bytes = m.to_bytes((m.bit_length()+7)//8, "big")
        print("Recovered plaintext bytes (raw):", m_bytes)
        try:
            print("Recovered plaintext (utf-8):")
            print(m_bytes.decode())
        except:
            print("Could not decode as UTF-8. Hex:")
            print(m_bytes.hex())
    except Exception as e:
        print("Error converting m to bytes:", e)

if __name__ == "__main__":
    main()
