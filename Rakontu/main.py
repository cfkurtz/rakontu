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
									  (HOME, BrowseEntriesPage),
									  (BuildURL("dir_visit"), BrowseEntriesPage),
									  (BuildURL("dir_visit", extraSlash=True), BrowseEntriesPage),
									  (BuildURL("dir_visit", "url_search_filter"), SavedSearchEntryPage),
									  (BuildURL("dir_visit", "url_read"), ReadEntryPage),
									  (BuildURL("dir_visit", "url_read_annotation"), ReadAnnotationPage),
									  
									  # looking at people
									  (BuildURL("dir_visit", "url_members"), SeeRakontuMembersPage),
									  (BuildURL("dir_visit", "url_member"), SeeMemberPage),
									  (BuildURL("dir_visit", "url_character"), SeeCharacterPage),
									  (BuildURL("dir_visit", "url_rakontu"), SeeRakontuPage),
									  
									  # membership
									  (BuildURL("dir_visit", "url_new"), NewMemberPage),
									  (BuildURL("dir_visit", "url_preferences"), ChangeMemberProfilePage),
									  (BuildURL("dir_visit", "url_drafts"), ChangeMemberDraftsPage),
									  (BuildURL("dir_visit", "url_filters"), ChangeMemberFiltersPage),
									  (BuildURL("dir_visit", "url_leave"), LeaveRakontuPage),
									  
									  # help
									  (BuildURL("dir_visit", "url_help"), GeneralHelpPage),
									  (BuildURL(None, "url_result"), ResultFeedbackPage),
									  (BuildURL(None, "url_help"), ContextualHelpPage),
									  (BuildURL("dir_visit", "url_ask"), AskGuidePage),
									  
									  # entering entries
									  (BuildURL("dir_visit", URLForEntryType("story")), EnterEntryPage),
									  (BuildURL("dir_visit", "url_retell"), EnterEntryPage),
									  (BuildURL("dir_visit", "url_remind"), EnterEntryPage),
									  (BuildURL("dir_visit", "url_respond"), EnterEntryPage),
									  (BuildURL("dir_visit", URLForEntryType("pattern")), EnterEntryPage),
									  (BuildURL("dir_visit", URLForEntryType("collage")), EnterEntryPage),
									  (BuildURL("dir_visit", URLForEntryType("invitation")), EnterEntryPage),
									  (BuildURL("dir_visit", URLForEntryType("resource")), EnterEntryPage),
									  (BuildURL("dir_visit", "url_entry"), EnterEntryPage),
									  
									  # answering questions
									  (BuildURL("dir_visit", "url_answers"), AnswerQuestionsAboutEntryPage),
									  (BuildURL("dir_visit", "url_preview"), PreviewPage),
									  (BuildURL("dir_visit", "url_preview_answers"), PreviewPage),
									  
									  # entering annotations
									  (BuildURL("dir_visit", URLForAnnotationType("request")), EnterAnnotationPage),
									  (BuildURL("dir_visit", URLForAnnotationType("tag set")), EnterAnnotationPage),
									  (BuildURL("dir_visit", URLForAnnotationType("comment")), EnterAnnotationPage),
									  (BuildURL("dir_visit", URLForAnnotationType("nudge")), EnterAnnotationPage),
									  (BuildURL("dir_visit", "url_annotation"), EnterAnnotationPage),
									  
									  # entering links
									  (BuildURL("dir_visit", "url_relate"), RelateEntryPage),
									  
									  # curating 
									  (BuildURL("dir_visit", "url_curate"), ReadEntryPage),
									  (BuildURL("dir_curate"), CurateFlagsPage),
									  (BuildURL("dir_curate", extraSlash=True), CurateFlagsPage), 
									  (BuildURL("dir_curate", "url_flags"), CurateFlagsPage),
									  (BuildURL("dir_curate", "url_gaps"), CurateGapsPage),
									  (BuildURL("dir_curate", "url_attachments"), CurateAttachmentsPage), 
									  (BuildURL("dir_curate", "url_tags"), CurateTagsPage),
									   
									  # guiding
									  (BuildURL("dir_guide"), ReviewResourcesPage),
									  (BuildURL("dir_guide", extraSlash=True), ReviewResourcesPage),
									  (BuildURL("dir_guide", "url_invitations"), ReviewInvitationsPage),
									  (BuildURL("dir_guide", "url_requests"), ReviewRequestsPage),
									  (BuildURL("dir_guide", "url_resources"), ReviewResourcesPage),
									  (BuildURL("dir_guide", URLForEntryType("resource")), EnterEntryPage),
									  (BuildURL("dir_guide", "url_copy_resources"), CopySystemResourcesPage),
									  
									  # liaising
									  (BuildURL("dir_liaise"), ReviewOfflineMembersPage),
									  (BuildURL("dir_liaise", extraSlash=True), ReviewOfflineMembersPage),
									  (BuildURL("dir_liaise", "url_batch"), BatchEntryPage),
									  (BuildURL("dir_liaise", "url_review"), ReviewBatchEntriesPage),
									  (BuildURL("dir_liaise", "url_members"), ReviewOfflineMembersPage),
									  (BuildURL("dir_liaise", "url_print_search"), PrintSearchPage),
									  (BuildURL("dir_liaise", "url_print_entry"), PrintEntryAnnotationsPage),
									  (BuildURL("dir_liaise", "url_print_member"), PrintMemberEntriesAndAnnotationsPage),
									  (BuildURL("dir_liaise", "url_print_character"), PrintCharacterEntriesAndAnnotationsPage),
									   
									  # managing
									  (BuildURL("dir_manage", "url_first"), FirstOwnerVisitPage),
									  (BuildURL("dir_manage"), ManageRakontuSettingsPage),
									  (BuildURL("dir_manage", extraSlash=True), ManageRakontuSettingsPage),
									  (BuildURL("dir_manage", "url_members"), ManageRakontuMembersPage),
									  (BuildURL("dir_manage", "url_settings"), ManageRakontuSettingsPage),
									  (BuildURL("dir_manage", "url_questions_list"), ManageRakontuQuestionsListPage),
									  # these are special and you can't use BuildURL for them
									  ('/%s/%s_%s' % (DIRS["dir_manage"], URLS["url_questions"], URLForQuestionRefersTo("story")), ManageRakontuQuestionsPage),
									  ('/%s/%s_%s' % (DIRS["dir_manage"], URLS["url_questions"], URLForQuestionRefersTo("pattern")), ManageRakontuQuestionsPage),
									  ('/%s/%s_%s' % (DIRS["dir_manage"], URLS["url_questions"], URLForQuestionRefersTo("collage")), ManageRakontuQuestionsPage),
									  ('/%s/%s_%s' % (DIRS["dir_manage"], URLS["url_questions"], URLForQuestionRefersTo("invitation")), ManageRakontuQuestionsPage),
									  ('/%s/%s_%s' % (DIRS["dir_manage"], URLS["url_questions"], URLForQuestionRefersTo("resource")), ManageRakontuQuestionsPage),
									  ('/%s/%s_%s' % (DIRS["dir_manage"], URLS["url_questions"], URLForQuestionRefersTo("member")), ManageRakontuQuestionsPage),
									  ('/%s/%s_%s' % (DIRS["dir_manage"], URLS["url_questions"], URLForQuestionRefersTo("character")), ManageRakontuQuestionsPage),
									  ('/%s/%s_%s' % (DIRS["dir_manage"], URLS["url_questions"], URLS["url_questions"]), ManageRakontuQuestionsPage),
									  (BuildURL("dir_manage", "url_questions_to_csv"), WriteQuestionsToCSVPage),
									  (BuildURL("dir_manage", "url_characters"), ManageCharactersPage),
									  (BuildURL("dir_manage", "url_character"), ManageCharacterPage),
									  (BuildURL("dir_manage", "url_inactivate"), InactivateRakontuPage),
									  (BuildURL("dir_manage", "url_export"), ExportRakontuDataPage),
									  (BuildURL("dir_manage", "url_export_search"), ExportSearchPage),
									  
									  # site admin
									  (BuildURL("dir_admin"), AdministerSitePage),
									  (BuildURL("dir_admin", extraSlash=True), AdministerSitePage),
									  (BuildURL("dir_admin", "url_admin"), AdministerSitePage),
									  (BuildURL("dir_admin", "url_create1"), CreateRakontuPage_PartOne),
									  (BuildURL("dir_admin", "url_create2"), CreateRakontuPage_PartTwo),
									  (BuildURL("dir_admin", "url_sample_questions"), GenerateSampleQuestionsPage),
									  (BuildURL("dir_admin", "url_default_resources"), GenerateSystemResourcesPage),
									  (BuildURL("dir_admin", "url_helps"), GenerateHelpsPage),
									  (BuildURL("dir_admin", "url_skins"), GenerateSkinsPage),
									  
									  # for testing
									  (BuildURL("dir_admin", "url_make_fake_data"), GenerateFakeDataPage),
									  (BuildURL("dir_admin", "url_stress_test"), GenerateStressTestPage),
									  
									  # file handlers
									  (BuildURL(None, "url_image"), ImageHandler),
									  (BuildURL("dir_visit", "url_image"), ImageHandler),
									  (BuildURL("dir_manage", "url_image"), ImageHandler),
									  (BuildURL(None, "url_attachment"), AttachmentHandler),
									  (BuildURL("dir_visit", "url_attachment"), AttachmentHandler),
									  (BuildURL(None, "url_export"), ExportHandler),
									  ],
									 debug=False)

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
	
