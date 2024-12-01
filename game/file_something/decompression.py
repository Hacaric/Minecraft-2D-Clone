BYTE_LEN_DEFAULT = 7
BYTE_LEN = BYTE_LEN_DEFAULT

def tobin(inpt, minimumlenght=None):
    if minimumlenght:
        return str(bin(int(inpt)))[2:].zfill(minimumlenght)
    return str(bin(inpt))[2:]

def todec(inpt):
    return int("0b" + str(inpt), 2)

def get_list_of_different_chars(text):
    return sorted(set(list(text)))

def integer(input_):
    number = input_.split(".")
    return int(number[0]) + int(number[1])/(10**(len(number[1])))

def get_app_version():
    return 1
    try:
        f = str(open("version.txt", "rb").read())
        version = integer(f[f.find("version:") + len("version:"):f.find(";")]) * 100
        return version
    except Exception as e:
        print("Error while reading app version(check version.txt): " + str(e))

def decode_by_pattern(text, bytelen = None):
    global BYTE_LEN_DEFAULT
    global BYTE_LEN
    if bytelen:
        BYTE_LEN = BYTE_LEN_DEFAULT
    version = todec(text[0:BYTE_LEN])/100
    if not version == get_app_version()/100:
        if not "y" == input(f"Your file's version({version}) is not the right. App version is {get_app_version()/100}. This can cause not right decompression of file. Try downloading older app version from github.\n\nDo you want to continue?(y/n) >> "):
            exit("Wrong version.")
    
    text_offset = todec(text[BYTE_LEN:BYTE_LEN*2])
    len_of_comprimed_char = todec(text[BYTE_LEN*2:BYTE_LEN*3])
    len_of_diff_char = todec(text[BYTE_LEN*3:BYTE_LEN*4])
    different_chars_list = []
    
    for i in range(BYTE_LEN*4, len_of_diff_char*BYTE_LEN + (4*BYTE_LEN), BYTE_LEN):
        different_chars_list.append(chr(todec(text[i:i + BYTE_LEN])))
    
    comprimed_text = text[len_of_diff_char*BYTE_LEN + (4*BYTE_LEN)+text_offset:]
    return len_of_comprimed_char, different_chars_list, comprimed_text

def decode(len_of_comprimed_char, comprimed_text, different_chars_list):
    text = ""
    for i in range(0, len(comprimed_text), len_of_comprimed_char):
        text += different_chars_list[todec(comprimed_text[i:i+len_of_comprimed_char])]
    return text

def decompress(text, bytelen = None) -> str:
    global BYTE_LEN_DEFAULT
    global BYTE_LEN
    if bytelen:
        BYTE_LEN = bytelen
    else:
        BYTE_LEN = BYTE_LEN_DEFAULT
    text = "".join([tobin(ord(i), minimumlenght=BYTE_LEN) for i in list(text)])
    len_of_comprimed_char, different_chars_list, comprimed_text = decode_by_pattern(text)
    decomprimed_text = decode(len_of_comprimed_char, comprimed_text, different_chars_list)
    
    return decomprimed_text