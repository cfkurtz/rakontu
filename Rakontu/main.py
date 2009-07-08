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
									  ('/guide/invitations', ReviewInvitationsPage),
									  ('/guide/requests', ReviewRequestsPage),
									  ('/guide/resources', ReviewResourcesPage),
									  ('/guide/resource', EnterEntryPage),
									  ('/guide/copySystemResourcesToRakontu', CopySystemResourcesPage),
									  
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
									  ('/manage/characters', ManageCharactersPage),
									  ('/manage/character', ManageCharacterPage),
									  ('/manage/technical', ManageRakontuTechnicalPage),
									  ('/manage/inactivate', InactivateRakontuPage),
									  ('/manage/export', ExportRakontuDataPage),
									  ('/manage/exportSearch', ExportSearchPage),
									  
									  # site admin
									  ('/admin/', AdministerRakontusPage),
									  ('/admin', AdministerRakontusPage),
									  ('/admin/review', AdministerRakontusPage),
									  ('/admin/generateSystemQuestions', GenerateSampleQuestionsPage),
									  ('/admin/generateSystemResources', GenerateSystemResourcesPage),
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

def real_main():
	run_wsgi_app(application)

def profile_log_main():
	 # This is the main function for profiling 
	 # We've renamed our original main() above to real_main()
	 import cProfile, pstats, StringIO
	 prof = cProfile.Profile()
	 prof = prof.runctx("real_main()", globals(), locals())
	 stream = StringIO.StringIO()
	 stats = pstats.Stats(prof, stream=stream)
	 stats.sort_stats("time")  # Or cumulative
	 stats.print_stats(80)  # 80 = how many to print
	 # The rest is optional.
	 # stats.print_callees()
	 # stats.print_callers()
	 logging.info("Profile data:\n%s", stream.getvalue())
	 
def profile_html_main():
	 # This is the main function for profiling 
	 # We've renamed our original main() above to real_main()
	 import cProfile, pstats
	 prof = cProfile.Profile()
	 prof = prof.runctx("real_main()", globals(), locals())
	 print "<pre>"
	 stats = pstats.Stats(prof)
	 stats.sort_stats("time")  # Or cumulative
	 stats.print_stats(80)  # 80 = how many to print
	 # The rest is optional.
	 # stats.print_callees()
	 # stats.print_callers()
	 print "</pre>"
	 
#main = profile_html_main
main = real_main

if __name__ == "__main__":
	main()
	
