# **Crackmes.one - P@ssw0rd**

## **Reversing and uderstanding code**

I used Ghidra to decompile this program. We have 2 interesting functions: `main()` and `encrypt()`. 

### **`main()`**
1. Program initizalizes some hardcoded variables and creates space for user input. Program also checks if is being deubgged. However this type of antidebugging protection is quite simple to evade, but we will not deal with it in this task.
2. Password provided by user is encrypted in custom `encrypt` function. For more info look at [encrypt](#encrypt) section.
3. Now encrypted value is compared with hardcoded values (local_48/40/38/20/28). So if valid password is provided, we will get desired output.

```c
undefined8 main(void)

{
  long isDebugged;
  undefined8 exit_code;
  int __edflag;
  char user_input [48];
  undefined8 local_48;
  undefined8 local_40;
  undefined8 local_38;
  undefined8 local_30;
  undefined8 local_28;
  int local_14;
  char *encrypted_data;
  
  isDebugged = ptrace(PTRACE_TRACEME,0,1,0);
  if (isDebugged == 0) {
    local_48 = 0x3a275e3d713c4a39;
    local_40 = 0x2b233a642a232a68;
    local_38 = 0x2b272329392a684a;
    local_30 = 0x734227293e23;
    local_28 = 0;
    printf("Enter a Password: ");
    __edflag = (int)local_78;
    __isoc99_scanf(&DAT_00102029);
    encrypt(local_78,__edflag);
    encrypted_data = local_78;
    local_14 = strcmp(encrypted_data,(char *)&local_48);
    if (isValid == 0) {
      printf("Congrats, Access Granted!!");
    }
    else {
      printf("Try Harder and Debug More!");
    }
    exit_code = 0;
  }
  else {
    puts("Debugger Detected");
    exit_code = 1;
  }
  return exit_code;
}
```

### **`encrypt()`**

Encrypting is quite simple, every character is added with constant value -10.

```c
void encrypt(char *__block,int __edflag)

{
  size_t len;
  int index;
  
  index = 0;
  while( true ) {
    len = strlen(__block);
    if (len <= (ulong)(long)index) break;
    __block[index] = __block[index] + -10;
    index = index + 1;
  }
  return;
}
```

## **Writing decrypt function**

Since we know hardocded values, we can write simple `decrypt()` function in C. `encrypted[]` is array of hardcoded values written in little-endian format. Remember to subtract 1 from length, it is really import because we need to exclude null terminator, otherwise undefined behaviour will occur.

```c
#include <stdio.h>


void decrypt(char* const encryptedData, size_t length){
    for (int i = 0; i < length ;i++){
        encryptedData[i] = encryptedData[i] + 10;
    }
}

int main(int argc, char const *argv[])
{
    char encrypted[] = "\x39\x4a\x3c\x71\x3d\x5e\x27\x3a\x68\x2a\x23\x2a\x64\x3a\x23\x2b\x4a\x68\x2a\x39\x29\x23\x27\x2b\x23\x3e\x29\x27\x42\x73";
    size_t length = sizeof(encrypted) - 1;
    decrypt(encrypted,length);
    printf("%s",encrypted);
    return 0;
}
```
Output:
```
CTF{Gh1Dr4-4nD-5Tr4C3-15-H31L}
```
Passing above value gives us final flag:
```
⚡root ./P@ssw0rd
Enter a Password: CTF{Gh1Dr4-4nD-5Tr4C3-15-H31L}
Congrats, Access Granted!!#
```