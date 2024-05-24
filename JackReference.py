import re

class JackReference:
    def __init__(self):
        pass

    keywords = ["class", "do", "function", "int", "let", "return", "var", "void", "while"]
    symbols = ["{", "}", "(", ")", "[", "]", ";", ",", ".", "+", "-", "/", "=", "<", ">"]
    # get list of elements per line
    regexSymbols = "\\" + "|\\".join(symbols)
    regexPattern = re.compile(r'\w+|' + regexSymbols + '|".+"')