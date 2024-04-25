# tagged_bookmarks_export_tool - introduction
Exports HTML file of bookmarks only tagged with a specific tag or pair of tags - relies on the places.sqlite file from a Firefox browser profile (and those bookmarks actually being tagged in the browser - a feature of the Firefox browser compared to some other well-known web browsers). Why use this? One might have built a library of tagged bookmarks & want to share only the bookmarks tagged with a particular tag - regardless of folder - whereas with most browsers the export format is an HTML file of all bookmarks - which one would then have to manually edit to leave just those bookmarks in the relevant folder.

![Screenshot of export tool showing main window with checkboxes for each tag and dual tag combination and two open windows of resulting HTML bookmarks](https://github.com/byjosh/tagged_bookmarks_export_tool/blob/main/Screenshot_tagged_bookmarks_export_tool.png?raw=true)

## Installation
Requires Python3 and wxPython. The following commands will clone the repository, create a virtual environment, and run source version (should work on MacOS and GNU/Linux environments - in 
Windows PowerShell you would have for instance a slightly different command in place of `source bin/activate`  of `.\Scripts\Activate.ps1` and `pip install -r requirements` would likely be `python.exe -m pip install -r requirements` (should check for commands for installing Python packages using pip and virtual environments on operating system you are using).

```
  git clone https://github.com/byjosh/tagged_bookmarks_export_tool.git
  python3 -m venv tagged_bookmarks_export_tool
  cd tagged_bookmarks_export_tool
  source bin/activate
  pip install -r requirements.txt
  python3 tagged_bookmarks_export_tool.py
```

One can make binaries - but if you have Python and Git installed it is easy enough to run from source - and for anyone capable of reading Python it would seem better to be able to check the code - than the user having to trust an unsigned binary or me going to the trouble of making signed binaries.

## Tests
Not that many tests but I am using [doctest](https://docs.python.org/3/library/doctest.html) from Python standard library to put in a few examples and there is a places.sqlite file for demonstration/testing purposes.

## Wishlist
Given unlimited time & expertise:
 * Keyboard navigation (helps users with disabilities)
 * Internationalisation (broadens use beyond non-English speakers) 
would be top of list.

For now just grateful that thanks to Python and wxPython & wxWidgets a cross platform GUI in a nice, native style seems not too much work.

## Licensing
This relies on [wxPython](https://wxpython.org/) and GPLv2 is very compatible with [the wxPython license](https://wxpython.org/pages/license/) (which seems to be GPLv2 with an exception to allow binaries to be distributed on any terms. So licensing my source here under GPLv2 seemed the easy choice.

## Use
From the help file
        <h3>Workflow</h3>
        <ol>
        <li><p>Find places.sqlite from your Firefox browser profile (see <a href="https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data">https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data</a>)</p></li>
        <li><p>Open it with this tool via File &gt; Open in menu</p></li>
        <li><p>Check checkbox by tag name to show bookmarks with that tag.</p></li>
        <li><p>In window that appears: click on the links to visit link in default browser or click "Save as HTML file" link to export window contents as HTML</p></li>
        <li><p>Use "Append categories for items tagged with 2 tags" checkbox before or after file opening to have shown after single tag checkboxes the checkboxes for those tagged with at least two (e.g. tag A & tag B). Use of window that appears is same as for single tag bookmarks.</p></li>
        </ol>\
        <h3>Rationale</h3>
        <p>Firefox browser exports bookmarks as a single HTML file with folders as the organising principle. In Firefox browser you can tag bookmarks in addition to choosing a folder location - and exporting by tag offers more flexibility to export just some of your bookmarks - including those with the same tag but in different folders.</p>
        <h3>Example</h3>
        <p>As an example of utility of using tags and this tool: suppose you bookmark pages about books for 3 reasons: 1) you want to read them yourself, 2) you are research the book as present for another person 3) you used or researched the book as a source for something you wrote such as a thesis. In all cases you could put them in an appropriate folder - but without tags you could not export all three combined. With tags: a common tag of e.g. "book" would allow export of a single list with all bookmarks tagged "book" regardless of folder, using two tags e.g. "book" as the common tag and a specific tag e.g. "to_buy", "for_mom", "thesis" (related to oneself, or books for one\'s mom, or one\'s thesis as appropriate) would - using the two tag combo option of this tool - allow you export a list of just the bookmarks labelled, in this example, "book" and "thesis" - showing only those bookmarks you marked as books related to your thesis.</p>
        <h3>Why is this not relevant to other browsers?</h3>
        <p>Besides the issue of Firefox browser specific bookmarks database structure: others (such as Chrome browser or Safari browser) do not seem to use tags (as at spring 2024) and they export as 1 HTML file organised by folder - the same as current default for bookmarks HTML export from Firefox browser. If one only organises one\'s bookmarks by folder then editing the HTML file exported by your browser is enough to produce a file only of the desired bookmarks. Hence this tool only serves a purpose for tagged bookmarks from Firefox browser.</p>
        <h3>Trademark acknowledgements</h3>
        <p>Firefox is a trademark of the Mozilla Foundation\n in the U.S. and other countries. Safari is a trademark of Apple Inc. Chrome is a trademark of Google LLC.</p>
