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

# this is just to avoid looking over and over at files already done
DONELIST = []
"""
		"../templates/english/common_attribution.html",
		"../templates/english/common_footer.html",
		"../templates/english/common_grid.html",
		"../templates/english/common_head.html",
		"../templates/english/common_menus.html",
		"../templates/english/common_questions.html",
		"../templates/english/help.html",
		"../templates/english/result.html",
		"../templates/english/start.html",
		"../templates/english/admin/admin.html",
		"../templates/english/admin/create_rakontu_part_one.html",
		"../templates/english/admin/create_rakontu_part_two.html",
		"../templates/english/curate/attachments.html",
		"../templates/english/curate/flags.html",
		"../templates/english/curate/gaps.html",
		"../templates/english/curate/tags.html",
		"../templates/english/guide/invitations.html",
		"../templates/english/guide/requests.html",
		"../templates/english/guide/resources.html",
		"../templates/english/liaise/batch.html",
		"../templates/english/liaise/members.html",
		"../templates/english/liaise/review.html",
		"../templates/english/manage/character.html",
		"../templates/english/manage/characters.html",
		"../templates/english/manage/export.html",
		"../templates/english/manage/first.html",
		"../templates/english/manage/inactivate.html",
		"../templates/english/manage/members.html",
		"../templates/english/manage/questions.html",
		"../templates/english/manage/questionsList.html",
		"../templates/english/manage/settings.html",
		"../templates/english/visit/annotation.html",
		"../templates/english/visit/answers.html",
		"../templates/english/visit/ask.html",
		"../templates/english/visit/character.html",
		"../templates/english/visit/drafts.html",
		"../templates/english/visit/entry.html",
		"../templates/english/visit/filter.html",
		"../templates/english/visit/filters.html",
		"../templates/english/visit/help.html",
		"../templates/english/visit/home.html",
		"../templates/english/visit/home_grid.html",
		"../templates/english/visit/leave.html",
		"../templates/english/visit/member.html",
		"../templates/english/visit/members.html",
		"../templates/english/visit/new.html",
		"../templates/english/visit/preview.html",
		"../templates/english/visit/previewAnswers.html",
		"../templates/english/visit/profile.html",
		"../templates/english/visit/rakontu.html",
		"../templates/english/visit/read.html",
		"../templates/english/visit/readAnnotation.html",
		"../templates/english/visit/relate.html",
		]
"""

def main():
	
	dirname = "../templates/"
	fileNameList = []
	for root, subFolders, fileNames in os.walk(dirname):
		for fileName in fileNames:
			if fileName[-5:] == ".html": # this is to ignore svn stuff
				fileNameList.append(os.path.join(root, fileName))
	try:
		outputFile = open("Template texts.txt", "w")
		filesDone = 0
		for fileName in fileNameList:
			if not fileName in DONELIST:
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
					filesDone += 1
	finally:
		outputFile.close()
		print filesDone, "of", len(fileNameList), "files processed."
	
	#print text

if __name__ == "__main__":
	main()
