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
									  ('/visit/home', BrowseEntriesPage),
									  ('/visit/filter', SavedSearchEntryPage),
									  ('/visit/read', ReadEntryPage),
									  ('/visit/readAnnotation', ReadAnnotationPage),
									  
									  # looking at people
									  ('/visit/members', SeeRakontuMembersPage),
									  ('/visit/member', SeeMemberPage),
									  ('/visit/character', SeeCharacterPage),
									  ('/visit/rakontu', SeeRakontuPage),
									  
									  # membership
									  ('/visit/new', NewMemberPage),
									  ('/visit/profile', ChangeMemberProfilePage),
									  ('/visit/drafts', ChangeMemberDraftsPage),
									  ('/visit/leave', LeaveRakontuPage),
									  
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
									  ('/guide/orphans', GuideOrphansPage),
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
									  ('/create', CreateRakontuPage),
									  ('/manage/first', FirstOwnerVisitPage),
									  ('/manage', ManageRakontuSettingsPage),
									  ('/manage/', ManageRakontuSettingsPage),
									  ('/manage/members', ManageRakontuMembersPage),
									  ('/manage/settings', ManageRakontuSettingsPage),
									  ('/manage/questions_list', ManageRakontuQuestionsListPage),
									  ('/manage/questions_story', ManageRakontuQuestionsPage),
									  ('/manage/questions_pattern', ManageRakontuQuestionsPage),
									  ('/manage/questions_collage', ManageRakontuQuestionsPage),
									  ('/manage/questions_invitation', ManageRakontuQuestionsPage),
									  ('/manage/questions_resource', ManageRakontuQuestionsPage),
									  ('/manage/questions_member', ManageRakontuQuestionsPage),
									  ('/manage/questions_character', ManageRakontuQuestionsPage),
									  ('/manage/questions_questions', ManageRakontuQuestionsPage),
									  ('/manage/questionsToCSV', WriteQuestionsToCSVPage),
									  ('/manage/characters', ManageRakontuCharactersPage),
									  ('/manage/character', ManageRakontuCharacterPage),
									  ('/manage/technical', ManageRakontuTechnicalPage),
									  ('/manage/inactivate', InactivateRakontuPage),
									  ('/manage/export', ExportRakontuDataPage),
									  ('/manage/systemResources', SystemResourcesPage),
									  
									  # site admin
									  ('/admin/', AdministerRakontusPage),
									  ('/admin', AdministerRakontusPage),
									  ('/admin/rakontus', AdministerRakontusPage),
									  ('/admin/generateSystemQuestions', GenerateSampleQuestionsPage),
									  ('/admin/generateHelps', GenerateHelpsPage),
									  
									  # message-to-user pages
									   ('/result', ResultFeedbackPage),
									   ('/help', ContextualHelpPage),
									  
									  # file handlers
									  ('/img', ImageHandler),
									  ('/visit/img', ImageHandler),
									  ('/manage/img', ImageHandler),
									  ('/attachment', AttachmentHandler),
									  ('/visit/attachment', AttachmentHandler),
									  ('/export', ExportHandler),
									  
									  ],
									 debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
