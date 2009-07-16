# --------------------------------------------------------------------------------------------
# RAKONTU
# Description: Rakontu is open source story sharing software.
# Version: pre-0.1
# License: GPL 3.0
# Google Code Project: http://code.google.com/p/rakontu/
# --------------------------------------------------------------------------------------------

# These are site-wide system resources, mainly help resources, that all Rakontus in the installation get 
# when they are created. (If some Rakontus don't want the resources, they can flag and delete them after creation.)

SYSTEM_INTRO_RESOURCE = [u"About Rakontu", u"Wiki markup", False, # boolean is whether it is for managers/owners only
u"""
= About Rakontu

Rakontu is a web application that helps groups, communities, and families share and work with stories. 

=== What it's for

Rakontu is for small groups of people (usually fewer than 50) who have something they would like to share 
experiences about: something they do together, a place they live in, a history they share. A Rakontu is 
both a living history museum and a gathering place to share what's going on. 

=== What you can do

These are the things you can do in a Rakontu:

  * You can tell stories, and people can comment on them, answer questions about them, describe them with 
    tags, ask questions about them, and rate them on issues important to the Rakontu. 
  * You can ask other people to tell stories about things you want to hear about.
  * You can look for stories in many different ways. If you see an interesting pattern, you can save it and ask 
    other people to comment on it.
  * You can build story collages, which are assemblages of stories you want to remember or present for a reason.

=== Doing more

If you like, you can take on a *helping role* in your Rakontu.

  * *Curators* watch over the living museum of stories, making sure they are clean and well connected.
  * *Guides* help other people use the system and encourage people to participate in the Rakontu.
  * *Liaisons* provide bridges between on-line members of the Rakontu (people who use the web site) 
    and off-line members (people who tell and hear stories but don't use the web site).

To get started, click on a story title and start reading!
"""]

SYSTEM_WIKI_MARKUP_RESOURCE = [u"Wiki markup in Rakontu", u"simple HTML", False, # boolean is whether it is for managers/owners only
u"""
<h1>Wiki markup in Rakontu</h1>

<p>You can use wiki-style markup in almost all the large text boxes in Rakontu (all those that have an "interpret as" choice).</p>

<p>Separate paragraphs with blank lines.</p>

<p>To write bold text, put asterisks around it: *bold text* becomes <b>bold text</b>.</p>

<p>To write italic text, put underscores around it: _italic text_ becomes <i>italic text</i>.</p>

<p>To write fixed-width text, put those little hat characters around it: ^code text^ becomes <code>text</code>.</p>

<p>To write struck-out text, put tildes around it: ~strikeout text~ becomes <del>text</del>.</p>

<p>To write a heading, put one equals sign at the start of the line, followed by a space: </p><p>= header 1 text</p><p>
becomes <h1>&nbsp; &nbsp; header 1 text</h1><p>

<p>To write a sub-heading, put two equals signs: </p><p>== header 2 text</p><p>becomes <h2>&nbsp; &nbsp; header 2 text</h2></p>

<p>To write a third-level heading, put three equals signs: </p><p>=== header 3 text</p><p>becomes <h3>&nbsp; &nbsp; header 3 text</h3></p>

<p>To write an unordered (bullet) list item, put an asterisk with two spaces before it. Keep two spaces in front of every line
in each list item (if they spill over), thus:</p><p>&nbsp; * unordered list item</p><p>&nbsp; continuation of line</p><p>
becomes <ul><li>unordered list item continuation of line</li></ul> </p>

<p>To write an ordered (numbered) list item, put a pound sign with two spaces before it. Keep two spaces in front of every line
in each list item (if they spill over), thus:</p><p>&nbsp; # ordered list item</p><p>&nbsp; continuation of  line</p><p>
becomes <ol><li>ordered list item continuation of line</li></ol> </p>

<p>To write a horizontal line (hr), put four or more dashes on a line by themselves:</p><p>----</p><p>becomes</p><p><hr></p>

<p>To write a link, put square brackets around it: [http://www.rakontu.org] 
becomes <a href="http://www.rakontu.org">http://www.rakontu.org</a></p>

<p>To write a named link, put the name in parentheses after the link but inside the 
square brackets: [http://www.rakontu.org(Rakontu)] becomes <a href="http://www.rakontu.org">Rakontu</a></p>

<p>To include an URL-based inline picture link, place the link in curly brackets, and include an alt tag in 
parentheses: {http://www.rakontu.org/Rakontu.jpg(Rakontu picture)} 
becomes <img src="http://www.rakontu.org/Rakontu.jpg" alt="Rakontu picture"/>

<p>To refer to an attachment within the text of an entry, put pound signs around the number of the attachment, like this: #1# or #2#. 
If the attachment is an image it will be shown in the document where you put the pound signs. If the attachment is another
kind of file (pdf, etc) a link will appear there that people can click on to download the file.</p>

<p>&nbsp; </p>
<p>Tables and nested lists are not supported.
"""]

