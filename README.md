# tagged_bookmarks_export_tool - introduction
Exports HTML file of bookmarks only tagged with a specific tag or pair of tags - relies on the places.sqlite file from a Firefox browser profile (and those bookmarks actually being tagged in the browser - a feature of the Firefox browser compared to some other well-known web browsers). 

Why use this? One might have built a library of tagged bookmarks & want to share only the bookmarks tagged with a particular tag. This tool allows:
* export as HTML suitable for editing and inclusion in most documents (emails, web page, Markdown docs like this README etc.)
* export as a Netscape Bookmark File Format HTML file - allowing import into another desktop browser (uses slightly different elements &amp; structure hence different to HTML mentioned in point above)
* export to CSV
* with appropriate configuration: export to Google Sheets.

 One can select &amp; copy multiple URLs at once from Firefox bookmark manager (Firefox Library window) - however when pasted those links are all on one line when pasted as HTML into a wordprocessing document (not conveniently separated) or if pasted as plain text this is URLs only with no descriptive text. This tool allows export of bookmarks just for certain tags or tag combinations - and with the descriptive text - using HTML, CSV, and Google Sheets options noted.
 
 Regarding descriptive text: using the https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3048994 URL seen in screenshot as an example it is hard to discern from a glance at the URL what it is about so sharing it as [Lateral Reading: Reading Less and Learning More When Evaluating Digital Information by Sam Wineburg, Sarah McGrew :: SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3048994) could be more useful - especially if sharing a lot of quite similar looking URLs such as links to social media or https://www.ncbi.nlm.nih.gov/pmc article links - hence best to retain descriptive text in addition to the URL if possible.

