# Substitution (Mono-alphabetic) – Writeup

## Challenge summary
We’re given a long numeric string and told it’s a **substitution cipher**.
Instead of letters being substituted by other letters directly, the ciphertext is made of **2-digit tokens** (bigrams like `27`, `55`, `58`, …). Each distinct token represents one symbol from:

```
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

So the task is:
1) split ciphertext into pairs of digits  
2) build a token dictionary (unique tokens)  
3) map each token to a character by index in the discovered token list

This is a **monoalphabetic substitution**, where the “alphabet” is the set of unique 2-digit tokens.

---

## Given data

### Ciphertext
```text
275558725655565081534711472750815594535872535647588653475004564772551183114772860250860203944758944758860311474794564754475894478117031194472747721755112850817227024711834702508153274754471172564772115047565647725453274772035056479447811772724781835647815511860247112703508647814758944950727950555602475011472747721711478153471172175572275049035011795053114758555394475886031147720247565681559447726036035052180394525394525847049452945381475264535656528347520255112708
```

### Alphabet
```text
ABCDEFGHIJKLMNOPQRSTUVWXYZ_
```

---

## Key observation
If you scan the ciphertext two digits at a time, you’ll notice there are **exactly 27 unique tokens**.

That matches the size of the alphabet:
- 26 letters `A-Z`
- plus underscore `_`

So each distinct 2-digit token corresponds to exactly one of those 27 symbols.

---

## Solution approach
We collect unique 2-digit tokens **in first-seen order** into a list `L`.
Then each token maps to a character using its index:

- token `L[0]` → `A`
- token `L[1]` → `B`
- …
- token `L[26]` → `_`

This works because the cipher is monoalphabetic: **one token → one symbol**.

---

## Solver

Run:
```bash
python3 solve.py
```

It prints:
- the discovered token list `L` and its length (should be 27)
- the raw decoded stream (underscores instead of spaces)

---

## Decryption output (final)
Using the decoded substitution and then letting **dCode.fr / Substitution mono-alphabétique** refine spacing (as seen in the screenshot), we recover a readable French plaintext and the embedded flag:

```text
DANS LA LUMIERE DU MATIN SILENCIEUX LES ARBRES CHUCHOTENT ENCORE
ET LE VENT EMPORTE DES PARFUMS D HERBE HUMIDE
VERS LES RUELLES VIDES OU LE TEMPS SEMBLE MARCHER
DOUCEMENT JUSQU A L HEURE DES PREMIERS PAS DU JOUR
QUI RENAIT ENCORE

SHELLMATES{YOU_GOT_IT_NEXT_TIME_WILL_BE_HARD}
```

✅ **Flag**
```text
SHELLMATES{YOU_GOT_IT_NEXT_TIME_WILL_BE_HARD}
```

---

## Notes / pitfalls
- The ordering of tokens in `L` matters (first appearance defines the mapping).
- If you rebuild `L` in a different order (sorted, etc.), you’ll get garbage.
