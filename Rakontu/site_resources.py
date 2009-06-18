SYSTEM_INTRO_RESOURCE = [u"About Rakontu", u"Wiki markup", 
u"""
= About Rakontu

Rakontu is a web application that helps groups, communities, and families share and work with stories. 

=== What it's for

Rakontu is for small groups of people (usually fewer than 50) who have something they would like to share 
experiences about: something they do together, a place they live in, a history they share. A Rakontu site is 
both a living history museum and a gathering place to share what's going on. 

=== What you can do

These are the things you can do on a Rakontu web site:

  * You can tell stories, and people can comment on them, answer questions about them, describe them with 
tags, ask questions about them, and rate them on issues important to the community. 
  * You can ask other people to tell stories about things you want to hear about.
  * You can look for stories in many different ways. If you see an interesting pattern, you can save it and ask 
other people to comment on it.
  * You can build story collages, assemblages of stories you want to remember or present for a reason.

=== Doing more

If you like, you can take on a *helping role* in your community.

  * *Curators* watch over the living museum of stories, making sure they are clean and well connected.
  * *Guides* help other people use the system and encourage people to participate in the community.
  * *Liaisons* provide bridges between on-line members of the community (people who use the web site) 
and off-line members (people who tell and hear stories but don't use the web site).

To get started, click on a story title and start reading!
"""]

SYSTEM_WIKI_MARKUP_RESOURCE = [u"Wiki markup in Rakontu", u"simple HTML",
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

SYSTEM_SIMPLE_HTML_RESOURCE = [u"Simple HTML in Rakontu", u"Wiki markup",
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

SYSTEM_TERMS_RESOURCE = [u"Terms in Rakontu", u"Wiki markup",
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

  * *Resources* are things put into the system to help people participate in the community, either to help them tell 
  stories or to provide useful information. Resources might include getting started guides as well as information about 
  a geographical community or pictures related to a subject.

== Annotations

Annotations are things that surround entries for the purpose of discussion and collective awareness.

  * *Comments* are just things people wanted to say in reaction to a story (or invitation, collage, pattern, or resource). 
  These will be familiar to people who have used any online community software.

  * *Requests* are a special kind of comment that asks other people to do something related to an entry -- translate a story 
  to another language, read a story out loud, transcribe an audio story, or just add some comments.

  * *Nudges* are ratings. When a community member nudges a story or other entry up or down, everyone sees the entry as 
  higher or lower in their main community page. The nudge system is similar to SlashDot's karma system, in that people gain 
  nudge points by participating in the community and can use them to nudge entries up or down. The main difference between 
  Rakontu's rating system and others, however, is that the community can define up to five _categories_ of nudges. This helps 
  people distinguish between entries that are useful for different reasons.

  * *Tags* on entries can be used to build an open-ended and changing set of descriptors for finding helpful things.

== Answers

Each type of entry (story, invitation, collage, pattern, resource) has a set of questions you can answer about them. 
The creator of the entry _and_ everyone else in the community can answer the same questions. Looking at differences of 
opinion about stories can be a useful way to think about issues in the community. It's also a great way to find stories 
you are interested in reading.

Members can also have questions they answer. These answers can be combined with questions about stories to produce 
interesting queries, like "Show me stories told by members under 20 in which people said they felt sad."

"""]

SYSTEM_PEOPLE_RESOURCE = [u"People in Rakontu", u"Wiki markup",
u"""
= People in Rakontu

== Members

Everyone who has access to a Rakontu site is a *member* of the community. All members can tell stories, ask other people 
to tell stories, build collages and note patterns. All members can tag, comment on, add a request to, 

=== Managers

Some of the people in the community are managers. These are the people who can change all of the governance-type 
settings in the community, such as what questions are asked about entries and members. Managers must be made managers 
by other managers.

=== Owners

At least one manager is called an owner. The only additional thing an owner can do is delete the community 
(so this person has to be trustworthy!). Usually the owner will be the person who started the community.

=== Helpers

There are three "helping roles" in any Rakontu community. These are always volunteer roles, and any member can take them 
on simply by checking a box that says they want to do this. (However, managers can ban a member from doing this if 
they need to, for example if someone abuses the privileges of the role.)

  * *Curators* are the herders of the stories and other information. They have the right to roam over the web site flagging 
  inappropriate items for deletion. They have several summary screens they can use to review missing links and other gaps 
  in the data set.

  * *Guides* are the people-helpers of the system. They alone can create resources, and they can review requests attached
  to entries, such as those needing transcription. When people need help, they can ask a guide.

  * *Liaisons* are bridges between on-line and off-line members of a community. Off-line members can tell stories,
  read and hear stories, and make comments and other annotations. Liaisons enter all of this information for them
  and output things for them to read and hear. 

=== Characters

Sometimes it's hard to tell a story that needs to be told. Communities can optionally set up characters, which are 
sort of like masks people can put on to tell a story they would rather not have labeled as theirs. Information about who 
told the story is still in the system, but nobody in the community (including its managers) can see it. Only a site 
administrator can see identifying information, and only with some effort. Characters have answers to questions as well, 
so you can search on things like "Show me stories told by characters that describe themselves as 'strong' where the 
storyteller said the story made them feel 'weak'."

Communities may vary on whether they have characters and which types of entries and annotations are allowed to use 
character attribution.

"""]

SYSTEM_RESOURCES = [
				SYSTEM_INTRO_RESOURCE, 
				SYSTEM_TERMS_RESOURCE, 
				SYSTEM_PEOPLE_RESOURCE,
				SYSTEM_WIKI_MARKUP_RESOURCE, 
				SYSTEM_SIMPLE_HTML_RESOURCE,
				]

