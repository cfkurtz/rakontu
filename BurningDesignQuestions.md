I'm just putting here a list of questions that will have a big impact on how Rakontu works and that I/we have to decide early on how they will work, because they need to get into the architecture of the program. (These may be cryptic if you haven't read the architecture document.)

(NOTE: I'm putting in updates for what happened in "later" development for each issue.)

### Multimedia ###

How many non-text elements should be allowed in Rakontu articles (stories, patterns, constructs, invitations, resources)? The way I have it right now is that each article has a plain-text area (of any length) and any number of binary "attachments" which are uploaded by the user from files. Is that too messy? Should it be simplified? For example should only one type be allowed at a time? Or is keeping it open better?

>> For the time being attachments is fine. Ideally this would be greatly expanded in future. However, right now the biggest problem is that the Google App Engine puts practical limits on what can be uploaded, to about 1MB per file.

### Inappropriateness ###

I have it right now that all annotations (comments, tags, answers, requests, nudges) can be marked as inappropriate. After a set number of these they disappear from the screen (this number can be set globally and overridden by users). The question is, should this be separate from the article system in which appropriateness is covered by nudges? Or should articles share in that system? If so, should the appropriateness category removed from nudging?

>> I now have a "flagging" system which is separate from nudging. Only curators can flag items and only managers can delete items. I think it works, though it may be a bit confusing.

### Queries ###

In the query system I am envisioning there are six types of query: free text, tags, answers, members, activities, and links. Is that too complicated? Will that really be useful, or is it overkill? (For details on this see models.py: go to Source-Browse, then click on trunk/Rakontu/models.py)

>> I did trim that down a bit. You can search on free text, tags, and answers (to questions about stories and about their tellers). The activity and link searching were too much, partly because you can get at that info by looking at other things.

### Profiles ###

How much profile info should be in the system? I don't want to rewrite Facebook. Is a text field and image enough? Do people need to put in pictures of themselves? Do they need more fields than that? I'm thinking people can link off to other things...

>> I have only a text field and a picture. No overkill needed...

### Role names ###

Do the roles curator, sustainer, and liaison work? Are there better names?

>> I changed "sustainer" to "guide" but the others are the same. I LIKE them. But maybe I'm just really used to them by now.

### Basement ###

Is the basement (where things "fall off" into not being shown) necessary? Should it be different?

>> I have it, but it doesn't have a name. It's just a display setting, "Hide entries below" x. It works. Overall I've removed names as much as possible, because too much jargon confuses people for no reason.

### What else? ###

... more to come ... please add comments to this page or in the discussion group.