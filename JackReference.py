import re

class JackReference:
    def __init__(self):
        pass

    keywords = ["boolean", "class", "do", "else", "function", "if", "int", "let", "return", "static", "var", "void", "while"]
    symbols = ["{", "}", "(", ")", "[", "]", ";", ",", ".", "+", "-", "/", "=", "<", ">"]
    # get list of elements per line
    regexSymbols = "\\" + "|\\".join(symbols)
    regexPattern = re.compile(r'\w+|' + regexSymbols + '|".+"')