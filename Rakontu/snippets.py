#---------------------------------------- FROM WEB

The simplest way to get a list of Author instances from a
db.ListProperty(db.Key) is:
authors = [db.get(key) for key in book.authors] 

# change property of Model
p.properties()[s].get_value_for_datastore(p) 

#---------------------------------------- NOT USING

FAKE_STORY_DATA = {
                   "My day at the zoo": "I lost my freeze pop, and the lion ate my cousin. Pretty fun day.",
                   "Let's all be friends": "It was my first day of school, and the teacher sat on me.",
                   "The tree fell on my house": "It was my second best tiny stick house, and a branch fell on it and squashed it.",
                   "My foot hurts": "Don't trust salespeople in shoe stores.",
                   "The newt turned back": "So I filled up the little pond, and a newt didn't like it, so he climbed out. Then the dog sniffed him and he climbed back in. (true story!)",
                   "There it is": "Every time I give up on finding something, there it is! What's up with that?",
                   "Lovely junk": "So I put this old plastic toy in the attic and now the kids love it because it's junk.",
                   "The story of our town": "Our town was built by a giant. Last week a massive tree fell onto it. We are rebuilding.",
                   "Shorts": "I like to take my shorts out in January and put them on and pretend I'm on the other side of the world.",
                   "The dead frog": "We found a dead frog in the stream. For a while we didn't drink the water, but then we forgot about it.",
                   }

FAKE_COMMENTS = {
                 "What?": "Come on, that didn't really happen.",
                 "Yep": "Same thing happened to me.",
                 "Liar!": "I think you totally made that up.",
                 "I was there!": "I think you have distorted things a little, haven't you?",
                 "You have helped me": "I can't tell you how much your story has touched my life.",
                 }

def CreateABunchOfFakeData():
    aMember = Member(users.get_current_user())

    
    for title in FAKE_STORY_DATA.keys():
        aStory = Story(title=title, text=FAKE_STORY_DATA[title], creator=aMember, )
    aStory = Story(
                  title="My day at the zoo",
                  text="I lost my freeze pop, and the lion ate my cousin. Pretty fun day.",
                  creator=aMember,
                  attribution="member",
                  tookPlace=datetime.datetime(2009, 4, 2),
                  collected=datetime.datetime.now)
    aStory.put()
    aComment = Comment(
                       subject="Your cousin??", 
                       post="Is that really true about your cousin?",
                       article=aStory,
                       creator=anotherMember,
                       attribution="personification",
                       personification=aPersonification,
                       collected=datetime.datetime.now)

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