SYSTEM_SIMPLE_HTML_RESOURCE = [u"Simple HTML in Rakontu", u"Wiki markup", False, # boolean is whether it is for managers/owners only
u"""
You can enter these simple HTML elements into any Rakontu text box:

<p>paragraph</p>

<b>bold</b>

<i>italic</i>

<del>strikeout</del>

<code>code</code>

<ul> <li>...<li> </ul>

<ol> <li>...<li> </ol>

<h1>header 1</h1>

<h2>header 2</h2>

<h3>header 3</h3>

line ending <br/>

<hr>

non-breaking space &nbsp; 

links <a href=""></a>

image tags <img src="" alt=""/> (these MUST include alt tags)

Tables and nested lists are not supported.

"""]

SYSTEM_TERMS_RESOURCE = [u"Terms in Rakontu", u"Wiki markup", False, # boolean is whether it is for managers/owners only
u"""
= Terms in Rakontu

There are three main types of object in Rakontu: entries, answers and annotations.

== Entries

Entries are the most important items in Rakontu. They are sort of like Wikipedia articles in that everything "hangs off" them. 
Most entries will be stories; but there are also four other kinds of entry.

  * *Invitations* are story solicitations. They propose topics for people to tell stories about.

  * *Collages* are groupings of stories. People may have many reasons to group stories together and highlight them. 
  In Rakontu 1.0 collages are just simple annotated lists of stories. Future versions are envisioned in which collages 
  can be time lines, composite stories, and other more complex groupings.

  * *Patterns* are observations about stories that have been told, usually together with answers to questions about them. 
  Patterns might be things like "I noticed that people over 60 were more likely to tell stories about hats, while people under 
  30 were more likely to tell stories about cats." While a collage is essentially an annotated list of stories, a pattern is 
  an annotated list of queries.

  * *Resources* are things put into the system to help people participate in the Rakontu, either to help them tell 
  stories or to provide useful information. Resources might include getting started guides as well as information about 
  a geographical community or pictures related to a subject.

== Annotations

Annotations are things that surround entries for the purpose of discussion and collective awareness.

  * *Comments* are just things people wanted to say in reaction to a story (or invitation, collage, pattern, or resource). 
  These will be familiar to people who have used any online community software.

  * *Requests* are a special kind of comment that asks other people to do something related to an entry -- translate a story 
  to another language, read a story out loud, transcribe an audio story, or just add some comments.

  * *Nudges* are ratings. When a Rakontu member nudges a story or other entry up or down, everyone sees the entry as 
  higher or lower in their Rakontu's home page. The nudge system is similar to SlashDot's karma system, in that people gain 
  nudge points by participating in the Rakontu and can use them to nudge entries up or down. The main difference between 
  Rakontu's rating system and others, however, is that the Rakontu can define up to five _categories_ of nudges. This helps 
  people distinguish between entries that are useful for different reasons.

  * *Tags* on entries can be used to build an open-ended and changing set of descriptors for finding helpful things.

== Answers

Each type of entry (story, invitation, collage, pattern, resource) has a set of questions you can answer about them. 
The creator of the entry _and_ everyone else in the Rakontu can answer the same questions. Looking at differences of 
opinion about stories can be a useful way to think about issues in the Rakontu. It's also a great way to find stories 
you are interested in reading.

Members can also have questions they answer. These answers can be combined with questions about stories to produce 
interesting queries, like "Show me stories told by members under 20 in which people said they felt sad."

"""]

