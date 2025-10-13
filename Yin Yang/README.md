# ☯️ Yin & Yang — Balance in Chaos

<img width="740" height="740" alt="Yin_Yang" src="https://github.com/user-attachments/assets/cf5a0118-8b64-4de8-8cb2-c3cf0bdbaf90" />

From ancient philosophy to modern thought, **Yin and Yang** represent balance, duality, and the harmony of opposites.  
This image hides a **secret** that embodies these very principles.  
Can you find **balance in chaos**?

---

## 🧩 Extracting the Hidden Data

From the image, we can extract two lists:

```python
yin  = [188, 125, 135, 65, 97, 24, 39, 210, 40, 181, 215, 126, 200, 223, 231, 91, 38, 207, 165, 117, 149, 157, 126]
yang = [219,  15, 232, 37, 15, 119, 92, 230, 28, 141, 229, 74, 240, 239, 212, 105, 21, 253, 149, 71, 166, 165,   3]
```

---

## ⚙️ First Step — XOR the Two Sides

In the spirit of Yin and Yang, we **combine** the two lists by applying the **XOR** operation:

```python
result = [a ^ b for a, b in zip(yin, yang)]
print(result)
```

Output:

```
[103, 114, 111, 100, 110, 111, 123, 52, 52, 56, 50, 52, 56, 48, 51, 50, 51, 50, 48, 50, 51, 56, 125]
```

---

## 🔍 Decoding the Message

Converting these ASCII values gives us:

```
grodno{448248032320238}
```

---

## 🏁 Flag

```
grodno{448248032320238}
```

---

### 💡 Insight

The puzzle highlights the **balance of opposites** — by combining Yin and Yang through XOR (a perfect digital analogy of duality), the hidden truth reveals itself.
