# tagged_bookmarks_export_tool - introduction
Exports HTML file of bookmarks only tagged with a specific tag or pair of tags - relies on the places.sqlite file from a Firefox browser profile (and those bookmarks actually being tagged in the browser - a feature of the Firefox browser compared to some other well-known web browsers). 

Why use this? One might have built a library of tagged bookmarks & want to share only the bookmarks tagged with a particular tag. One can copy multiple URLs at once from Firefox bookmark manager - however this is URLs only with no descriptive text. Using the https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3048994 URL seen in screenshot as an example it is hard to discern from a glance at the URL what it is about so sharing it as [Lateral Reading: Reading Less and Learning More When Evaluating Digital Information by Sam Wineburg, Sarah McGrew :: SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3048994) could be more useful - especially if sharing a lot of quite similar looking URLs such as links to social media or https://www.ncbi.nlm.nih.gov/pmc article links.

![Screenshot of export tool showing main window with checkboxes for each tag and dual tag combination and two open windows of resulting HTML bookmarks](https://github.com/byjosh/tagged_bookmarks_export_tool/blob/main/Screenshot_tagged_bookmarks_export_tool.png?raw=true)

## Installation
Requires Python3 and wxPython. The following commands will 
1. clone the repository,
2.  create a Python virtual environment, 
3. change into the directory
4. activate the virtual environment
5. use pip to install requirements
6. run source version 

 and should work on MacOS.
In GNU/Linux environments rather than using a virtual environment install a python 3 wxPython 4 package may be faster.
So you would use lines 1 (clone repository), 3 (change into directory) and 6 (run the source version of program) after installing appropriate package (e.g. [python3-wxpython4 (tested & works with this script)](https://packages.fedoraproject.org/pkgs/python-wxpython4/python3-wxpython4/) or [wxpython4 (not tested but from name appears seems likely package)](https://packages.debian.org/stable/source/wxpython4.0) or similar depending on your choice of Linux distribution)

```
  git clone https://github.com/byjosh/tagged_bookmarks_export_tool.git
  python3 -m venv tagged_bookmarks_export_tool
  cd tagged_bookmarks_export_tool
  source bin/activate
  pip install -r requirements.txt
  python3 tagged_bookmarks_export_tool.py
```

In a Windows PowerShell environment the following should work (`python3.12.exe` may have different version number or simply be `python.exe` in your setup).
```
git clone https://github.com/byjosh/tagged_bookmarks_export_tool.git
python3.12.exe -m venv .\tagged_bookmarks_export_tool
cd .\tagged_bookmarks_export_tool
.\Scripts\Activate.ps1
python3.12.exe -m pip install -r requirements.txt
python3.12.exe .\tagged_bookmarks_export_tool.py
```

One can make binaries - but if you have Python and Git installed it is easy enough to run from source - and for anyone capable of reading Python it would seem better to be able to check the code - than the user having to trust an unsigned binary or me going to the trouble of making signed binaries.

## Tests
Not that many tests but I am using [doctest](https://docs.python.org/3/library/doctest.html) from Python standard library to put in a few examples and there is a places.sqlite file for demonstration/testing purposes.

## Wishlist
Given unlimited time & expertise:
 * keyboard navigation (in general helps users with disabilities) - already good if running this on Windows or Linux
 * internationalisation (broadens use beyond non-English speakers)
 * better copy/paste functionality
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
        <p>Firefox is a trademark of the Mozilla Foundation in the U.S. and other countries. Safari is a trademark of Apple Inc. Chrome is a trademark of Google LLC.</p>
