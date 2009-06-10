# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from visit import *
from create import *
from manage import *

application = webapp.WSGIApplication(
									 [('/', StartPage),
									  
									  # visiting
									  ('/visit', BrowseArticlesPage),
									  ('/visit/', BrowseArticlesPage),
									  ('/visit/look', BrowseArticlesPage),
									  ('/visit/read', ReadArticlePage),
									  ('/visit/curate', ReadArticlePage),
									  ('/visit/flag', FlagOrUnflagItemPage),
									  ('/visit/readAnnotation', ReadAnnotationPage),
									  ('/visit/members', SeeCommunityMembersPage),
									  ('/visit/member', SeeMemberPage),
									  ('/visit/character', SeeCharacterPage),
									  ('/visit/community', SeeCommunityPage),
									  ('/visit/new', NewMemberPage),
									  ('/visit/profile', ChangeMemberProfilePage),
									  
									  # entering articles
									  ('/visit/story', EnterArticlePage),
									  ('/visit/retell', EnterArticlePage),
									  ('/visit/remind', EnterArticlePage),
									  ('/visit/respond', EnterArticlePage),
									  ('/visit/pattern', EnterArticlePage),
									  ('/visit/collage', EnterArticlePage),
									  ('/visit/invitation', EnterArticlePage),
									  ('/visit/resource', EnterArticlePage),
									  ('/visit/article', EnterArticlePage),
									  
									  # answering questions
									  ('/visit/answers', AnswerQuestionsAboutArticlePage),
									  ('/visit/preview', PreviewPage),
									  ('/visit/previewAnswers', PreviewPage),
									  
									  # entering annotations
									  ('/visit/request', EnterAnnotationPage),
									  ('/visit/tagset', EnterAnnotationPage),
									  ('/visit/comment', EnterAnnotationPage),
									  ('/visit/nudge', EnterAnnotationPage),
									  ('/visit/annotation', EnterAnnotationPage),
									  
									  # entering links
									  ('/visit/relate', RelateArticlePage),
									  
									  ('/curate/flags', CurateFlagsPage),
									  
									  # managing
									  ('/createCommunity', CreateCommunityPage),
									  ('/manage', ManageCommunitySettingsPage),
									  ('/manage/', ManageCommunitySettingsPage),
									  ('/manage/members', ManageCommunityMembersPage),
									  ('/manage/settings', ManageCommunitySettingsPage),
									  ('/manage/questions_story', ManageCommunityQuestionsPage),
									  ('/manage/questions_pattern', ManageCommunityQuestionsPage),
									  ('/manage/questions_collage', ManageCommunityQuestionsPage),
									  ('/manage/questions_invitation', ManageCommunityQuestionsPage),
									  ('/manage/questions_resource', ManageCommunityQuestionsPage),
									  ('/manage/questions_member', ManageCommunityQuestionsPage),
									  ('/manage/questions_questions', ManageCommunityQuestionsPage),
									  ('/manage/characters', ManageCommunityCharactersPage),
									  ('/manage/technical', ManageCommunityTechnicalPage),
									  
									  # file handlers
									  ('/img', ImageHandler),
									  ('/visit/img', ImageHandler),
									  ('/manage/img', ImageHandler),
									  ('/visit/attachment', AttachmentHandler),
									  
									  # site admin
									  ('/admin/showAllCommunities', ShowAllCommunities),
									  ('/admin/showAllMembers', ShowAllMembers),
									  ('/admin/generateSystemQuestions', GenerateSystemQuestionsPage),
									  ('/admin/generateHelps', GenerateHelpsPage),
									  ],
									 debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
