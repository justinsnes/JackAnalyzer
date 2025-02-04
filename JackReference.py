import re

class JackReference:
    def __init__(self):
        pass

    keywords = ["boolean", "char", "class", "constructor", "do", "else", "field", "function", "if", "int", "let", "method", "return", "static",
                "this", "var", "void", "while"]
    symbols = ["{", "}", "(", ")", "[", "]", ";", ",", ".", "+", "-", "/", "=", "<", ">"]
    # get list of elements per line
    regexSymbols = "\\" + "|\\".join(symbols)
    regexPattern = re.compile(r'\w+|' + regexSymbols + '|".+"')