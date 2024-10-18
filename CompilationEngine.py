# Written in Python 3.10.12. Python 3.8+ needed at minimum to use pathlib.Path().unlink with missing_ok
import pathlib
import re
import xml.etree.ElementTree as ET

from JackReference import JackReference

class CompilationEngine:

    def grabNextElement(self):
        elem = self.TokenFileItems[self.TokenIndex]
        self.TokenIndex += 1
        return elem

    def __init__(self, tokenFile):
        tree = ET.parse(tokenFile)
        self.TokenFileItems = list(tree.iter())
        self.TokenIndex = 0

        firstToken = self.grabNextElement()
        if firstToken.tag != "tokens":
            raise Exception("Tokenized XML is improperly formatted. First tag is not <tokens>")

        self.OutputXML = None

    def CompileClass(self):
        self.OutputXML = ET.Element("class")

        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            nextElement = ET.SubElement(self.OutputXML, element.tag)
            nextElement.text = element.text
            if (element.text.strip() == "}"):
                break
            elif (element.text.strip() == "{"):
                subroutineDec = ET.SubElement(self.OutputXML, "subroutineDec")
                self.CompileSubroutineDec(subroutineDec)
            elif (element.text.strip() in ["static"]):
                classVarDec = ET.SubElement(self.OutputXML, "classVarDec")
                pass

        print(element.tag)
        print(element.text)

    def CompileSubroutineDec(self, parentContainer):
        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            nextElement = ET.SubElement(parentContainer, element.tag)
            nextElement.text = element.text

            if (nextElement.text.strip() == "("):
                # compile parameter list
                parameterList = ET.SubElement(parentContainer, "parameterList")
                parameterList.text = "\n"
            elif (nextElement.text.strip() == ")"):
                break

        subroutineBody = ET.SubElement(parentContainer, "subroutineBody")
        self.CompileSubroutineBody(subroutineBody)

    def CompileSubroutineBody(self, parentContainer):
        element = self.grabNextElement()
        leftBracket = ET.SubElement(parentContainer, element.tag)
        leftBracket.text = element.text

        #for i, tokenItem in enumerate(self.TokenFileItems):
        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            if (element.text.strip() == "var"):
                varDec = ET.SubElement(parentContainer, "varDec")
                self.CompileVarDec(varDec, element)
            elif (element.text.strip() == "}"):
                rightBracket = ET.SubElement(parentContainer, element.tag)
                rightBracket.text = element.text
                break
            else:
                statements = ET.SubElement(parentContainer, "statements")
                self.CompileStatements(statements)

    def CompileVarDec(self, parentContainer, firstKeyword):
        keywordVar = ET.SubElement(parentContainer, firstKeyword.tag)
        keywordVar.text = firstKeyword.text

        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            nextElement = ET.SubElement(parentContainer, element.tag)
            nextElement.text = element.text
            if (element.text.strip() == ";"):
                break

    def CompileStatements(self, parentContainer):
        # not passing the first keyword for statements so make sure to rewind first
        self.TokenIndex -= 1
        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            if element.text.strip() == "return":
                returnStatement = ET.SubElement(parentContainer, "returnStatement")
                self.CompileStatement(returnStatement, element)
                break
            elif element.text.strip() == "let":
                letStatement = ET.SubElement(parentContainer, "letStatement")
                self.CompileStatement(letStatement, element)
            elif element.text.strip() == "if":
                ifStatement = ET.SubElement(parentContainer, "ifStatement")
                self.CompileStatement(ifStatement, element)
            elif element.text.strip() == "while":
                whileStatement = ET.SubElement(parentContainer, "whileStatement")
                self.CompileStatement(whileStatement, element)
            elif element.text.strip() == "do":
                doStatement = ET.SubElement(parentContainer, "doStatement")
                self.CompileStatement(doStatement, element)
            elif element.text.strip() == "}":
                self.TokenIndex -= 1
                break

    def CompileStatement(self, parentContainer, firstKeyword):
        keyword = ET.SubElement(parentContainer, firstKeyword.tag)
        keyword.text = firstKeyword.text

        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            nextElement = ET.SubElement(parentContainer, element.tag)
            nextElement.text = element.text
            if element.text.strip() in [";", "}"]:
                break
            elif keyword.text.strip() == "do" and element.text.strip() == "(":
                expressionList = ET.SubElement(parentContainer, "expressionList")
                expression = ET.SubElement(expressionList, "expression")
                self.CompileExpression(expression)
                # if the expression has no elements, just take it out
                if len(expression.findall("*")) == 0:
                    expressionList.remove(expression)
                    expressionList.text = "\n"
            elif element.text.strip() in ["=", "(", "["]:
                expression = ET.SubElement(parentContainer, "expression")
                self.CompileExpression(expression)
            elif element.text.strip() == "{":
                # if a left bracket occurs, we're in a statement that can have other statements
                # such as a while loop
                statements = ET.SubElement(parentContainer, "statements")
                self.CompileStatements(statements)


    def CompileExpression(self, parentContainer):
        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()

            if element.text.strip() in [";", ")", "]"]:
                self.TokenIndex -= 1
                break
            elif element.text.strip() in JackReference.symbols:
                nextElement = ET.SubElement(parentContainer, element.tag)
                nextElement.text = element.text
            else:
                # if the next element triggered a term, it belongs in the term
                self.TokenIndex -= 1
                term = ET.SubElement(parentContainer, "term")
                self.CompileTerm(term)

    def CompileTerm(self, parentContainer):
        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()

            # a closing parenthesis belongs outside of the current term
            if element.text.strip() in [";", ")", "]", "<", "+", "/"]:
                self.TokenIndex -= 1
                break

            nextElement = ET.SubElement(parentContainer, element.tag)
            nextElement.text = element.text
            if element.text.strip() == "(":
                expressionList = ET.SubElement(parentContainer, "expressionList")
                expression = ET.SubElement(expressionList, "expression")
                self.CompileExpression(expression)
                # the inevitable closing parenthesis
                element = self.grabNextElement()
                nextElement = ET.SubElement(parentContainer, element.tag)
                nextElement.text = element.text
            elif element.text.strip() == "[":
                expression = ET.SubElement(parentContainer, "expression")
                self.CompileExpression(expression)
                # the inevitable closing bracket
                element = self.grabNextElement()
                nextElement = ET.SubElement(parentContainer, element.tag)
                nextElement.text = element.text