SYSTEM_PEOPLE_RESOURCE = [u"People in Rakontu", u"Wiki markup", False, # boolean is whether it is for managers/owners only
u"""
= People in Rakontu

== Members

Everyone who has access to a Rakontu site is a *member* of the Rakontu. All members can tell stories, ask other people 
to tell stories, build collages and note patterns. All members can tag, comment on, add a request to, 

=== Managers

Some of the people in the Rakontu are managers. These are the people who can change all of the governance-type 
settings in the Rakontu, such as what questions are asked about entries and members. Managers must be made managers 
by other managers.

=== Owners

At least one manager is called an owner. The only additional thing an owner can do is delete the Rakontu 
(so this person has to be trustworthy!). Usually the owner will be the person who started the Rakontu.

=== Helpers

There are three "helping roles" in any Rakontu. These are always volunteer roles, and any member can take them 
on simply by checking a box that says they want to do this. (However, managers can ban a member from doing this if 
they need to, for example if someone abuses the privileges of the role.)

  * *Curators* are the herders of the stories and other information. They have the right to roam over the web site flagging 
  inappropriate items for deletion. They have several summary screens they can use to review missing links and other gaps 
  in the data set.

  * *Guides* are the people-helpers of the system. They alone can create resources, and they can review requests attached
  to entries, such as those needing transcription. When people need help, they can ask a guide.

  * *Liaisons* are bridges between on-line and off-line members of a Rakontu. Off-line members can tell stories,
  read and hear stories, and make comments and other annotations. Liaisons enter all of this information for them
  and output things for them to read and hear. 

=== Characters

Sometimes it's hard to tell a story that needs to be told. Rakontus can optionally set up characters, which are 
sort of like masks people can put on to tell a story they would rather not have labeled as theirs. Information about who 
told the story is still in the system, but nobody in the Rakontu (including its managers) can see it. Only a site 
administrator can see identifying information, and only with some effort. Characters have answers to questions as well, 
so you can search on things like "Show me stories told by characters that describe themselves as 'strong' where the 
storyteller said the story made them feel 'weak'."

Rakontus may vary on whether they have characters and which types of entries and annotations are allowed to use 
character attribution.

"""]

SYSTEM_CURATOR_RESOURCE = [u"How to be a curator", u"Wiki markup", False, # boolean is whether it is for managers/owners only
u"""
Curating a Rakontu means helping to tend the museum of stories (and things that surround them). Are the stories
and other information in good order? Is it all as useful as it could be? Can people find what they need when they need it?
Are there loose ends, broken links, dead wood?  People who like organizing "stuff" are good curators. 

There are three main activities you might do as a curator: filling gaps, flagging things that should be removed, and 
maintaining consistency.

= Filling gaps

As a curator you should look around the Rakontu frequently just checking on activity. The Gaps page (Curate->Gaps) can help you 
find places that might need attention. These are the things listed on the Gaps page.

  # *Untagged entries*. Entries with no tags are less likely to be found when people are searching on tags. Filling these in, especially
  for items with high nudge values (therefore important or useful) or high activity, 
  will help the whole set of entries become more useful.
  # *Unlinked entries*. Links between entries help people go from one story to another finding things that are useful in different
  ways. One of the most helpful things curators can do is notice similarities between stories and link them together
  so that people can move from one to another. 
  # *Entries with no answers to questions*. As with tags, entries that have no answers to questions are harder to find. If the teller of the story didn't answer any questions about it, you can still answer some as a curator. 
  # *Collages with no links to stories*. Collages with no story links might have linked to stories that have been removed from the system. These should either be removed or updated.

= Flagging items

You can flag every type of entry (story, invitation, collage, pattern, resource), annotation (comment, request, tag set,
nudge) and answer, as well as search filters.

To flag an entry or any of its annotations or answers, click on the entry on the Rakontu's home
page, then choose "Curate this story" (or invitation, etc) from the "What would you like to do next?" drop-down list.
After you click "Go," the page will redisplay with little green flags next to each item. Click any flag to mark the
item as inappropriate or unhelpful. 

To flag a search filter, select it on the home page, then click Change. In the page that shows the details
of the filter, click Flag.

To view all of the flags you have marked, choose Flags from the Curate menu at the top of the page. 
  * If you are a manager of the Rakontu, you can either unflag items or remove them from the Rakontu. 
  * If you are not a manager, you can unflag items or notify the Rakontu manager(s) that the items should be removed. 
  Notification is mainly to let managers know if something is particularly in need of removal (obscene or hate speech, for example). 
  It's best not to over use notification if you want the managers to pay attention when you _do_ need to get their attention.
  
=== Flagging items through attachments

Because entries can have attachments (like email) it can sometimes be hard to see if someone has added something
offensive or just huge and not helpful. (Many large attachments can slow down access to the Rakontu.) It's a good
idea to keep an eye on attachments in a separate list. To review attachments, choose Curate->Attachments. You can then
flag the entry that goes with any attachment as needing review.

= Maintaining tags

Rakontu managers can decide whether they want curators (meaning, everybody) to be able to be change the tags on
existing entries. This is very useful if you want to maintain consistency in your tags, for example fixing misspellings
and changing plurals (like "cats" to "cat") so that tags match up during searches. However, if your Rakontu is
particularly large or widespread your managers may have decided not to allow this. Check your Curate menu
to see if there is a Tags option there. If there isn't and you want one, ask a manager about it. 
"""]

