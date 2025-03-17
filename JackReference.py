import re

class JackReference:
    def __init__(self):
        pass

    keywords = ["boolean", "char", "class", "constructor", "do", "else", "false", "field", "function", "if", "int", "let", "method", "null",
                "return", "static", "this", "true", "var", "void", "while"]
    symbols = ["{", "}", "(", ")", "[", "]", ";", ",", ".", "+", "-", "*", "/", "=", "<", ">", "|", "&", "~"]
    # get list of elements per line
    regexSymbols = "\\" + "|\\".join(symbols)
    regexPattern = re.compile(r'\w+|' + regexSymbols + '|".+"')