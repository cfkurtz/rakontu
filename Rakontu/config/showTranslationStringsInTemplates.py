# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

import re, os

# you can put something in these if you need to see the control statements (if/for) or html tags
SHOWCONTROLSTATEMENT = " "
SHOWCOMMENTSTATEMENT = " "
SHOWHTMLTAG = " "
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
				file = open(fileName)
				text = file.read()
				
				# remove things in django if/else/for brackets
				tagExpression = re.compile(r'{%(.+?)%}')
				tags = tagExpression.findall(text)
				for tag in tags:
					text = text.replace("{%%%s%%}" % tag, SHOWCONTROLSTATEMENT)
					
				# remove django comments
				tagExpression = re.compile(r'{#(.+?)#}')
				tags = tagExpression.findall(text)
				for tag in tags:
					text = text.replace("{#%s#}" % tag, SHOWCOMMENTSTATEMENT)
					
				# special search for button names (which are inside html tags)
				buttonNameExpression = re.compile(r'<input type="submit" name="(.+?)" value="(.+?)"', re.DOTALL)
				namesAndValues = buttonNameExpression.findall(text)
				for name, value in namesAndValues:
					text = text.replace('<input type="submit" name="%s" value="%s"' % (name, value), \
									'\n    %s: %s\n<' % (SHOWBUTTON, value))
			
				# remove html tags
				tagExpression = re.compile(r'\<(.+?)\>', re.DOTALL)
				tags = tagExpression.findall(text)
				for tag in tags:
					text = text.replace("<%s>" % tag, SHOWHTMLTAG)
						
				# remove django template lookups, but show that something was referred to
				tagExpression = re.compile(r'{{(.+?)}}')
				tags = tagExpression.findall(text)
				for tag in tags:
					text = text.replace("{{%s}}" % tag, SHOWINCLUSION)
				text = text.replace("(%s)" % SHOWINCLUSION, "") # don't show refs with only parens around them
				text = text.replace("- %s" % SHOWINCLUSION, "") # similar thing, sometimes there is a "- none"
				text = text.replace("%s  %s" % (SHOWINCLUSION, SHOWINCLUSION), "") # similar thing
				text = text.replace("%s %s" % (SHOWINCLUSION, SHOWINCLUSION), "") # similar thing
					
				text = text.replace("&nbsp;", " ")
				lines = text.split('\n')
				strippedLines = []
				for line in lines:
					if len(line.strip()) and line.strip() != SHOWINCLUSION:
						strippedLines.append(line.strip())
				text = "\n".join(strippedLines)
				
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
