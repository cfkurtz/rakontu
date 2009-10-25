# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.

# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------
# This utility checks whether the help texts in help.csv are correctly linked to specifications in the templates files.
# Use this when you change the templates files or when you change or translate the help.csv file,
# to make sure things are mapped correctly (ie you didn't delete anything by accident).
# --------------------------------------------------------------------------------------------
# NOTE: The regex expression here will freak out if there are TWO of these
# help-text references on the same line. (I know, I should know regex better.)
# So if that happens just go into the template and put a carriage return between them.
# Or fix the regex expression yourself!
# --------------------------------------------------------------------------------------------

import re, os, csv, sys

CONFIG_LANGUAGE_DIR = "english" # change to suit your language

def stringBeyond(aString, aDelimiter):
    if len(aString) == 0:
        result = ""
        return result
    delimiterPos = aString.find(aDelimiter)
    if delimiterPos == -1:
        result = aString
    elif delimiterPos == len(aString) - 1:
        result = ""
    else:
        result = aString[delimiterPos + len(aDelimiter):]
    return result

def main():
	
	helpFileName = "../config/%s/help.csv" % CONFIG_LANGUAGE_DIR
	helpTypesAndNamesWithFileNames = {}
	missingHelpTextsInFileNames = {}
	file = open(helpFileName) 
	try:
		helpStrings = csv.reader(file)
		for row in helpStrings:
			if len(row[0]) > 0 and row[0][0] != ";":
				helpTypesAndNamesWithFileNames[(row[0].strip(), row[1].strip())] = []
	finally: 
		file.close()     

	templateDir = "../templates"
	fileNameList = []
	for root, subFolders, fileNames in os.walk(templateDir):
		for fileName in fileNames:
			if fileName[-5:] == ".html": # this is to ignore svn stuff
				fileNameList.append(os.path.join(root, fileName))
	try:
		outputFile = open("Help ID connections.txt", "w")
		filesDone = 0
		for fileName in fileNameList:
			try:
				file = open(fileName)
				text = file.read()
				# add all usages to dictionary of help.csv items
				for type, name in helpTypesAndNamesWithFileNames.keys():
					if type == "button":
						typeToLookFor = "buttonTooltip"
					else:
						typeToLookFor = type
					if text.find('{{"%s"|%s}}' % (name, typeToLookFor)) >= 0:
						list = helpTypesAndNamesWithFileNames[(type, name)]
						list.append(stringBeyond(fileName, "../templates/"))
				# check for items referred to in html file but NOT in help.csv
				for id in ["tip", "info", "caution", "buttonTooltip"]:
					expression = re.compile(r'{{\"(.+?)\"\|%s}}' % id)
					names = expression.findall(text)
					if id == "buttonTooltip":
						idToLookFor = "button"
					else:
						idToLookFor = id
					for name in names:
						if name.strip():
							if not helpTypesAndNamesWithFileNames.has_key((idToLookFor, name)):
								if not missingHelpTextsInFileNames.has_key((idToLookFor, name)):
									missingHelpTextsInFileNames[(idToLookFor, name)] = []
								missingHelpTextsInFileNames[(idToLookFor, name)].append(fileName)
			finally:
				file.close()
				filesDone += 1
		outputFile.write("HELP TEXTS IN HELP.CSV AND THEIR USES IN THE HTML TEMPLATES \n\n")
		typesAndNamesSorted = []
		typesAndNamesSorted.extend(helpTypesAndNamesWithFileNames.keys())
		typesAndNamesSorted.sort(lambda a,b: cmp(a[0], b[0]))
		for type, name in typesAndNamesSorted:
			list = helpTypesAndNamesWithFileNames[(type, name)]
			if len(list):
				outputFile.write("%s: %s \n    %s\n\n" % (type, name, "\n    ".join(list)))
			else:
				outputFile.write("%s: %s \n    >>>> THIS HELP TEXT IS NOT REFERENCED IN ANY TEMPLATE.\n\n" % (type, name))
		outputFile.write("\n=============\n\nREFERENCES IN HTML TEMPLATES WITH NO HELP TEXTS IN HELP.CSV\n\n")
		if missingHelpTextsInFileNames:
			typesAndNamesSorted = []
			typesAndNamesSorted.extend(missingHelpTextsInFileNames.keys())
			typesAndNamesSorted.sort(lambda a,b: cmp(a[0], b[0]))
			for type, name in typesAndNamesSorted:
				list = missingHelpTextsInFileNames[(type, name)]
				outputFile.write("%s: %s \n    %s\n\n" % (type, name, "\n    ".join(list)))
		else:
			outputFile.write("(none)\n")
	finally:
		outputFile.close()
		print filesDone, "of", len(fileNameList), "files processed."
	
	#print text

if __name__ == "__main__":
	main()
