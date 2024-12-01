import math

BYTE_LEN_DEFAULT = 7
BYTE_LEN = BYTE_LEN_DEFAULT

def tolendividablebyBYTE_LEN(binary):
    return binary.zfill(math.ceil(len(binary)/BYTE_LEN)*BYTE_LEN)

def ceillog2(num):
    num = math.ceil(math.log2(num))
    if num == 0:
        return 1
    return num

def tobin(inpt, minimumlenght = None):
    if type(minimumlenght) == int:
        value = str(bin(int(inpt)))[2:].zfill(minimumlenght)
    else:
        value = str(bin(inpt))[2:]
    return value

def todec(inpt):
    return int("0b" + str(inpt),2)

def get_list_of_different_chars(text):
    return sorted(set(list(text)))

def integer(input_):
    number = input_.split(".")
    return int(number[0]) + int(number[1])/(10**(len(number[1])))

def get_app_version():
    return 1
    try:
        f = str(open("version.txt", "rb").read())
        version = integer(f[f.find("version:") + len("version:")  :  f.find(";")]) * 100
        return version
    except Exception:
        pass

def text_to_bin(text, use_min_len = BYTE_LEN):
    binary = ""
    if use_min_len:
        for i in range(len(text)):
            binary += tobin(ord(text[i]), minimumlenght=use_min_len)
        return binary
    for i in range(len(text)):
        binary += tobin(ord(text[i]))
    return binary

def text_to_bin_comprime(text:str, key:list[str], min_len) -> str:
    binary = ""
    for i in range(len(text)):
        binary += tobin(key.index(text[i]), minimumlenght=min_len)
    return binary

def force_text_from_binary(binary):
    text = ""
    for i in range(0, len(binary), BYTE_LEN):
        text += chr(todec(binary[i:i+BYTE_LEN]))
    return text

def compress(text, bytelen = None)->str:
    global BYTE_LEN_DEFAULT
    global BYTE_LEN
    if bytelen:
        BYTE_LEN = bytelen
    else:
        BYTE_LEN = BYTE_LEN_DEFAULT
    if not text:
        print("Not text given to comprime. Exiting function with empty string.")
        return ""
    different_chars_list = get_list_of_different_chars(text)
    len_of_comprimed_char = ceillog2(len(different_chars_list))
    chars_binary = text_to_bin("".join(different_chars_list))
    comprimed_text = text_to_bin_comprime(text, different_chars_list, len_of_comprimed_char)
    comprimed_text_offset = (math.ceil(len(comprimed_text)/BYTE_LEN)*BYTE_LEN) - len(comprimed_text)
    comprimed_text = tolendividablebyBYTE_LEN(comprimed_text)
    version = get_app_version()
    final_bin = tobin(version, minimumlenght=BYTE_LEN) + tobin(comprimed_text_offset, minimumlenght=BYTE_LEN) + tobin(len_of_comprimed_char, minimumlenght=BYTE_LEN)
    final_bin += tobin(len(different_chars_list), minimumlenght=BYTE_LEN)
    final_bin += chars_binary
    final_bin += comprimed_text
    final_text = force_text_from_binary(final_bin)
    if not "".join([tobin(ord(i),minimumlenght=BYTE_LEN) for i in list(final_text)]) == final_bin:
        exit("Error: final_text is not equal to final_bin")
    return final_text