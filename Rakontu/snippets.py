#---------------------------------------- FROM WEB

The simplest way to get a list of Author instances from a
db.ListProperty(db.Key) is:
authors = [db.get(key) for key in book.authors] 

# change property of Model
p.properties()[s].get_value_for_datastore(p) 

# --------------------------------- NOT USING

class JoinCommunityPage(webapp.RequestHandler):
    def get(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {'url': url, 'url_linktext': url_linktext,'communities': models.Community.all().fetch(1000)}
        if users.get_current_user():
            path = os.path.join(os.path.dirname(__file__), 'templates/joinCommunity.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'templates/notLoggedIn.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        user = users.get_current_user()
        if user:
            okayToJoin = False
            community = db.get(self.request.get('community_key')) 
            if community:
                if community.passwordIsRequired:
                    passwordEntered = self.request.get('password')
                    if passwordEntered == community.password:
                        okayToJoin = True
                    else:
                        self.redirect('/badPassword')
                else:
                    okayToJoin = True
            if okayToJoin:
                member = models.Member(
                    googleAccountID=user.user_id(),
                    community=community,
                    nickname = self.request.get('nickname'),
                    nicknameIsRealName = self.request.get('nickname_is_real_name')=="yes",
                    profileText = self.request.get('profile_text)'))
                member.put()
                self.redirect('/')
            else:
                self.redirect('/couldNotJoin')
                
class CouldNotJoinPage(webapp.RequestHandler):
    def get(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {'url': url, 'url_linktext': url_linktext}
        path = os.path.join(os.path.dirname(__file__), 'templates/couldNotJoin.html')
        self.response.out.write(template.render(path, template_values))

# ------------------------------- NOT USING

                      <td>
                      {% if aMember.isManager %} 
                          <form action="/manageCommunity_Members" method="post">
                          <input type="submit" name="removeManager|{{aMember.googleAccountID}}" value="Remove as Manager">
                          </form>
                      {% else %}
                          <form action="/manageCommunity_Members" method="post">
                          <input type="submit" name="addManager|{{aMember.googleAccountID}}" value="Make Manager">
                          </form>
                      {% endif %}
                      {% ifequal current_member.googleAccountID aMember.googleAccountID %}
                          {% if current_member.isOwner %}
                              <P>Owner
                          {% else %}
                              <p>(not Owner)
                          {% endif %}
                      {% else %}
                          {% if current_member.isOwner %}
                              {% if aMember.isOwner %} 
                                  <form action="/manageCommunity_Members" method="post">
                                  <input type="submit" name="removeOwner|{{aMember.googleAccountID}}" value="Remove as Owner">
                                  </form>
                              {% else %}
                                  <form action="/manageCommunity_Members" method="post">
                                  <input type="submit" name="addOwner|{{aMember.googleAccountID}}" value="Make Owner">
                                  </form>
                              {% endif %}
                          {% endif %}
                      {% endifequal %}
                      </td>
                      
# ------------------------------- NOT USING

                      
# --------------------------------------------------------------------------------------------
# System
# --------------------------------------------------------------------------------------------

class System(db.Model):
    """ Stores system-wide (above the community level) info
    """
    pass

    def getCommunities(self):
        return Community.all()
    
    def getGlobalCommunityQuestions(self):
        return Question.all().filter("community = ", None).filter("refersTo = ", "community").fetch(1000)
    
    def getGlobalAnnotationQuestions(self, articleType):
        return Question.all().filter("community = ", None).filter("refersTo = ", articleType).fetch(1000)
    
    def getGlobalMemberQuestions(self):
        return Question.all().filter("community = ", None).filter("refersTo = ", "member").fetch(1000)
    
    def getGlobalRules(self):
        return Rule.all().filter("community = ", None).fetch(1000)
    
# ----------------------------- NOT USING

    config = ConfigParser.RawConfigParser()
    config.read('rakontu_installation.cfg')
    configSections = config.sections()
    systemQuestions = {}
    for refersToConstant in QUESTION_REFERS_TO:
        for section in configSections:
            (refersToInCFG, name) = section.split(" - ")
            if refersToInCFG == refersToConstant:
                if not systemQuestions.has_key(refersToConstant):
                    systemQuestions[refersToConstant] = []
                newQuestion = Question(
                                       community=None,
                                       type=config.get(section, "Type")
                
                

    
                systemQuestions[refersToConstant].append(config.)

# ----------------------------- NOT USING

"""
# Note, In this early version the rules and community questions are not used, and community managers/owners
# just choose from lists of questions about things. These will be used later.

[community - Geographic]
Text=Is this a geographic community?
Type=nominal
Choices=yes|no
Multiple=false

[Rule]
Name=Where if geographic
CommunityQuestion=Geographic
Test=same as
TestValues=yes
IncludeIf=true
AnnotationQuestion=Where took place
MemberQuestion=Where live
"""

# ---------------------------- NOT USING - was chooseCommunityToManage.html

<html>
    <head>
        <link type="text/css" rel="stylesheet" href="/stylesheets/base.css" />
    </head>
    <body>
        <form action="/chooseCommunityToManage" method="post">
            {% if communities %}
                Which community do you want to manage?
                <div><select name="community_key" size=5>
                {% for community in communities %}
                    <option value="{{ community.key }}">{{ community.name }}</option>
                {% endfor %}
                </select></div>
                <div><input type="submit" value="Manage Selected Rakontu Community"></div>
            {% else %}
                You are not a manager or owner in any communities.
            {% endif %}
        </form>
    <a href="{{ url }}">{{ url_linktext }}</a>
    <p><a href="/">Main page</a>
    </body>
</html>

# ------------------------ NOT USING - was chooseCommunityToVisit.html

<html>
    <head>
        <link type="text/css" rel="stylesheet" href="/stylesheets/base.css" />
    </head>
    <body>
        <form action="/chooseCommunityToVisit" method="post">
            {% if communities %}
                Which community do you want to visit?
                <div><select name="community_key" size=5>
                {% for community in communities %}
                    <option value="{{ community.key }}">{{ community.name }}</option>
                {% endfor %}
                </select></div>
                <div><input type="submit" value="Visit Selected Rakontu Community"></div>
            {% else %}
                You are not a member of any communities.
            {% endif %}
        </form>
    <a href="{{ url }}">{{ url_linktext }}</a>
    <p><a href="/">Main page</a>
    </body>
</html>

# -------------------- NOT USING - decided to save rules for later, should not have non-working classes in now

RULE_TESTS = ["same as", "<", "<=", ">", ">=", "=", "includes"]

class Rule(db.Model):
    """ Simple if-then statement to choose annotation questions based on community questions.
    
    Properties
        community:            The Rakontu community this rule belongs to.
                            If None, is in a global list communities can copy from.
        communityQuestion:    What question about the community the rule is based on.
        annotationQuestion: What question about articles is affected by the rule.
        memberQuestion:     What question about members is affected by the rule.
                            The same rule can affect both annotation and member questions.

        test:                The operation used to compare the community answer to the test value.
        testValues:            The thing(s) compared to the community answer.
        includeIf:            Whether the test should be true or false to include the annotation question. 

    Usage
        In the abstract:
            For the community question <communityQuestion>, 
            IF the evaluation of (<Answer> <test> <testValues>) = includeIf, 
            THEN include <annotationOrMemberQuestion>.
        Examples:
            For the community question "Is this community united by a geographic place?",
              IF the evaluation of (<Answer> "=" ["yes"]) = true, 
              THEN include "Where do you live?" in member questions.
              
              For the community question "Do people want to talk about social issues?",
              IF the evaluation of (<Answer> "includes" ["no!", "maybe not", "not sure"] = false,
              THEN include "Who needs to hear this story?" in annotation questions.
    """
    community = db.ReferenceProperty(Community)
    communityQuestion = db.ReferenceProperty(Question, collection_name="rules pointing to community questions")
    annotationQuestion = db.ReferenceProperty(Question, collection_name="rules pointing to annotation questions")
    memberQuestion = db.ReferenceProperty(Question, collection_name="rules pointing to member questions")

    test = db.StringProperty(choices=RULE_TESTS)
    testValues = db.StringListProperty()
    includeIf = db.BooleanProperty(default=True)

# --------------------- I took a quick look at making a Javscript confirm dialog, but am not allowing myself
# --------------------- to get further into it right now. So saving this for later

    <input type="submit" name="changesTo|{{refer_type}}" value="Change Questions" onClick="javascript:return confirm('Save changes?')">

# -------------------- NOT USING - was questions.html before improving

<html>
    <head>
        <link type="text/css" rel="stylesheet" href="/stylesheets/base.css" />
    </head>
    <body>
        <form action="/manage/questions" method="post">
        <h2>Changing Settings for Rakontu Community "{{ community.name|escape }}"</h2>
        <h3>Questions</h3>
        {% for refer_type in question_refer_types %}
            <h4>{{refer_type|capfirst}} questions</h4>
                {% for question in system_questions %}
                    {% ifequal question.refersTo refer_type %}
                        <label><input type="checkbox" name="{{refer_type}}|{{question.name}}" value="{{refer_type}}|{{question.name}}" 
                        {% for commQuestion in community.getQuestions %}
                            {% ifequal commQuestion.refersTo question.refersTo %}
                                {% ifequal commQuestion.name question.name %}
                                    checked="checked"
                                {% endifequal %}
                            {% endifequal %}
                        {% endfor %}
                            />
                        {{question.text}} - {{question.type}} 
                            {% ifequal question.type "nominal" %}
                                - {{question.choices|join:", "}}
                            {% endifequal %}
                            {% ifequal question.type "ordinal" %}
                                - {{question.choices|join:", "}}
                            {% endifequal %}
                            {% if question.multiple %}
                                - multiple
                            {% endif %}
                            </label></div><br>
                    {% endifequal %}
                {% endfor %}
        {% endfor %}
        <p>
    <input type="submit" name="changeQuestions" value="Change Questions">    
    </form>    
    <p>
    <a href="{{ url }}">{{ url_linktext }}</a>
    </body>
    <p><a href="/">Main page</a>
</html>

# ---------------------- SAVE FOR LATER - had annotations editing in article.html but moving it

            <h3>Annotations</h3>
            <fieldset>
            {% if article %}
                <p>Your annotations for this {{article_type}}</p>
            {% else %}
                <p>If you like, you can enter some annotations for this {{article_type}}.</p>
            {% endif %}
            
            <h4>Tags</h4>
            <p><input type="text" name="tag0" size="20" value="{% if tags %} {{tags.0}} {% endif %}"/>
            <input type="text" name="tag1" size="20" value="{% if tags %} {{tags.1}} {% endif %}"/>
            <input type="text" name="tag2" size="20" value="{% if tags %} {{tags.2}} {% endif %}"/>
            <input type="text" name="tag3" size="20" value="{% if tags %} {{tags.3}} {% endif %}"/>
            <input type="text" name="tag4" size="20" value="{% if tags %} {{tags.4}} {% endif %}"/></p>
            
            <h4>Comment</h4>
            <p>Subject</p>
            <div><input type="commentSubject" name="tag0" size="60" value="
                {% if comment %}
                    {{comment.subject}} 
                {% endif %}
                "/></div>
            <p>Text</p>
            <div><textarea name="commentPost" rows="3" cols="60">
                {% if comment %} 
                    {{comment.post}} 
                {% endif %}
                </textarea></div>
            
            <h4>Request</h4>
            <p>Title</p>
            <div><input type="requestTitle" name="tag0" size="60" value="
                {% if request %}
                    {{request.title}} 
                {% endif %}
                "/></div>
            <p>Text</p>
            <div><textarea name="requestText" rows="3" cols="60">
                {% if request %} 
                    {{request.text}} 
                {% endif %}
                </textarea></div>
            <p>Type</p>
            <div><select>
                {% for aType in request_types %}
                    <option value="request|{{aType}}" 
                        {% if request %} 
                            {% ifequal request.type aType %}
                                selected="selected"
                            {% endifequal %}
                        {% endif %}
                        >{{aType}}</option>
                {% endfor %}
                </select></div>
            </fieldset>
            
# ---------------------------------------- NOT USING - whether they are logged in to Google is not really that relevant

def GenerateURLs(request):
    """ Used to make login/logout link on every page.
        Probably some better way to do this.
    """
    if users.get_current_user():
        url = users.create_logout_url(request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(request.uri)
        url_linktext = 'Login'
    return url, url_linktext

# -------------------------------- NOT USING - decided to get rid of extra pattern info. 
# --------------------------------- instructions can be question, screenshot can be attachment

            {% ifequal article_type "pattern" %}
                <h3>Extra Pattern Information</h3>
                <fieldset>
                {% if article %}
                    <p>Instructions to recreate pattern</p>
                {% else %}
                    <p>Please enter some instructions to recreate the pattern you observed.</p>
                {% endif %}
                <div><textarea name="instructionsIfPattern" rows="3" cols="60">{% if article %} {{article.instructionsIfPattern}} {% endif %}</textarea></div>
                {% if article %}
                    <p>Pattern screenshot</p>
                {% else %}
                    <p>Please upload a screenshot showing the pattern.</p>
                {% endif %}
                {% if article %}
                    {% if article.screenshotIfPattern %}
                        <div><img src="img?article_id={{article.key}}"></img></div>
                    {% endif %}
                {% endif %}
                <p><div><input type="file" name="img"/></div></p>
                </fieldset>
            {% endifequal %}
            </fieldset>

# ---------------------------------- MOVED, may reuse, but needs to be updated

# --------------------------------------------------------------------------------------------
# Queries
# --------------------------------------------------------------------------------------------

class Query(db.Model):
	""" Choice to show subsets of items in main viewer.

	Properties (common to all types):
		owner:			Who this query belongs to.
		created:			When it was created.

		type:				One of free text, tags, answers, members, activities, links. 
		targets:			All searches return articles, annotations, or members (no combinations). 
	"""
	owner = db.ReferenceProperty(Member, required=True, collection_name="queries")
	created = TzDateTimeProperty(auto_now_add=True)

	type = db.StringProperty(choices=QUERY_TYPES, required=True)
	targets = db.StringListProperty(choices=QUERY_TARGETS, required=True)
	
	""" Free text search
	
	Properties:
		targets:			Articles or annotations, or specific types of either.
		text:				The text to search on. Can include boolean AND, OR, NOT.
	Usage: 
		Show [QUERY_TARGETS] with <text> 
	Examples: 
		Show [comments] with <hate OR love> 
		(with selection) Show [nudges] in the selection with <NOT ""> (meaning, with non-blank nudge comments)
	"""
	text = db.StringProperty()
	
	""" Tag search
	
	Properties:
		targets:			Articles or annotations, or specific types of either. 
		tags:				List of tags to search on. 1-n.
		combination:		Whether to search for all or any of the tags listed.
	Usage:
		Show [QUERY_TARGETS] in which [All, ANY] of <tags> appear 
	Examples: 
		Show [invitations] with [ANY OF] the tags <"need for project", "important">
		(with selection) Show [resources] in the selection with the tag <"planning"> 
	"""
	tags = db.StringListProperty()
	combination = db.StringProperty(choices=BOOLEAN_CHOICES, default="ANY")
	
	""" Answer search
	
	Properties:
		targets:			Articles or annotations, or specific types of either. 
		questionAnswers:	List of strings denoting question and one or more answers.
							Saved together and parsed. 1-n.
		combination:		Whether to search for all or any of the question-answer sets listed.
	Usage:
		Show [QUERY_TARGETS] in which {questions+answers} appear 
	Examples: 
		Show [stories] with [ALL OF] <How do you feel ~ includes ~ happy> and <What was the outcome ~ is ~ bad>
		(with selection) Show [articles] in the selection with <How damaging is this story ~ >= ~ 75>
	"""
	questionAnswers = db.StringListProperty()
	
	""" Member search
	
	Properties:
		memberType:			What sort of member to find. 
		activity:			What the member should have done. 
		timeFrame:			When the member should have done it. 
	Usage:
		Show [MEMBER_TYPES] who have [ACTIVITIES_VERB] in [RECENT_TIME_FRAMES]
	Examples: 
		Show [off-line members] who [commented] in [the last week]
		(with selection) Show [members] who [nudged] the selected story in [the last hour]
	"""
	memberType = db.StringProperty(choices=MEMBER_TYPES)
	activity = db.StringProperty(choices=ACTIVITIES_VERB)
	timeFrame = db.StringProperty(choices=RECENT_TIME_FRAMES)
	
	""" Activity search
	Properties:
		targets:			Articles or annotations, or specific types of either. 
		activity:			What the member should have done. 
		memberIDS:			Who should have done it. 1-n.
		combination:		Whether to search for all or any of the members listed.
		timeFrame:			When the member(s) should have done it. 
	Usage:
		Show [QUERY_TARGETS] in which [ACTIVITIES_VERB] were done by {members} in [RECENT_TIME_FRAMES]
	Examples:
		Show [stories] [retold] by {Joe OR Jim} in [the past 6 months]
		(with selection) Show which of the selected [articles] {I} have [nudged] [ever]
	"""
	memberIDs = db.StringListProperty()
	
	""" Link search
	Properties:
		articleType:		Articles (without annotations). 
		linkType:			Type of link. 
		typeLinkedTo:		What sort of article should have been linked to. 
		memberIDS:			Who should have done it. 1-n.
		timeFrame:			When the member(s) should have done it. 
	Usage:
		Show [ARTICLE_TYPES] {members} connected with [LINK_TYPES] to [ARTICLE_TYPES] in [RECENT_TIME_FRAMES]
	Examples:
		Show [resources] {I} have [related] to [stories] in [the past month]
		(with selection) Show [stories] [included] in the selected pattern by {anyone} [ever]
	"""
	articleType = db.StringProperty(choices=ARTICLE_TYPES)
	linkType = db.StringProperty(choices=LINK_TYPES)
	typeLinkedTo = db.StringProperty(choices=ARTICLE_TYPES)



