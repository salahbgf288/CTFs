
FRSA (No Hack No CTF)

At first glance this looks like an RSA challenge, but it’s actually a monoalphabetic substitution: the script encrypts each character independently as $$c=ord(ch)^e$$ $mod$ $n$ and writes the list of residues. Because characters are handled one by one, each plaintext symbol maps to a single fixed ciphertext value. In our instance the plaintext is upercased, so if you take the set of distinct ciphertext integers X, you get 27 symbols (space plus A–Z). The intended solve is frequency analysis: rank the ciphertext values by frequency and map them to the English order ' ETAOINSHRDLCUMWFGYPBVKJXQZ' (space is most frequent), hence the nickname FRSA (frequency RSA).

This yields the following text:

AN WENEROU VHUTOARE IOAD TSAI ANODVERTENTUG O CEP CUAEI YATE O CEP TALEI NEVER MON DETOAN O SERHAM WOUUHKANW SHRIE TSAI IEELI TH LOBE O UHT HC IENIE RAWST TSE JFAMB YRHPN CHQ ZFLKI HVER TSE UOXG DHW DELHMRATFI HNME IOAD TSAI DHNT UHHB OT EVERGHNE PATS DAITRFIT YFT YE CARL OND CARL TSAI AI ANDEED O PAIE IOGANW TSEN PSOT YOWESHT HNME IOAD O CARL YEUAEC MON LOBE TSE SEORT HC TSE ITRHNW CARL OND TSEG ORE LHRE DETERLANED OUTSHFWS TSAI IENTENME AI ISHRT AT LOBEI LE TSANB OYHFT AT PSG DHEI NSNMTSAIAIRIOONDCREJFENMGONOUGIAI SOKKEN

This still isn’t the intended plaintext. Because the sample isn’t long enough, a simple frequency-based mapping (space + 26 letters) doesn’t converge perfectly, so some letters remain misassigned. To finish the solve, try a monoalphabetic-substitution helper:

dCode Monoalphabetic Substitution: https://www.dcode.fr/substitution-monoalphabetique

quipqiup: https://quipqiup.com/
<img width="788" height="588" alt="FRSA" src="https://github.com/user-attachments/assets/e1491b04-6cdb-4003-8062-0c45a4770e30" />