![Screenshot of export tool showing main window with checkboxes for each tag and dual tag combination and two open windows of resulting HTML bookmarks](https://github.com/byjosh/tagged_bookmarks_export_tool/blob/main/Screenshot_tagged_bookmarks_export_tool.png?raw=true)

## Installation
Requires Python 3 installed and wxPython (on MacOS or Windows operating systems use pip to get wxPython - on Linux it is probably better to install wxPython via distribution specific binary). The following commands will 
1. clone the repository,
2.  create a Python virtual environment, 
3. change into the directory
4. activate the virtual environment
5. use pip to install requirements
6. run source version 

 and should work on MacOS.
```
  git clone https://github.com/byjosh/tagged_bookmarks_export_tool.git
  python3 -m venv tagged_bookmarks_export_tool
  cd tagged_bookmarks_export_tool
  source bin/activate
  pip install -r requirements.txt
  python3 tagged_bookmarks_export_tool.py
```
In GNU/Linux environments rather than using a virtual environment installing a distro specific Python 3 wxPython 4 package may be faster as this will avoid build time.
So of the above you would use lines: 1 (clone repository), 3 (change into directory) and 6 (run the source version of program) after installing appropriate package (e.g. [python3-wxpython4 on Fedora (tested & works with this script)](https://packages.fedoraproject.org/pkgs/python-wxpython4/python3-wxpython4/) or [wxpython4 on Debian (not tested but from name appears seems likely package)](https://packages.debian.org/stable/source/wxpython4.0) or similar depending on your choice of Linux distribution)

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
This relies on [wxPython](https://wxpython.org/) and GPLv2 is very compatible with [the wxPython license](https://wxpython.org/pages/license/) (which seems to be GPLv2 with an exception to allow binaries to be distributed on any terms. So licensing my source here under GPLv2 seemed the easy choice. The text of Apache License Version 2.0 is included as that was the license for some code samples used as basis for implementing export to Google Sheets (noted in appropriate files) - while project license is in the <code>LICENSE</code> file.

## Use
From the help file
        <h2>Workflow</h2>
        <ol>
                <li>
                        <p>Find places.sqlite from your Firefox browser profile (see <a href="https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data">https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data</a>)</p>
                </li>
                <li>
                        <p>Open it with this tool via File &gt; Open in menu</p>
                </li>
                <li>
                        <p>Choose in "Fields" dropdown what fields you want (default is HTML links - &quot;HTML links - as browser bookmarks file&quot; option lacks useful summary info but when saved as HTML is ready to import into a browser)</p>
                </li>
                <li>
                        <p>Make a choice in the "Export format" dropdown to:- view the bookmarks & export HTML (for general use or browser import), save to a CSV file, or export to Google Sheets (see help on configuration re: Google Sheets below).</p>
                </li>
                <li>
                        <p>Check checkbox by tag name to show bookmarks with that tag.</p>
                </li>
                <li>
                        <p>Use "Append categories for items tagged with 2 tags" checkbox before or after file opening to have shown after single tag checkboxes the checkboxes for those tagged with at least two (e.g. tag A & tag B). Use of window that appears is same as for single tag bookmarks.</p>
                </li>
        </ol>
        <h3>Options in HTML window</h3>
        <ul>
                <li>
                        <p> click on the links to visit link in default browser</p>
                </li>
                <li>
                        <p>click "Save as HTML file" link to export window contents as HTML (if you selected &quot;HTML links - as browser bookmarks file&quot; in Fields dropdown in main window then the file saved can be used to import the bookmarks into a browser)</p>
                </li>
                <li>
                        <p>copy plain text to clipboard via mouse &amp; keyboard</p>
                </li>
                <li>
                        <p>copy all bookmarks as HTML to clipboard via clicking link in window present for that purpose</p>
                </li>
        </ul>
        <h3>Difference between &quot;HTML links - as browser bookmarks file&quot; and other HTML options in Fields dropdown</h3>
        <p>&quot;HTML links - as browser bookmarks file&quot; format</p>
        <ol>
                <li>conforms to the standard HTML file <a href="https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa753582(v=vs.85)?redirectedfrom=MSDN">format</a> for exchanging browser bookmarks between browsers</li>
                <li>when imported into a browser (tested with Mozilla Firefox, Google Chrome and Apple Safari browsers) will create a folder containing the bookmarks - with "Tag A" and "Tag A & Tag B" relevant tag and tag combo</li>
                <ul>
                        <li>In Firefox (as at version 127): folder is named after the tag or tag combo and will be inside the &quot;Bookmarks Menu&quot; location in Bookmarks</li>
                        <li>In Google Chrome (as at version 125): folder is named after the tag/tag combo and will be inside in a folder named &quot;Imported&quot;(perhaps with a version number appeneded e.g. &quot;Imported (1)&quot; etc.) in the &quot;Bookmarks Bar&quot; folder in Bookmarks</li>
                        <li>In Safari (as at version 17.3.1): folder is named after the tag/tag combo and will be inside a folder named Imported with today&apos;s date in the name - and if you import more than one file on same date a version number so: &quot;Imported 30/05/2024 2&quot; for 2nd set of bookmarks imported on 30th May 2024 (first set would lack the 2 in name) etc.) in the &quot;Bookmarks Bar&quot; and </li>
                </ul>
                <li>the <a href="https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa753582(v=vs.85)?redirectedfrom=MSDN">format</a> is white space sensitive (if you alter the software and the import fails - it may be indentation related) and is not great for presentation compared to other HTML options (below).</li>
        </ol>
        <p>Other HTML options - anything in Fields dropdown except &quot;HTML links - as browser bookmarks file&quot; option</p>
        <ol>
                <li>includes useful summary info on number of links in the preview window</li>
                <li>appropriately spaces the links using paragraph elements</li>
                <li>would be a fairly clean and standard starting point for incorporating the HTML in another document - email, wordprocessing document, Markdown, a webpage etc. compared to the &quot;HTML links - as browser bookmarks file&quot; option</li>
        </ol>
        <h2>Necessary configuration for export to Google Sheets</h2>
        <p>Export to a Google Sheet is possible if you are willing to authorise this as a test app.</p>
        <p>I have decided to use a recommended non-sensitive scope <em>"https://www.googleapis.com/auth/drive.file"</em> as the scope for the app - restricting it to files in your Google Drive created with the app (see <a href="https://developers.google.com/drive/api/guides/api-specific-auth">https://developers.google.com/drive/api/guides/api-specific-auth</a>). However as this is open-source depending on where you got this from someone could modify it to use a more sensitive scope or to be malicious in
                some other way. So this is a suitable export mechanism if </p>
        <ul>
                <li>you understand Python enough to examine the program and be reasonably sure it is not malicious</li>
                <li>or you obtained this from <a href="https://github.com/byjosh/tagged_bookmarks_export_tool/">https://github.com/byjosh/tagged_bookmarks_export_tool/</a> directly AND trust me AND trust I have not been hacked</li>
                <li>or you obtained it from someone else you know and trust to both be competent in assessing Python programs and non-malicious</li>
                <li>you are running it in a situation where neither the computer you are running it on nor the account being accessed matters greatly if this was malicious/hacked - e.g. on a laptop with no personal files on it, inside a virtual machine and accessing throw-away account with no personal data in it</li>
        </ul>
        <p>Assuming it is sensible to trust this program with limited access to your Google account 4 things need to be done at <a href="https://console.cloud.google.com/apis/dashboard">https://console.cloud.google.com/apis/dashboard</a> in your account - mostly under the APIs and Services section:</p>
        <ol>
                <li>Firstly create a project and give it a name (e.g. <em>MyProject</em>) - after which the following steps are under the APIs and Services of your project e.g. <em>MyProject</em> </li>
                <li> Under "OAuth consent screen" and add yourself (and anyone you want to use the tool) as a test user</li>
                <li> Under "Enabled APIs &amp; services" search for Google Drive and enable that</li>
                <li> Under "Credentials": create and download OAuth 2.0 Client ID and save this in the same folder as main Python file as <code>credentials.json</code></li>
        </ol>
        <p>With that configuration done when you tick the checkbox for a tag with "Export to Google Sheets" as selected export mechanism for first time that should lead to web browser based authentication prompt. After successful configuration and authentication you should have two additional files present in the folder <code>credentials.json</code> and <code>token.json</code>(the former downloaded, second created by successful authentication process)</p>
        <p>As this app is not read only the scope of "https://www.googleapis.com/auth/drive.file" is needed and is non-sensitive
                see <a href="https://developers.google.com/drive/api/guides/api-specific-auth">https://developers.google.com/drive/api/guides/api-specific-auth</a>. Once configured and you have gone through browser based authentication you will need to create a spreadsheet using the app - as if "https://www.googleapis.com/auth/drive.file" is the only scope one cannot access spreadsheets created through web interface of Google Sheets. </p>
        <p>To enable its use without being added as a test user would need the app to be published and possibly to go through verification outlined here https://support.google.com/cloud/answer/13463073 . </p>
        <h2>Workflow once Export to Google Sheets is configured</h2>
        <h3>Initial window - allows creating or selecting spreadsheet and filtering data.</h3>
        <p>In this window, opening after selecting Export via Google Sheets in main window, one can create spreadsheet (if no existing spreadsheets created with app available to select), select a spreadsheet previously created with the app and filter the data - by ticking a box by any bookmarks one does not want exported.</p>
        <p>Note fields of the form <code>=HYPERLINK('https://example.com','Example.com Home Page')</code> is the necessary format to create a link in Google Sheets that will be visually say 'Example.com Home Page' while linking to the actual URL of 'https://example.com'. This format is important when the URL itself does not say much about the content of the page (a common situation with, for instance, links to articles in scholarly journals).</p>
        <h3>Final window - creating or selecting spreadsheet and filtering data</h3>
        <p>Once a spreadsheet has been created with the app (so it can be worked with) one can choose or create a sheet within a selected spreadsheet. The ability to create a sheet means that one could export a series of tagged bookmarks with each tag (or tag combo, links tagged with both tag A &amp; tag B) on its own sheet within the same spreadsheet.</p>
        <p>Having chosen an existing sheet or created one the data will be exported to that sheet - and the window and previous window both closed.</p>
        <h3>Spreadsheet IDs</h3>
        <p>The spreadsheet ID needed to identify a Google Sheets spreadsheet is shown to the user (to aid telling apart sheets with similar or identical names - to the same end you are shown the date &amp; time each sheet was created).</p>
        <h4>Spreadsheet ID is not editable in app - should it be?</h4>
        <p>If one added the scope <em>"https://www.googleapis.com/auth/spreadsheets"</em> to the app
                &amp; made spreadsheet ID box editable (via removing "style=wx.TE_READONLY," in line of code adding the spreadsheet ID box) one could get ID manually to copy &amp; paste in an ID
                by looking at Google Sheets spreadsheet URL (see below) and use this to edit an existing spreadsheet created outside this app. However using only the scope of <em>"https://www.googleapis.com/auth/drive.file"</em>
                makes app more secure by conforming to principle of least privilege
                (here: only allowing it access to spreadsheets created by app - not all one's spreadsheets).</p>
        <h4>How do I see the spreadsheet ID from a URL</h4>
        <p>For example: if Google Sheets spreadsheet URL was https://docs.google.com/spreadsheets/d/1-ABC123def/edit#gid=0
                then <em>1-ABC123def</em> would be ID (in reality ID would be longer & more random but ID is between the /d/ and the /edit# in URL). The ID can allow you to tell the difference between two spreadsheets that might otherwise have the same names</p>
        <h2>Rationale for this app</h2>
        <p>Firefox browser exports bookmarks as a single HTML file with folders as the organising principle. In Firefox browser you can tag bookmarks in addition to choosing a folder location - and exporting by tag offers more flexibility to export just some of your bookmarks - including those with the same tag but in different folders.</p>
        <h2>Example</h2>
        <p>As an example of utility of using tags and this tool: suppose you bookmark pages about books for 3 reasons: 1) you want to read them yourself, 2) you are research the book as present for another person 3) you used or researched the book as a source for something you wrote such as a thesis. In all cases you could put them in an appropriate folder - but without tags you could not export all three combined. With tags: a common tag of e.g. "book" would allow export of a single list with all bookmarks
                tagged "book" regardless of folder, using two tags e.g. "book" as the common tag and a specific tag e.g. "to_buy", "for_mom", "thesis" (related to oneself, or books for one's mom, or one's thesis as appropriate) would - using the two tag combo option of this tool - allow you export a list of just the bookmarks labelled, in this example, "book" and "thesis" - showing only those bookmarks you marked as books related to your thesis.</p>
        <h2>Why is this not relevant to other browsers?</h2>
        <p>Besides the issue of Firefox browser specific bookmarks database structure: others (such as Chrome browser or Safari browser) do not seem to use tags (as at spring 2024) and they export as 1 HTML file organised by folder - the same as current default for bookmarks HTML export from Firefox browser. If one only organises one's bookmarks by folder then editing the HTML file exported by your browser is enough to produce a file only of the desired bookmarks. Hence this tool only serves a purpose for
                tagged bookmarks from Firefox browser.</p>
        <h2>Trademark acknowledgements</h2>
        <p>Firefox is a trademark of the Mozilla Foundation in the U.S. and other countries. Safari is a trademark of Apple Inc. Chrome, Google Drive, and Google Sheets are trademarks of Google LLC.</p>