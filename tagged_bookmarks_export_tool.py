# Copyright: josh - web@byjosh.co.uk github.com/byjosh
# Licensed under GPLv2 - see LICENSE.txt in repository 
# or https://www.gnu.org/licenses/old-licenses/gpl-2.0.html

import webbrowser
import wx
from wx.html import HtmlWindow
import wx.lib.inspection
from database_utils import *
from html_utils import *

html_page_source = ""
file_path()


class TabCheckbox(wx.CheckBox):
    """Subclass the checkbox - re: keyboard input - TODO: Look into MacOS specific default behaviour re: keyboard navigation"""

    def __init__(self, *args, **kw):
        super(TabCheckbox, self).__init__(*args, **kw)
        # self.EnableVisibleFocus(True) # causes error on Fedora Linux with python3-wxpython4 package

    def AcceptsFocusFromKeyboard(self):
        return True

    def AcceptsFocus(self):
        return True


class MainFrame(wx.Frame):
    """
    Frame that shows the tags list
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(MainFrame, self).__init__(*args, **kw)

        # create set of of tags - used to determine if more than one box ticked
        self.tags = set()
        self.margin = 20
        self.multitag_added = False  # to check that multitags have not already been added.

        # create a panel in the frame
        # show scroll bars
        self.pnl = wx.ScrolledWindow(self, wx.ID_ANY, name="Main pnl Panel as labelled", size=wx.Size(600, 600))
        self.pnl.SetScrollbars(1, 1, 1, 1)

        # list for convenience
        self.panels_sizers = []

        self.pnlA = wx.Panel(self.pnl, name="Panel_A_top")
        self.pnlB = wx.Panel(self.pnl, name="Panel_B_bottom")

        # This text is instructional
        header_text = "Get started:- \n"
        header_text += "open a places.sqlite file\n"
        header_text += "from your Firefox browser profile\n"
        header_text += "(see Help menu or web search for how\n"
        header_text += "to find profile folder && places.sqlite),\n"
        header_text += "using File menu > Open or use Ctrl+O\n"
        header_text += " or Cmd+O depending on your computer operating system."
        header_area_message = wx.StaticText(self.pnlA, label=header_text)
        font = header_area_message.GetFont()
        font.PointSize += 2
        font = font.Bold()
        header_area_message.SetFont(font)

        # This text will be replaced when tags load
        tags_area_message = wx.StaticText(self.pnlB,
                                          label="Your tags will load here when you open a file \n - File > Open or use Ctrl+O or CMD+O depending on your OS")
        font = tags_area_message.GetFont()
        tags_area_message.SetFont(font)

        # sizers to manage the layout of child widgets
        self.sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.pnlA.sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.pnlB.sizer = wx.FlexGridSizer(cols=1)
        # self.pnlB.SetBackgroundColour(wx.GREEN) # to see how layout options affect panel

        # add panels to sizers
        self.sizer.Add(self.pnlA, wx.SizerFlags().Top())
        self.sizer.Add(self.pnlB, wx.SizerFlags().Top())

        multi_tag_checkbox = TabCheckbox(self.pnlA,
                                         label="Append categories for items tagged with 2 tags e.g. both tag A && tag B\n (tick this before or after opening your sqlite file then look below list of single tag entries\n for entries of form 'tag A && tag B')",
                                         name="multitag_categories")
        self.multitag_check = multi_tag_checkbox

        # add the messages and checkbox to sizers
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        self.pnlA.sizer.Add(header_area_message, wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        self.pnlA.sizer.Add(self.multitag_check, wx.SizerFlags().Border(wx.LEFT, self.margin))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        self.pnlA.sizer.Add(wx.StaticText(self.pnlA,
                                          label="Export format - choose how bookmarks will appear: \npage of HTML links with/without plaintext URLs or save direct to CSV"),
                            wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        export_format_box = wx.Choice(self.pnlA, id=101, choices=[k for k in export_format_choices],
                                      name="Export Format")
        self.pnlA.sizer.Add(export_format_box, wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        self.pnlB.sizer.Add(tags_area_message,
                            wx.SizerFlags().Border( wx.LEFT, self.margin * 2))
        self.pnlA.SetFocus()

        # record initial format choice and resent as needed via EVT_CHOICE
        format_window = wx.FindWindowById(101, self.pnlA)
        format_choice_index = format_window.GetSelection()
        self.format_choice = format_window.GetString(format_choice_index)

        # try only showing after open file
        self.panels_sizers.extend([(self.pnl, self.sizer), (self.pnlA, self.pnlA.sizer), (self.pnlB, self.pnlB.sizer)])
        self.set_sizers()
        self.SetSize(wx.Size(600, 600))
        # create a menu bar
        self.make_menu()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Load a places.sqlite bookmarks file to get started")
        self.Bind(wx.EVT_CHECKBOX, self.OnEVTCheckBox)
        self.Bind(wx.EVT_CHOICE, self.OnEVTChoice)
        self.SetFocus()

    def set_sizers(self):
        """Create a panel and add to panels property - helps with repetitive layout task"""
        for item in self.panels_sizers:
            pnl, sizer = item
            pnl.SetSizer(sizer)

    def panel_sizer_with_this_panel_removed(self, panel):
        return [x for x in self.panels_sizers if x[0] != panel]

    def add_multitag_checkboxes(self, sizer, panel):
        """Adds the multitag checkboxes to chosen size & panel"""
        width, height = self.GetSize()
        if self.multitag_added is True:
            return
        tags = tag_dict(get_results(db_cursor(db_connect()), qs["tags"]))
        self.multitag_links_dict = dual_tag_non_zero_dict(dual_tag_dict=dual_tag_dict(tags))
        if self.multitag_added is False and len(self.multitag_links_dict) > 0:
            multi_tag_list_header = wx.StaticText(self.pnlB,
                                                  label="Entries for items tagged with both tag A && tag B\ncheck box to show bookmarked links")
            sizer.Add(multi_tag_list_header, wx.SizerFlags().Align(wx.TOP).Border(wx.LEFT, self.margin * 2))
            for textlabel in self.multitag_links_dict:
                sizer.Add(wx.CheckBox(panel, label=textlabel), wx.SizerFlags().Border(wx.LEFT, int(self.margin * 2)))
            self.multitag_added = True
            # Just laying out the changed panel after SetSizer and SetSize calls works
            # self.pnlA.Layout() # this with pnl.Layout after setsize leaves Panel B as main thing - with Panel A layout alone items are added to panel B but misplaced but Panel A present
            self.SetStatusText("Entries added for bookmarks tagged with at least two tags - scroll down to see")
        else:
            no_dual_tags_message = "Current sqlite file (this set of bookmarks)\ndoesn't have any bookmarks tagged with\nmore than 1 tag. Try another file?"
            sizer.Add(wx.StaticText(self.pnlB, label=no_dual_tags_message),
                      wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
            self.SetStatusText("In this file no bookmarks tagged with more than 1 tag. Try another file?")

        sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, 50))
        self.set_sizers()
        # print("name ",self.Name)
        self.SetSize(wx.Size(width, height+1))
        panel.Layout()


    def open_or_export(self, format_choice):
        """Export file or opening window in response to event"""

        global html_page_source
        global pathname
        x_pos, y_pos = self.GetPosition()
        width, height = self.GetSize()
        # pure CSV for export is final format
        csv_choice = [k for k in export_format_choices][-1]

        def csv_file_dialog(urls_titles):
            # CSV save file dialog - uses csv_only function from html_utils.
            with wx.FileDialog(self, "Save CSV file", wildcard="CSV files (*.csv)|*.csv",
                               defaultFile=title.replace("&", "_and_"),
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return  # decided not to save file

                # save the csv
                csvfile = fileDialog.GetPath()
                try:
                    csv_only(urls_titles, csvfile)
                except IOError:
                    wx.LogError("Cannot save current data in file '%s'." % csvfile)

        urls_titles = None
        for set_tuple in self.tags:
            tagID = set_tuple[0]
            title = set_tuple[1]
        # searching for && is checking for single tags
        is_dual_tag = [x for x in self.tags][0][1].find("&&") != -1
        if is_dual_tag is False:
            urls_titles = urls_from_tagID(tagID)
        if is_dual_tag is True:
            urls_titles = urls_from_combinedtagname(title, self.multitag_links_dict)
            title = title.replace("&&", "&")
            # have HTML source in appropriate format - open in new window unless choice is to save to CSV directly
        if format_choice != csv_choice:
            html_page_source = full_html(urls_titles, title, export_format_choices[format_choice])
            myHtmlFrame(self, size=wx.Size(800, 600), pos=wx.Point(x_pos + width, y_pos), title=title).SetPage(
                html_page_source,urls_titles,export_format_choices[format_choice]).Show()
        else:
            csv_file_dialog(urls_titles)

    def OnEVTChoice(self, event):
        format_window = wx.FindWindowById(101, self.pnlA)
        format_choice_index = format_window.GetSelection()
        self.format_choice = format_window.GetString(format_choice_index)
        if len(self.tags) == 1:
            # only one checkbox checked so changing format likely to indicate a different format wanted
            # so open or export
            self.open_or_export(self.format_choice)

    def OnEVTCheckBox(self, event):

        if event.GetEventObject().Name != "multitag_categories":
            id_tagname_tuple = (event.GetEventObject().Id, event.GetEventObject().Label)
            if event.GetEventObject().Value is True:
                self.tags.add(id_tagname_tuple)
                if len(self.tags) > 1:
                    checked_box_labels = ", ".join([x[1].replace("&&", "&") for x in self.tags])
                    wx.MessageBox(f'Uncheck whichever is unnecessary of\n {checked_box_labels} ',
                                  "More than 1 checkbox selected!")
            elif event.GetEventObject().Value is False:
                self.tags.remove(id_tagname_tuple)

            if len(self.tags) == 1:
                self.open_or_export(self.format_choice)


        elif event.GetEventObject().Name == "multitag_categories" and (
                file_path() is not None) and event.GetEventObject().GetValue():
            if is_bookmarks_file():
                self.add_multitag_checkboxes(self.pnlB.sizer, self.pnlB)
            else:
                self.SetStatusText("Need a bookmarks file to append categories for items with 2 tags! ")

    def make_menu(self):
        """
        Make a menu bar with File > Open, Help and About items.
        """

        # Make a file menu with Open and Exit items
        fileMenu = wx.Menu()
        openItem = fileMenu.Append(-1, "&Open sqlite file...\tCtrl-O",
                                   "Open a places.sqlite file from the browser for fine-grained export")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)
        helpItem = helpMenu.Append(-1, "&Show help ...\tF1", "Show single page help window")
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnOpen, openItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
        self.Bind(wx.EVT_MENU, self.OnHelp, helpItem)

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnOpen(self, event):
        """File Open dialogue"""
        width, height = self.GetSize()
        # pick file
        with wx.FileDialog(self, "Open sqlite file", wildcard="sqlite files (*.sqlite)|*.sqlite",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # user changed their mind but no change to interface in that case
            pathname = fileDialog.GetPath()
            if len(pathname) == 0:
                return
            self.multitag_added = False
            # use the pathname just retrieve to set filepath in function from database_utils
            file_path(filepath=pathname)

        # remove and add back the lower Panel B
        self.tags = set()
        self.panels_sizers = self.panel_sizer_with_this_panel_removed(self.pnlB)
        self.pnlB.Destroy()
        self.pnlB = wx.Panel(self.pnl)
        self.pnlB.sizer = wx.FlexGridSizer(cols=1)
        self.panels_sizers.append((self.pnlB, self.pnlB.sizer))
        self.sizer.Add(self.pnlB, wx.SizerFlags().Top().Expand())
        if is_bookmarks_file():
            # append tags to lower Panel B
            self.pnlB.sizer.Add(wx.StaticText(self.pnlB,
                                              label="Entries with items tagged with tag below\ncheck box to show bookmarked links"),
                                wx.SizerFlags().Align(wx.TOP).Border(wx.LEFT, self.margin * 2))

            tags = tag_dict(get_results(db_cursor(db_connect()), qs["tags"]))
            for tag in tags:
                self.pnlB.sizer.Add(TabCheckbox(self.pnlB, id=tags[tag], label=tag),
                                    wx.SizerFlags().Align(wx.TOP).Border(wx.LEFT, int(self.margin * 2)))

            self.pnlB.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, 20))
            if self.multitag_check.GetValue():
                self.add_multitag_checkboxes(self.pnlB.sizer, self.pnlB)
            self.SetStatusText("File loaded")
            self.set_sizers()

            self.pnl.Layout()
            # TODO: the following is terrible hack - changing by 1 pixel to get auto-layout working
            self.SetSize(wx.Size(width, height-1))
        else:
            self.SetStatusText("Not an appropriate bookmarks file - try another file?")
            self.pnlB.sizer.Add(wx.StaticText(self.pnlB,
                                              label="Last opened file lacks necessary database tables (moz_places and moz_bookmarks)\nIs it a places.sqlite bookmarks file from Firefox browser?\nTry another sqlite file?"),
                                wx.SizerFlags().Border( wx.LEFT , self.margin * 2))

        self.set_sizers()

        self.pnl.Layout()
        # TODO: the following is terrible hack - changing by 1 pixel to get auto-layout working
        self.SetSize(wx.Size(width, height+1))



    def OnAbout(self, event):
        """Display an About Dialog"""
        about_text = "By github.com/byjosh. \n\n"
        about_text += "Given the places.sqlite from your Firefox browser profile \n"
        about_text += "(or derivatives like Iceweasel) if you use tags to \n"
        about_text += "label your bookmarks then this can export an HTML \n"
        about_text += "file of just those bookmarks the tag selected (or \n"
        about_text += "two tag combination if one checks the box to see \n"
        about_text += "those combinations as options)."

        box = wx.RichMessageDialog(self, about_text,
                                   "About Bookmarks export tool",
                                   style=wx.OK | wx.CENTRE)

        box.ShowModal()

    def OnHelp(self, event):
        """Show Help file (single page HTML)"""
        x_pos, y_pos = self.GetPosition()
        width,height = self.GetSize()
        title = "Tagged bookmarks export tool - Help"
        html_text = f'<html><head><title>{title}</title><style></style></head><body>\
        <h1>Help</h1>\
        <h2>Workflow</h2>\
        <ol>\
        <li><p>Find places.sqlite from your Firefox browser profile (see <a href="https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data">https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data</a>)</p></li>\
        <li><p>Open it with this tool via File &gt; Open in menu</p></li>\
        <li><p>Check checkbox by tag name to show bookmarks with that tag.</p></li>\
        <li><p>In window that appears: click on the links to visit link in default browser or click "Save as HTML file" link to export window contents as HTML</p></li>\
        <li><p>Use "Append categories for items tagged with 2 tags" checkbox before or after file opening to have shown after single tag checkboxes the checkboxes for those tagged with at least two (e.g. tag A & tag B). Use of window that appears is same as for single tag bookmarks.</p></li>\
        </ol>\
        <h2>Rationale</h2>\
        <p>Firefox browser exports bookmarks as a single HTML file with folders as the organising principle. In Firefox browser you can tag bookmarks in addition to choosing a folder location - and exporting by tag offers more flexibility to export just some of your bookmarks - including those with the same tag but in different folders.</p>\
        <h2>Example</h2>\
        <p>As an example of utility of using tags and this tool: suppose you bookmark pages about books for 3 reasons: 1) you want to read them yourself, 2) you are research the book as present for another person 3) you used or researched the book as a source for something you wrote such as a thesis. In all cases you could put them in an appropriate folder - but without tags you could not export all three combined. With tags: a common tag of e.g. "book" would allow export of a single list with all bookmarks tagged "book" regardless of folder, using two tags e.g. "book" as the common tag and a specific tag e.g. "to_buy", "for_mom", "thesis" (related to oneself, or books for one\'s mom, or one\'s thesis as appropriate) would - using the two tag combo option of this tool - allow you export a list of just the bookmarks labelled, in this example, "book" and "thesis" - showing only those bookmarks you marked as books related to your thesis.</p>\
        <h2>Why is this not relevant to other browsers?</h2>\
        <p>Besides the issue of Firefox browser specific bookmarks database structure: others (such as Chrome browser or Safari browser) do not seem to use tags (as at spring 2024) and they export as 1 HTML file organised by folder - the same as current default for bookmarks HTML export from Firefox browser. If one only organises one\'s bookmarks by folder then editing the HTML file exported by your browser is enough to produce a file only of the desired bookmarks. Hence this tool only serves a purpose for tagged bookmarks from Firefox browser.</p>\
        <h2>Trademark acknowledgements</h2>\
        <p>Firefox is a trademark of the Mozilla Foundation\n in the U.S. and other countries. Safari is a trademark of Apple Inc. Chrome is a trademark of Google LLC.</p>\
        </body></html>'

        helpframe = wx.Frame(self, size=wx.Size(600, 600), )
        myHtmlFrame(helpframe, size=wx.Size(800, 600), pos=wx.Point(x_pos + width, y_pos), title=title).SetPage(
            html_text).Show()


class myHtmlFrame(wx.Frame):
    """
    A Frame of HTML that opens from Main Frame and contains a single HtmlWindow whose source is set with SetPage method
    """

    def __init__(self, *args, **kw):
        super(myHtmlFrame, self).__init__(*args, **kw)
        self.html_win = HtmlWindow(self, size=wx.Size(800, 600))
        self.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.OnClick)
        self.html_win.Bind(wx.EVT_TEXT_COPY, self.OnTextCopy)

    def SetPage(self, source,urls_titles,processing_function):
        self.links = make_list_source_from_urls_titles(urls_titles,processing_function)
        self.source = source
        self.html_win.SetPage(source)
        return self

    def OnTextCopy(self, event):
        text = self.html_win.SelectionToText()
        # from random import randint # random int to log event fired
        # print("Text copied ",randint(1,100))
        if wx.TheClipboard.Open():
            wx.TheClipboard.Clear()
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()

    def OnClick(self, event):
        """Handles when HTML link is clicked - opens in browser or saves HTML file for href == # """
        special_hrefs = ["#","##"]
        if event.GetLinkInfo().GetHref() not in special_hrefs:
            webbrowser.open(event.GetLinkInfo().GetHref())
        if event.GetLinkInfo().GetHref() == "##":
            # just links as HTML
            if wx.TheClipboard.Open():
                wx.TheClipboard.Clear()
                wx.TheClipboard.SetData(wx.HTMLDataObject(self.links))
                wx.TheClipboard.Close()
        if event.GetLinkInfo().GetHref() == "#":
            # This is save file dialog
            with wx.FileDialog(self, "Save as HTML file", wildcard="HTML files (*.html)|*.html",
                               defaultFile=self.Label.replace("&", "_and_"),
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return  # decided not to save file

                # save the HTML
                pathname = fileDialog.GetPath()
                try:
                    with open(pathname, 'w') as file:
                        file.write(self.source.replace(instructional_text,""))
                except IOError:
                    wx.LogError("Cannot save current data in file '%s'." % pathname)


if __name__ == '__main__':
    # create app, create main frame and show it and start event loop
    app = wx.App()
    frm = MainFrame(None, size=wx.Size(600, 600), title='Tagged bookmarks export tool')
    frm.Show()
    # wx.lib.inspection.InspectionTool().Show()  # uncomment for debugging via inspection tool
    app.MainLoop()
