# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

from visit import *
from create import *
from curate import *
from guide import *
from liaise import *
from manage import *
from admin import *

application = webapp.WSGIApplication(
									 [('/', StartPage),
									  
									  # looking at objects
									  ('/visit', BrowseEntriesPage),
									  ('/visit/', BrowseEntriesPage),
									  ('/visit/look', BrowseEntriesPage),
									  ('/visit/filter', SavedSearchEntryPage),
									  ('/visit/read', ReadEntryPage),
									  ('/visit/readAnnotation', ReadAnnotationPage),
									  
									  # looking at people
									  ('/visit/members', SeeCommunityMembersPage),
									  ('/visit/member', SeeMemberPage),
									  ('/visit/character', SeeCharacterPage),
									  ('/visit/community', SeeCommunityPage),
									  
									  # membership
									  ('/visit/new', NewMemberPage),
									  ('/visit/profile', ChangeMemberProfilePage),
									  ('/visit/drafts', ChangeMemberDraftsPage),
									  ('/visit/leave', LeaveCommunityPage),
									  
									  # help
									  ('/visit/help', GetHelpPage),

									  # entering entries
									  ('/visit/story', EnterEntryPage),
									  ('/visit/retell', EnterEntryPage),
									  ('/visit/remind', EnterEntryPage),
									  ('/visit/respond', EnterEntryPage),
									  ('/visit/pattern', EnterEntryPage),
									  ('/visit/collage', EnterEntryPage),
									  ('/visit/invitation', EnterEntryPage),
									  ('/visit/resource', EnterEntryPage),
									  ('/visit/entry', EnterEntryPage),
									  
									  # answering questions
									  ('/visit/answers', AnswerQuestionsAboutEntryPage),
									  ('/visit/preview', PreviewPage),
									  ('/visit/previewAnswers', PreviewPage),
									  
									  # entering annotations
									  ('/visit/request', EnterAnnotationPage),
									  ('/visit/tagset', EnterAnnotationPage),
									  ('/visit/comment', EnterAnnotationPage),
									  ('/visit/nudge', EnterAnnotationPage),
									  ('/visit/annotation', EnterAnnotationPage),
									  
									  # entering links
									  ('/visit/relate', RelateEntryPage),
									  
									  # curating
									  ('/visit/curate', ReadEntryPage),
									  ('/visit/flag', FlagOrUnflagItemPage),
									  ('/curate', CurateFlagsPage),
									  ('/curate/', CurateFlagsPage),
									  ('/curate/flags', CurateFlagsPage),
									  ('/curate/gaps', CurateGapsPage),
									  ('/curate/attachments', CurateAttachmentsPage),
									  ('/curate/tags', CurateTagsPage),
									  
									  # guiding
									  ('/guide/', ReviewResourcesPage),
									  ('/guide', ReviewResourcesPage),
									  ('/guide/resource', EnterEntryPage),
									  ('/guide/resources', ReviewResourcesPage),
									  ('/guide/requests', ReviewRequestsPage),
									  
									  # liaising
									  ('/liaise/', ReviewOfflineMembersPage),
									  ('/liaise', ReviewOfflineMembersPage),
									  ('/liaise/batch', BatchEntryPage),
									  ('/liaise/review', ReviewBatchEntriesPage),
									  ('/liaise/members', ReviewOfflineMembersPage),
									  ('/liaise/printSearch', PrintSearchPage),
									  ('/liaise/printEntryAndAnnotations', PrintEntryAnnotationsPage),
									  
									  # managing
									  ('/createCommunity', CreateCommunityPage),
									  ('/manage/first', FirstOwnerVisitPage),
									  ('/manage', ManageCommunitySettingsPage),
									  ('/manage/', ManageCommunitySettingsPage),
									  ('/manage/members', ManageCommunityMembersPage),
									  ('/manage/settings', ManageCommunitySettingsPage),
									  ('/manage/questions_list', ManageCommunityQuestionsListPage),
									  ('/manage/questions_story', ManageCommunityQuestionsPage),
									  ('/manage/questions_pattern', ManageCommunityQuestionsPage),
									  ('/manage/questions_collage', ManageCommunityQuestionsPage),
									  ('/manage/questions_invitation', ManageCommunityQuestionsPage),
									  ('/manage/questions_resource', ManageCommunityQuestionsPage),
									  ('/manage/questions_member', ManageCommunityQuestionsPage),
									  ('/manage/questions_character', ManageCommunityQuestionsPage),
									  ('/manage/questions_questions', ManageCommunityQuestionsPage),
									  ('/manage/questionsToCSV', WriteQuestionsToCSVPage),
									  ('/manage/characters', ManageCommunityCharactersPage),
									  ('/manage/character', ManageCommunityCharacterPage),
									  ('/manage/technical', ManageCommunityTechnicalPage),
									  ('/manage/inactivate', InactivateCommunityPage),
									  ('/manage/export', ExportCommunityDataPage),
									  ('/manage/systemResources', SystemResourcesPage),
									  
									  # site admin
									  ('/admin/', AdministerCommunitiesPage),
									  ('/admin', AdministerCommunitiesPage),
									  ('/admin/communities', AdministerCommunitiesPage),
									  ('/admin/generateSystemQuestions', GenerateSampleQuestionsPage),
									  ('/admin/generateHelps', GenerateHelpsPage),
									  
									  # general message-to-user page
									   ('/result', ResultFeedbackPage),
									  
									  # file handlers
									  ('/img', ImageHandler),
									  ('/visit/img', ImageHandler),
									  ('/manage/img', ImageHandler),
									  ('/visit/attachment', AttachmentHandler),
									  ('/export', ExportHandler),
									  
									  ],
									 debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
