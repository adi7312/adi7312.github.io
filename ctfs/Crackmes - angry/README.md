**Objective:** Write key generator.

## Reversing `main()` with Ghidra and r2

To obtain final flag we need to provide password that meets folowing requirements:

```
password[0] + password[1] = 0xa6
password[3] ^ password[5] = 0x50
password[2] + password[6] = 0xd7
password[4] / password[7] = 0x01
password[4] * password[11] = 0x3c0f
password[8] -  password[2] = 0x09
password[9] + password[3] = 0x97
password[10] & password[11] = 0x64
password[0] + password[11] = 0xf3
password[1] + password[10] = 0x94
password[9] % password[2] = 0x33 
password[3] ^ password[8] = 0x16
password[4] | password[7] = 0x7f
password[5] + password[6] = 0xa2
```

```c
int main(void)

{
  size_t len;
  long in_FS_OFFSET;
  undefined8 password;
  byte local_30;
  char cStack_2f;
  byte bStack_2e;
  byte bStack_2d;
  undefined2 uStack_2c;
  undefined2 uStack_2a;
  undefined6 uStack_28;
  undefined8 local_22;
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  password = 0;
  local_30 = 0;
  cStack_2f = '\0';
  bStack_2e = 0;
  bStack_2d = 0;
  uStack_2c = 0;
  uStack_2a = 0;
  uStack_28 = 0;
  local_22 = 0;
  __isoc99_scanf(&DAT_00102004,&password);
  len = strlen((char *)&password);
  if (((((len == 0xc) && ((int)password[1] + (int)(char)password[0] == 0xa6)) &&
       ((password[3] ^ password.[5]) == 0x50)) &&
      ((((int)password[6] + (int)password[2] == 0xd7 &&
        ((int)(char)password[4] / (int)(char)password[7] == 1)) &&
       (((int)(char)password[4] * (int)(char)password[5] == 0x3c0f &&
        (((int)(char)local_30 - (int)password[2]== 9 &&
         ((int)(char)password[3] + (int)(char)password[9] == 0x97)))))))) &&
     (((password[10] & password[11]) == 100 &&
      ((((((int)(char)password + (int)(char)password[11] == 0xf3 &&
          ((int)password[1] + (int)(char)password[10] == 0x94)) &&
         ((int)cStack_2f % (int)password[2] == 0x33)) &&
        (((password[3] ^ local_30) == 0x16 && ((password[4] | password[7]) == 0x7f)))) &&
       ((int)(char)password[5] + (int)password[6] == 0xa2)))))) {
    printf("%s is a valid flag!",&password);
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
}
```

## **Building password**

```python
import itertools
from z3 import *

# I have no fucking idea what is going on here, I stole that from someone else
# https://stackoverflow.com/questions/11867611/z3py-checking-all-solutions-for-equation
def models(formula, max = 100):  
    
    solver = Solver()
    solver.add(formula)
    count = 0
    while count < max:
        count +=1
        if solver.check() == sat:
            model = solver.model()
            yield model
            block = []
            for z3_decl in model:
                arg_domains = []
                for i in range(z3_decl.arity()):
                    domain, arg_domain = z3_decl.domain(i), []
                    for j in range(domain.num_constructors()):
                        arg_domain.append( domain.constructor(j) () )
                    arg_domains.append(arg_domain)
                for args in itertools.product(*arg_domains):
                    block.append(z3_decl(*args) != model.eval(z3_decl(*args)))
            solver.add(Or(block))

password = []
requirements = []

for i in range(12):
    password.append(BitVec(f"password_{str(i).zfill(2)}", 8))
    requirements += [ password[i] >= 0x21, password[i] <= 0x7e ] # we are interested only in printable ascii characters

requirements += [password[0] + password[1]   == 0xa6,
      password[3] ^ password[5]   == 0x50,
      password[2] + password[6]   == 0xd7,
      password[4] / password[7]   == 0x01,
      password[4] * password[11]  == 0x3c0f,
      password[8] - password[2]   == 0x09,
      password[9] + password[3]   == 0x97,
      password[11] & password[10] == 0x64,
      password[0] + password[11]  == 0xf3,
      password[1] + password[10]  == 0x94,
      password[9] % password[2]   == 0x33,
      password[3] ^ password[8]   == 0x16,
      password[4] | password[7]   == 0x7f,
      password[5] + password[6]   == 0xa2 ]

for m in models(requirements):
    m_dict = {d.name():m[d].as_long() for d in m}
    print(''.join([chr(m_dict[k]) for k in sorted(m_dict.keys())]))
```

Output:

```
v0id{4n?r3d}
v0id{4n_r3d}
v0id{4nWr3d}
v0id{4nGr3d}
v0id{4nFr3d}
v0id{4nfr3d}
v0id{4nvr3d}
v0id{4nwr3d}
v0id{4ngr3d}
v0id{4ner3d}
v0id{4ndr3d}
v0id{4ntr3d}
v0id{4nur3d}
v0id{4nEr3d}
v0id{4nMr3d}
v0id{4nOr3d}
v0id{4nNr3d}
v0id{4nnr3d}
v0id{4nlr3d}
v0id{4nDr3d}
v0id{4nTr3d}
v0id{4nLr3d}
v0id{4n\r3d}
v0id{4n]r3d}
v0id{4nmr3d}
v0id{4nor3d}
v0id{4n>r3d}
v0id{4n^r3d}
v0id{4nVr3d}
v0id{4nUr3d}
```

Final result:
```
⚡ root  ./a.out
v0id{4nUr3d}
v0id{4nUr3d} is a valid flag!#
```
