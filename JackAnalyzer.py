# Written in Python 3.10.12. Python 3.8+ needed at minimum to use pathlib.Path().unlink with missing_ok
import argparse
import os
import xml.etree.ElementTree as ET

from JackTokenizer import JackTokenizer

parser = argparse.ArgumentParser("JackAnalyzer")
parser.add_argument("jackfilepath", help="The target Jack file/directory to be translated to xml tokens and parsing", type=str)
args = parser.parse_args()
# expanduser translates ~ to the exact path it represents. needed on Windows
targetFilepath = os.path.expanduser(args.jackfilepath)
print(targetFilepath + " is the target file/directory")

jackFiles = [];

isFolder = os.path.isdir(targetFilepath)
if isFolder:
    for jackFile in os.listdir(targetFilepath):
        if jackFile.endswith(".jack"):
            jackFiles.append(targetFilepath + "/" + jackFile)
else:
    jackFiles.append(targetFilepath)

for jackFile in jackFiles:
    tokenFilename = JackTokenizer.tokenizeFile(jackFile)
    analyzedXmlFile = jackFile.replace(".jack", "_output.xml")

    tokenTree = ET.parse(tokenFilename)
    ET.indent(tokenTree, '  ')
    tokenTree.write(analyzedXmlFile)
        

print("End JackAnalyzer")
