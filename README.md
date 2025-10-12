
FRSA (No Hack No CTF)

At first glance this looks like an RSA challenge, but it’s actually a monoalphabetic substitution: the script encrypts each character independently as $$c=ord(ch)^e mod n$$ and writes the list of residues. Because characters are handled one by one, each plaintext symbol maps to a single fixed ciphertext value. In our instance the plaintext is upercased, so if you take the set of distinct ciphertext integers X, you get 27 symbols (space plus A–Z). The intended solve is frequency analysis: rank the ciphertext values by frequency and map them to the English order ' ETAOINSHRDLCUMWFGYPBVKJXQZ' (space is most frequent), hence the nickname FRSA (frequency RSA).
