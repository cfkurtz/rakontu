# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

# Because these questions will not be hard-coded in later versions, I'm just putting them
# directly into code, to save time.

from google.appengine.ext import db

from models import Question

def AddSystemQuestionIfNotThere(info):
	matchingQuestions = Question.all().filter("community = ", None).filter("refersTo = ", info[0]).filter("name = ", info[1]).fetch(1000)
	if not matchingQuestions:
		newQuestion = Question(
							   refersTo=info[0],
							   name=info[1],
							   text=info[2],
							   type=info[3],
							   choices=info[4],
							   help=info[5],
							   useHelp=info[6],
							   multiple=info[7],
							   community=None,
							   )
		newQuestion.put()
	else:
		matchingQuestion = matchingQuestions[0]
		# this is so you can make changes to existing questions
		matchingQuestion.refersTo = info[0]
		matchingQuestion.name = info[1]
		matchingQuestion.text = info[2]
		matchingQuestion.type = info[3]
		matchingQuestion.choices = info[4]
		matchingQuestion.help = info[5]
		matchingQuestion.useHelp = info[6]
		matchingQuestion.multiple = info[7]
		matchingQuestion.put()
	
def AddSystemQuestionsToDataStore():
	# member questions
	AddSystemQuestionIfNotThere(["member", "Age", "How old are you?",
		"ordinal", ["20 or younger", "21-40", "41-60", "61 or over"],
		"Please choose an age range.",
		"Connecting which stories are told by people of what ages can be a useful way to look at stories.",
		False])
	AddSystemQuestionIfNotThere(["member", "How feel about community", "How do you feel about our community?",
		"nominal", ["I love it!", "It could be better.", "It's as good a place as any.", "I hate it here."],
		"Describe how you feel about this place.",
		"Connecting which stories are told by people of what ages can be a useful way to look at stories.",
		True])
	AddSystemQuestionIfNotThere(["member", "Location", "Where do you live?",
		"text", [],
		"Enter any sort of location you like, specific or vague.",
		"This question is most useful when your community is geographic.",
		False])
	AddSystemQuestionIfNotThere(["member", "Full time", "Do you live here all the time?",
		"boolean", [],
		"Some people just live here in the summers.",
		"This question is most useful when your community fluctuates.",
		False])
	AddSystemQuestionIfNotThere(["member", "Location", "Where do you live?",
		"text", [],
		"Enter any sort of location you like, specific or vague.",
		"This question is most useful when your community is geographic.",
		False])
	AddSystemQuestionIfNotThere(["member", "How long lived here", "How many years have you been here?",
		"value", [],
		"If less than one, just put one.",
		"This question is most useful when your community is geographic.",
		False])
	
	# story questions
	AddSystemQuestionIfNotThere(["story", "Where took place", "Where did the events of this story take place?",
					"text", [],
					"Describe as much as you like about the location.",
					"This question is most useful when your community is geographic.",
					False])
	AddSystemQuestionIfNotThere(["story", 
					"How feel about",
					"How do you feel about this story?",
					"nominal", ["great", "okay", "bad"],
					"What was your reaction when you read the story?",
					"This is a very useful question and should almost always be included.",
					True])
	
	# pattern questions
	AddSystemQuestionIfNotThere(["pattern", 
					"Observations",
					"What pattern do you see?",
					"text", [],
					"Please describe what is noteworthy, confining yourself to facts that anyone could agree on.",
					"",
					False])
	AddSystemQuestionIfNotThere(["pattern", 
					"Interpretations",
					"What do you think this pattern means?",
					"text", [],
					"Venture an opinion on why the pattern appears the way it does.",
					"",
					False])
	AddSystemQuestionIfNotThere(["pattern", 
					"Implications",
					"What do you think should be done about this pattern?",
					"text", [],
					"If this pattern represents a problem, what can be done about it? If it represents and opportunity, what can be done to benefit from it?",
					"",
					False])
	
	# construct quetsions
	AddSystemQuestionIfNotThere(["construct", 
					"Why built",
					"Why was this construct built?",
					"text", [],
					"Give viewers some idea of the construct's purpose.",
					"",
					False])
	AddSystemQuestionIfNotThere(["construct", 
					"Type", 
					"Why was this construct built?",
					"nominal", ["top ten list", "twice-told stories", "history", "emergent construct"],
					"Which of these types of construct best describes this one?",
					"",
					False])
	
	# invitation questions
	AddSystemQuestionIfNotThere(["invitation", 
					"Why asked",
					"Why was this invitation created?",
					"text", [],
					"Please describe why you think this invitation's creator (yourself or someone else) asked people talk about this.",
					"",
					False])
	AddSystemQuestionIfNotThere(["invitation", 
					"Reference",
					"Is this invitation in reference to an event, person, thing, what?",
					"text", [],
					"Is there anything this invitation asks about in particular?",
					"",
					False])
	
	# resource questions
	AddSystemQuestionIfNotThere(["resource", 
					"Why added",
					"Why was this resource added to the community? What is its value?",
					"text", [],
					"Give your opinion about the reasons behind this resource being added.",
					"",
					False])
	AddSystemQuestionIfNotThere(["resource", 
					"Source",
					"Where did this resource come from?",
					"text", [],
					"List the resource's source.",
					"",
					False])

	# community questions
	AddSystemQuestionIfNotThere(["community", 
					"Geographic",
					"Is this a geographic community?",
					"boolean", [],
					"Does this community represent a place or a group of people?",
					"",
					False])
	AddSystemQuestionIfNotThere(["community", 
					"Why created",
					"Why was this community created?",
					"text", [],
					"Explain why the community was created.",
					"",
					False])



