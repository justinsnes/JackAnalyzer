# Written in Python 3.10.12. Python 3.8+ needed at minimum to use pathlib.Path().unlink with missing_ok
import pathlib
import re
import xml.etree.ElementTree as ET

from JackReference import JackReference

class JackTokenizer:

    def tokenizeFile(targetJackFile):
        tokenizedFile = targetJackFile.replace(".jack", "T_output.xml")
        # unlink and overwrite any existing file rather than append to it
        pathlib.Path(tokenizedFile).unlink(missing_ok=True)

        tokens = ET.Element('tokens')

        with open(targetJackFile) as file:
            for line in file:
                if line.startswith("//") or line.startswith("/*") or not line.strip():
                    continue
                if line.find("//") > -1:
                    line = line.partition("//")[0]

                for element in re.findall(JackReference.regexPattern, line):
                    element = element.replace("\n", "")
                    if element == "":
                        continue

                    category = "identifier"
                    if (element[0] == '"'):
                        category = "stringConstant"
                    elif (element.replace('-', '', 1).isdigit()):
                        # replace only one - and test if everything is are digits. most performant way of checking
                        category = "integerConstant"
                    elif (element in JackReference.keywords):
                        category = "keyword"
                    elif (element in JackReference.symbols):
                        category = "symbol"
                    wordElement = ET.SubElement(tokens, category)
                    wordElement.text = " " + element.replace('"', '') + " "

            tree = ET.ElementTree(tokens)
            ET.indent(tree, '')
            tree.write(tokenizedFile)

        return tokenizedFile
