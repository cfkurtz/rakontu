# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.

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

urlInfo = [('/', StartPage),
	  # looking at objects
	  (HOME, BrowseEntriesPage),
	  (BuildURL(None, "url_home"), BrowseEntriesPage),
	  (BuildURL("dir_visit"), BrowseEntriesPage),
	  (BuildURL("dir_visit", extraSlash=True), BrowseEntriesPage),
	  (BuildURL("dir_visit", "url_filter"), FilterEntryPage),
	  (BuildURL("dir_visit", "url_find"), SimpleSearchPage),
	  (BuildURL("dir_visit", "url_read"), ReadEntryPage),
	  (BuildURL("dir_visit", "url_read_annotation"), ReadAnnotationPage),
	  # looking at people
	  (BuildURL("dir_visit", "url_members"), SeeRakontuMembersPage),
	  (BuildURL("dir_visit", "url_message"), SendMessagePage),
	  (BuildURL("dir_visit", "url_member"), SeeMemberPage),
	  (BuildURL("dir_visit", "url_character"), SeeCharacterPage),
	  (BuildURL("dir_visit", "url_rakontu"), SeeRakontuPage),
	  # membership
	  (BuildURL("dir_visit", "url_new"), NewMemberPage),
	  (BuildURL("dir_visit", "url_profile"), ChangeMemberProfilePage),
	  (BuildURL("dir_visit", "url_nickname"), ChangeMemberNicknamePage),
	  (BuildURL("dir_visit", "url_preferences"), ChangeMemberPreferencesPage),
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
	  (BuildURL("dir_visit", "url_attachments"), ManageEntryAttachmentsPage),
	  (BuildURL("dir_visit", "url_attachment"), AddOneAttachmentPage),
	  (BuildURL("dir_visit", "url_editors"), ManageAdditionalEntryEditorsPage),
	  # answering questions
	  (BuildURL("dir_visit", "url_answers"), AnswerQuestionsAboutEntryPage),
	  (BuildURL("dir_visit", "url_preview"), PreviewPage),
	  (BuildURL("dir_visit", "url_preview_answers"), PreviewAnswersPage),
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
	  (BuildURL("dir_liaise", "url_print_filter"), PrintFilteredItemsPage),
	  (BuildURL("dir_liaise", "url_print_entry"), PrintEntryAnnotationsPage),
	  (BuildURL("dir_liaise", "url_print_member"), PrintMemberEntriesAndAnnotationsPage),
	  (BuildURL("dir_liaise", "url_print_character"), PrintCharacterEntriesAndAnnotationsPage),
	  # managing
	  (BuildURL("dir_manage", "url_first"), FirstOwnerVisitPage),
	  (BuildURL("dir_manage"), ManageRakontuSettingsPage),
	  (BuildURL("dir_manage", extraSlash=True), ManageRakontuSettingsPage),
	  (BuildURL("dir_manage", "url_members"), ManageRakontuMembersPage),
	  (BuildURL("dir_manage", "url_invitation_message"), SendInvitationMessagePage),
	  (BuildURL("dir_manage", "url_appearance"), ManageRakontuAppearancePage),
	  (BuildURL("dir_manage", "url_skin"), ManageRakontuSkinPage),
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
	  (BuildURL("dir_manage", "url_question"), ManageOneQuestionPage),
	  (BuildURL("dir_manage", "url_unlinked_answers"), FixHangingAnswersPage),
	  (BuildURL("dir_manage", "url_questions_to_csv"), WriteQuestionsToCSVPage),
	  (BuildURL("dir_manage", "url_characters"), ManageCharactersPage),
	  (BuildURL("dir_manage", "url_character"), ManageCharacterPage),
	  (BuildURL("dir_manage", "url_availability"), SetRakontuAvailabilityPage),
	  (BuildURL("dir_manage", "url_export"), ExportRakontuDataPage),
	  (BuildURL("dir_manage", "url_export_filter"), ExportFilteredItemsPage),
	  # site admin
	  (BuildURL("dir_admin"), AdministerSitePage),
	  (BuildURL("dir_admin", extraSlash=True), AdministerSitePage),
	  (BuildURL("dir_admin", "url_admin"), AdministerSitePage),
	  (BuildURL("dir_admin", "url_create1"), CreateRakontuPage_PartOne),
	  (BuildURL("dir_admin", "url_create2"), CreateRakontuPage_PartTwo),
	  (BuildURL("dir_admin", "url_sample_questions"), GenerateSampleQuestionsPage),
	  (BuildURL("dir_admin", "url_default_resources"), GenerateSystemResourcesPage),
	  (BuildURL("dir_admin", "url_recopy_system_resource"), RecopySystemResourcePage),
	  (BuildURL("dir_admin", "url_helps"), GenerateHelpsPage),
	  (BuildURL("dir_admin", "url_skins"), GenerateSkinsPage),
	  (BuildURL("dir_admin", "url_confirm_remove_rakontu"), ConfirmRemoveRakontuPage),
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
	  # errors and other exceptional situations
	  (BuildURL(None, "url_not_found"), NotFoundPageHandler),
	  (BuildURL(None, "url_role_not_found"), RoleNotFoundPageHandler),
	  (BuildURL(None, "url_no_member"), NoActiveMemberPageHandler),
	  (BuildURL(None, "url_no_rakontu"), NoRakontuPageHandler),
	  (BuildURL(None, "url_rakontu_not_available"), RakontuNotAvailablePageHandler),
	  (BuildURL(None, "url_managers_only"), ManagersOnlyPageHandler),
	  (BuildURL(None, "url_owners_only"), OwnersOnlyPageHandler),
	  (BuildURL(None, "url_admin_only"), AdminOnlyPageHandler),
	  (BuildURL(None, "url_database_error"), DatabaseErrorPageHandler),
	  (BuildURL(None, "url_attachment_too_large"), AttachmentTooLargePageHandler),
	  (BuildURL(None, "url_attachment_wrong_type"), AttachmentWrongTypeErrorPageHandler),
	  (BuildURL(None, "url_transaction_failed"), TransactionFailedPageHandler),
	  ]

application = webapp.WSGIApplication(urlInfo, debug=True)

def real_main():
	run_wsgi_app(application)
	
def profile_randomly_main():
	# every once in a while, profile a page in use, to see how things are going
	if random.randint(0, 100) == 4:
		profile_log_main()
	else:
		real_main()

def profile_log_main():
	 import cProfile, pstats, StringIO
	 prof = cProfile.Profile()
	 prof = prof.runctx("real_main()", globals(), locals())
	 stream = StringIO.StringIO()
	 stats = pstats.Stats(prof, stream=stream)
	 stats.sort_stats("time")  # Or cumulative
	 stats.print_stats(80)  # 80 = how many to print
	 # stats.print_callees()
	 # stats.print_callers()
	 logging.info("Profile data:\n%s", stream.getvalue())
	 
def profile_html_main():
	 import cProfile, pstats
	 prof = cProfile.Profile()
	 prof = prof.runctx("real_main()", globals(), locals())
	 print "<pre>"
	 stats = pstats.Stats(prof)
	 stats.sort_stats("time")  # Or cumulative
	 stats.print_stats(80)  # 80 = how many to print
	 # stats.print_callees()
	 # stats.print_callers()
	 print "</pre>"
	 
#main = profile_html_main
main = real_main
#main = profile_randomly_main

if __name__ == "__main__":
	main()
	