SYSTEM_GUIDE_RESOURCE = [u"How to be a guide", u"Wiki markup", False, # boolean is whether it is for managers/owners only
u"""
Being a Rakontu guide means paying attention to the people side of things. Are people getting what they want out of it?
Are they confused? Are they interested? Motivated? Contributing? People who are "people people" are good guides.

There are three main things guides do: answer questions, help people find their way around, and monitor responses.

= Answering questions

First: all guides must be willing to accept emails from the Rakontu and be listed on the Help page to answer
questions people have about the Rakontu.

When you become a guide, you should enter a paragraph or so into your preferences page that tells people
what sorts of questions you can answer well. Perhaps you know a lot about the history of your community,
or you are a "techie" and can help them with system problems, or you can help them write good stories.
Writing a good *guide introduction* can help people find the answers they need, and it can help you
avoid getting questions you can't answer or find boring. 

= Helping people find their way around

Rakontu guides are in charge of on-line help for Rakontu members. As a guide, you can 
create and maintain *resources* that help people find their way around and contribute to your Rakontu
in a positive way. For example,
maintaining a frequently-asked-questions list about how your group works is a good way to help
people who have questions like "What sorts of nicknames are people supposed to use?" and
"How many shared search filters should I make?" and so on. A "news" resource that highlights the latest activity
is also helpful. To review your resources, choose Resources from the Guide menu.

= Monitoring responses

There are two main types of response in Rakontu: telling a story in response to an invitation, and doing something
in response to a request about a particular story (or other type of entry). For example, people might ask
others to transcribe an audio story, read a written story out loud, translate a story into another language,
and so on. As a guide, you will want to
check on whether there are invitations or requests that have been "orphaned" and need some attention. 

To review invitations or requests, choose one of these items in your Guide menu. You can either look only
at invitations or requests with no reponses or all of them. For requests, you can mark them as completed
if you see that they have been satisfied.
"""]

SYSTEM_LIAISON_RESOURCE = [u"How to be a liaison", u"Wiki markup", False, # boolean is whether it is for managers/owners only
u"""
Being a liaison CFK FINISH
"""]

SYSTEM_MANAGING_RESOURCE = [u"How to manage a Rakontu", u"Wiki markup", True, # boolean is whether it is for managers/owners only
u"""
Here is how you do it. CFK FINISH
"""]

SYSTEM_RESOURCES = [
				SYSTEM_INTRO_RESOURCE, 
				SYSTEM_TERMS_RESOURCE, 
				SYSTEM_PEOPLE_RESOURCE,
				SYSTEM_WIKI_MARKUP_RESOURCE, 
				SYSTEM_SIMPLE_HTML_RESOURCE,
				SYSTEM_CURATOR_RESOURCE, 
				SYSTEM_GUIDE_RESOURCE, 
				SYSTEM_LIAISON_RESOURCE,
				SYSTEM_MANAGING_RESOURCE,
				]

