

## Cryptohack - Forbidden attack

Zadanie polega na zdobyciu flagi poprzez wykorzystanie faktu że zdalny cel nie poprawnie implementuje szyfrowanie AES w trybie Galois Counter Mode (GCM) - każda wiadomość powinna być szyfrowana z wykorzystaniem innego `nonce`, jednak w przypadku zadania za każdym razem wykorzystywany jest ten sam `nonce`. Jednak w odróżnieniu od AES w trybie CTR, tutaj mamy do czynienia z szyfrowaniem uwierzytelniającym (AEAD) - zatem dla każdej wiadomości będzie generowany nowy tag uwierzytelniający $t$. Niemożliwe jest wysłanie wiadomości która zawiera słowo `flag`, przez co nie możemy bezpośrednio obliczyć tag uwierzytelniający, jednak z racji tego że `nonce` jest powtarzany możemy nadużyć wewnętrzne działanie trybu GCM.

Niech $h$ będzie kluczem uwierzytelniającym takim że:
1. $h \rightarrow Enc(K,0)$
Gdzie $K$ jest kluczem szyfrującym. Następnie padujemy zerami `AD` i szyfrogram `CT`.
2. $pad(AD,0x0) || pad(CT,0x0) \rightarrow a_0 || a_1 || c_0 || c_1 || c_2$
Podobnie dodajemy do powyższego równania  długości `AD` i `CT`
3. $a_0 || a_1 || c_0 || c_1 || c_2 || len(AD) || len(CT)$
Niech $g$ będzie kluczowanym hashem bloków wejśćiowych, generowanym w następujacy sposób:
4.
```
g := 0
    for b in bs:
         g := g + b
           g := g * h
```

GCM następnie bierze 96 bitowy `nonce` i tworzy secret `s`:
5. $s \rightarrow Enc(K, nonce || 1)$
Na koniec obliczany jest tag $t$
6. $t \rightarrow g + s$
W przypadku podanego wyżej szyfrogramu (o 3 blokach) wielomian generujący tag można opisać funkcją:

$f(x) = a_0x^6 + a_1x^5 + c_0x^4 + c_1x^3 + c_2x^2 + lenx + s$
Gdzie na wejściu podawany jest $x$ czyli klucz uwierzytelniający, zatem $t=f(h)$.

W przypadku ponownie używanego `nonce` rozważmy pewien przypadek, niech poprzednie wygenerowane $t=t_0$. Stwórzmy nowy szyfrogram $D$, tak że na wejściu algorytmu po dodaniu bloków $AD$ (w tym przypadku $b$) i odpowiednich długości otrzymujemy:

$b_0 || d_0 || d_1 || len(AD_B) || len(D)$

Czyli tag uwierzytelniający $t_1$ dla szyfrogramy $D$ wygląda tak:

$t_1=b_0h^4 + d_0h^3 + d_1h^2 + lenh + s_1$

Jeśli `nonce` $N$ wiadomości $C$ jest taki sam jak wiadomości $D$ to $s_0=s_1$, zatem po dodaniu tagów (XOR) $t_1$ i $t_2$ $s$ zredukuje się:

$t_0 \oplus t_1 = a_0h^6 + a_1h^5 + (c_0+b_0)h^4 + (c_1+d_0)h^3 + (c_2+d_1)h^2 + (len_1 + len_2)h$

Zatem $f(h)=0 \iff$ $h$ jest pierwiastkiem uwierzytelniającym i tej wartości potrzebujemy aby stworzyć wiarygodny tag uwietrzytelniający.

```python
"""
Task realized with SageMath Kernel
"""

from sage.all import * 
from Cryptodome.Util.number import long_to_bytes as lb
from Cryptodome.Util.number import bytes_to_long as bl
from binascii import unhexlify, hexlify
from sage.all import *
import struct
import requests
import json

def bytes_to_polynomial(block, a):
    polynomial = 0 
    bin_block = bin(bl(block))[2 :].zfill(128)
    for i in range(len(bin_block)):
        polynomial += a^i * int(bin_block[i])
    return polynomial

def polynomial_to_bytes(poly):
    return lb(int(bin(poly.integer_representation())[2:].zfill(128)[::-1], 2))

def convert_to_blocks(ciphertext):
    return [ciphertext[i:i + 16] for i in range(0 , len(ciphertext), 16)]

def xor(s1, s2):
    if(len(s1) == 1 and len(s1) == 1):
        return bytes([ord(s1) ^ ord(s2)])
    else:
        return bytes(x ^ y for x, y in zip(s1, s2))


def encrypt(plaintext) -> tuple:
    plaintext = (plaintext).hex()
    r = requests.get('http://aes.cryptohack.org/forbidden_fruit/encrypt/'+plaintext)
    data = json.loads(r.text)
    return data["ciphertext"], (data["tag"]), data["nonce"]

def encrypt_flag(plaintext) -> str:
    plaintext = (plaintext).hex()
    r = requests.get('http://aes.cryptohack.org/forbidden_fruit/encrypt/'+plaintext)
    data = json.loads(r.text)
    return data["ciphertext"]

def get_flag(nonce, ciphertext, tag, asso_data) -> str:
    flag = requests.get('http://aes.cryptohack.org/forbidden_fruit/decrypt/' +
                        nonce + '/' + ciphertext + '/' + tag + '/' + asso_data).json()['plaintext']
    return bytes.fromhex(flag).decode()

def construct_galois_field() -> tuple:
    return GF(2^128, name="a", modulus=x^128 + x^7 + x^2 + x + 1).objgen()

def construct_poly_ring(field):
    return PolynomialRing(field, name="x").objgen()

def ciphertext_to_polynomial(ciphertext):
    return [bytes_to_polynomial(ciphertext[i], a) for i in range(len(ciphertext))]

def construct_tag_poly(poly, var, length, tag):
    return (poly[0] * var^2) + (length * var) + tag

if __name__ == "__main__":
    

    F, a = construct_galois_field()
    R, x = construct_poly_ring(F)

    admin = b'give me the flag'
    PT1 = b'give me the dead'
    PT2 = b'give me the beaf'

    ciphertext = (encrypt_flag(admin))

    C = convert_to_blocks(bytes.fromhex(ciphertext))

    C1, T1, nonce = encrypt(PT1)
    C1 = convert_to_blocks(bytes.fromhex(C1))
    T1 = bytes.fromhex(T1)

    C2, T2, nonce = encrypt(PT2)
    C2 = convert_to_blocks(bytes.fromhex(C2))
    T2 = bytes.fromhex(T2)

    length = struct.pack(">QQ", 0 * 8, len(C1) * 8)

    C_polynomial = ciphertext_to_polynomial(C)
    C1_polynomial = ciphertext_to_polynomial(C1)
    C2_polynomial = ciphertext_to_polynomial(C2)
    
    T1_p = bytes_to_polynomial(T1, a)
    T2_p = bytes_to_polynomial(T2, a)
    
    L_p = bytes_to_polynomial(length, a)
    
    G_1 = construct_tag_poly(C1_polynomial, x, L_p, T1_p)
    G_2 = construct_tag_poly(C2_polynomial, x, L_p, T2_p)
    G_3 = construct_tag_poly(C_polynomial, x, L_p, 0)
    
    P = G_1 + G_2
    auth_keys = [r for r, _ in P.roots()]
    for H, _ in P.roots():
        EJ = G_1(H)
        T3 = G_3(H) + EJ
        T3 = str(polynomial_to_bytes(T3).hex())
        associated_data = "43727970746f4861636b"
        print(get_flag(nonce, ciphertext, T3, associated_data))
```



