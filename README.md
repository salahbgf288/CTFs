
FRSA (No Hack No CTF)

At first glance this looks like an RSA challenge, but it’s actually a monoalphabetic substitution: the script encrypts each character independently as $$c=ord(ch)^e$$ $mod$ $n$ and writes the list of residues. Because characters are handled one by one, each plaintext symbol maps to a single fixed ciphertext value. In our instance the plaintext is upercased, so if you take the set of distinct ciphertext integers X, you get 27 symbols (space plus A–Z). The intended solve is frequency analysis: rank the ciphertext values by frequency and map them to the English order ' ETAOINSHRDLCUMWFGYPBVKJXQZ' (space is most frequent), hence the nickname FRSA (frequency RSA).

This yields the following text:

AN WENEROU VHUTOARE IOAD TSAI ANODVERTENTUG O CEP CUAEI YATE O CEP TALEI NEVER MON DETOAN O SERHAM WOUUHKANW SHRIE TSAI IEELI TH LOBE O UHT HC IENIE RAWST TSE JFAMB YRHPN CHQ ZFLKI HVER TSE UOXG DHW DELHMRATFI HNME IOAD TSAI DHNT UHHB OT EVERGHNE PATS DAITRFIT YFT YE CARL OND CARL TSAI AI ANDEED O PAIE IOGANW TSEN PSOT YOWESHT HNME IOAD O CARL YEUAEC MON LOBE TSE SEORT HC TSE ITRHNW CARL OND TSEG ORE LHRE DETERLANED OUTSHFWS TSAI IENTENME AI ISHRT AT LOBEI LE TSANB OYHFT AT PSG DHEI NSNMTSAIAIRIOONDCREJFENMGONOUGIAI SOKKEN

This still isn’t the intended plaintext. Because the sample isn’t long enough, a simple frequency-based mapping (space + 26 letters) doesn’t converge perfectly, so some letters remain misassigned. To finish the solve, try a monoalphabetic-substitution helper:

dCode Monoalphabetic Substitution: https://www.dcode.fr/substitution-monoalphabetique

quipqiup: https://quipqiup.com/
<img width="788" height="588" alt="FRSA" src="https://github.com/user-attachments/assets/e1491b04-6cdb-4003-8062-0c45a4770e30" />

We see that we obtained the wanted plaintext: 
IN GENERAL VOLTAIRE SAID THIS INADVERTENTLY A FEW FLIES BITE A FEW TIMES NEVER CAN DETAIN A HEROIC GALLOPING HORSE THIS SEEMS TO MAKE A LOT OF SENSE RIGHT THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG DEMOCRITUS ONCE SAID THIS DONT LOOK AT EVERYONE WITH DISTRUST BUT BE FIRM AND FIRM THIS IS INDEED A WISE SAYING THEN WHAT BAGEHOT ONCE SAID A FIRM BELIEF CAN MAKE THE HEART OF THE STRONG FIRM AND THEY ARE MORE DETERMINED ALTHOUGH THIS SENTENCE IS SHORT IT MAKES ME THINK ABOUT IT WHY DOES NHNCTHISISRSAANDFREQUENCYANALYSIS HAPPEN

Flag : NHNC{THIS_IS_RSA_AND_FREQUENCY_ANALYSIS}


