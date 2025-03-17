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
    
    def checkNextElement(self):
        elem = self.TokenFileItems[self.TokenIndex]
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
            elif (element.text.strip() in ["constructor", "function", "method"]):
                self.OutputXML.remove(nextElement)
                self.TokenIndex -= 1
                subroutineDec = ET.SubElement(self.OutputXML, "subroutineDec")
                self.CompileSubroutineDec(subroutineDec)
            elif (element.text.strip() in ["field", "static"]):
                self.OutputXML.remove(nextElement)
                self.TokenIndex -= 1
                classVarDec = ET.SubElement(self.OutputXML, "classVarDec")
                self.CompileVarDec(classVarDec, element)
                pass

    def CompileSubroutineDec(self, parentContainer):
        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            nextElement = ET.SubElement(parentContainer, element.tag)
            nextElement.text = element.text

            if (nextElement.text.strip() == "("):
                # compile parameter list
                parameterList = ET.SubElement(parentContainer, "parameterList")
                parameterList.text = "\n"
                if self.checkNextElement().text.strip() != ")":
                    self.CompileParameterList(parameterList)
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
                self.TokenIndex -= 1
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
        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            nextElement = ET.SubElement(parentContainer, element.tag)
            nextElement.text = element.text
            if (element.text.strip() == ";"):
                break

    def CompileParameterList(self, parentContainer):
        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            nextElement = ET.SubElement(parentContainer, element.tag)
            nextElement.text = element.text
            if self.checkNextElement().text.strip() == ")":
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
                # if the next statement is an else, we're still in the if statement
                if self.checkNextElement().text.strip() == "else":
                    pass
                else:
                    break
            elif keyword.text.strip() == "return" and not element.text.strip() in [JackReference.symbols]:
                # go back one because we found the beginning of an expression
                parentContainer.remove(nextElement)
                self.TokenIndex -= 1
                expression = ET.SubElement(parentContainer, "expression")
                self.CompileExpression(expression)
            elif keyword.text.strip() == "do" and element.text.strip() == "(":
                expressionList = ET.SubElement(parentContainer, "expressionList")
                self.CompileExpressionList(expressionList)
            elif element.text.strip() in ["=", "(", "["]:
                expression = ET.SubElement(parentContainer, "expression")
                self.CompileExpression(expression)
            elif element.text.strip() == "{":
                # if a left bracket occurs, we're in a statement that can have other statements
                # such as a while loop
                statements = ET.SubElement(parentContainer, "statements")
                statements.text = "\n"
                self.CompileStatements(statements)

    def CompileExpressionList(self, parentContainer):
        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            if element.text.strip() == ")":
                if len(parentContainer.findall("*")) == 0:
                    parentContainer.text = "\n"
                self.TokenIndex -= 1
                break
            self.TokenIndex -= 1
            expression = ET.SubElement(parentContainer, "expression")
            self.CompileExpression(expression)
            # if the expression has no elements, just take it out
            if len(expression.findall("*")) == 0:
                parentContainer.remove(expression)
                parentContainer.text = "\n"
            else:
                element = self.grabNextElement()
                if element.text.strip() == ")":
                    self.TokenIndex -= 1
                    break
                elif element.text.strip() == ",":
                    nextElement = ET.SubElement(parentContainer, element.tag)
                    nextElement.text = element.text


    def CompileExpression(self, parentContainer):
        tokenCount = 0
        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            tokenCount += 1

            if element.text.strip() in [";", ")", "]", ","]:
                self.TokenIndex -= 1
                break
            elif element.text.strip() in ["("] or (tokenCount == 1 and element.text.strip() in ["-", "~"]):
                # if the next element triggered a term, it belongs in the term
                self.TokenIndex -= 1
                term = ET.SubElement(parentContainer, "term")
                self.CompileTerm(term)
            elif element.text.strip() in JackReference.symbols:
                nextElement = ET.SubElement(parentContainer, element.tag)
                nextElement.text = element.text
            else:
                # if the next element triggered a term, it belongs in the term
                self.TokenIndex -= 1
                term = ET.SubElement(parentContainer, "term")
                self.CompileTerm(term)

    def CompileTerm(self, parentContainer):
        tokenCount = 0
        for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
            element = self.grabNextElement()
            tokenCount += 1

            # a closing parenthesis belongs outside of the current term
            if tokenCount > 1 and element.text.strip() in [";", ")", "]", "<", ">", "+", "-", "/", "*", ",", "|", "&", "="]:
                self.TokenIndex -= 1
                break

            nextElement = ET.SubElement(parentContainer, element.tag)
            nextElement.text = element.text

            # a term for a unary op (-, ~) is represented as symbol -> term
            # Ex: (-j)
            if (tokenCount <= 1 and element.text.strip() in ["-", "~"]):
                anotherTerm = ET.SubElement(parentContainer, "term")
                self.CompileTerm(anotherTerm)

            if element.text.strip() in ["("]:
                isExpressionList = False
                elementsSearched = 0
                for itemIndex in range(self.TokenIndex, len(self.TokenFileItems)):
                    lookAheadElement = self.grabNextElement()
                    elementsSearched += 1
                    if lookAheadElement.text.strip() == "," or (elementsSearched <= 1 and lookAheadElement.text.strip() == ")"):
                        isExpressionList = True
                        self.TokenIndex -= elementsSearched
                        break
                    elif lookAheadElement.text.strip() == ")":
                        self.TokenIndex -= elementsSearched
                        break

                if isExpressionList:
                    expressionList = ET.SubElement(parentContainer, "expressionList")
                    self.CompileExpressionList(expressionList)
                    # the inevitable closing parenthesis
                    element = self.grabNextElement()
                    nextElement = ET.SubElement(parentContainer, element.tag)
                    nextElement.text = element.text
                    continue

            if element.text.strip() in ["[", "("]:
                expression = ET.SubElement(parentContainer, "expression")
                self.CompileExpression(expression)
                # the inevitable closing bracket
                element = self.grabNextElement()
                nextElement = ET.SubElement(parentContainer, element.tag)
                nextElement.text = element.text
