# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

import re, os

# you can put something in these if you need to see the control statements (if/for) or html tags
SHOWCONTROLSTATEMENT = ""
SHOWHTMLTAG = ""
# this one you are more likely to want to see
SHOWINCLUSION = "[ref]"
SHOWBUTTON = "BUTTON"

def main():
	
	dirname = "../templates/"
	fileNameList = []
	for root, subFolders, fileNames in os.walk(dirname):
		for fileName in fileNames:
			if fileName[-5:] == ".html": # this is to ignore svn stuff
				fileNameList.append(os.path.join(root, fileName))
	try:
		outputFile = open("Template texts.txt", "w")
		for fileName in fileNameList:
			try:
				# replace things in django if/else/for brackets
				file = open(fileName)
				text = file.read()
				tagExpression = re.compile(r'{%(.+?)%}')
				tags = tagExpression.findall(text)
				for tag in tags:
					text = text.replace("{%%%s%%}" % tag, SHOWCONTROLSTATEMENT)
					
				# special search for button names (which are inside html tags)
				buttonNameExpression = re.compile(r'<input type="submit" name="(.+?)" value="(.+?)"', re.DOTALL)
				namesAndValues = buttonNameExpression.findall(text)
				for name, value in namesAndValues:
					text = text.replace('<input type="submit" name="%s" value="%s"' % (name, value), \
									'\n    %s: %s\n<' % (SHOWBUTTON, value))
			
				# replace html tags
				tagExpression = re.compile(r'\<(.+?)\>', re.DOTALL)
				tags = tagExpression.findall(text)
				for tag in tags:
					text = text.replace("<%s>" % tag, SHOWHTMLTAG)
						
				# replace django template lookups, but show that something was referred to
				tagExpression = re.compile(r'{{(.+?)}}')
				tags = tagExpression.findall(text)
				for tag in tags:
					text = text.replace("{{%s}}" % tag, SHOWINCLUSION)
					
				text = text.replace("&nbsp;", "")
				lines = text.split('\n')
				strippedLines = []
				for line in lines:
					if len(line.strip()) and line.strip() != SHOWINCLUSION:
						strippedLines.append(line.strip())
				text = "\n".join(strippedLines)
				#text = "<p>" + text.replace("\n", "</p>\n<p>") + "</p>"
				
				outputFile.write("=====================\n" + fileName + "\n=====================\n\n")
				outputFile.write(text)
				outputFile.write("\n\n")
			finally:
				file.close()
	finally:
		outputFile.close()
	
	#print text

if __name__ == "__main__":
	main()
