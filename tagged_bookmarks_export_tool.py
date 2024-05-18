# Copyright: josh - web@byjosh.co.uk github.com/byjosh
# Licensed under GPLv2 - see LICENSE.txt in repository 
# or https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
import os.path
import webbrowser
import wx
from wx.html import HtmlWindow
import wx.lib.inspection
from database_utils import db_util
from html_utils import *
import changespreadsheets
import findfiles

"""import logging
logging.basicConfig(level=logging.DEBUG)
log_main = logging.getLogger(name="TBET MAIN")
log_main.setLevel(logging.DEBUG)

Use find and replace in IDE to uncomment # from log_main calls - see comment in database_utils about speed
"""

html_page_source = ""


def html_link(data):
    """
    :param data: tuple with link as 2nd field and title as last
    :type data: tuple
    :return:  html link with descriptive title
    :rtype: str
    """
    return f'<a href="{html.escape(data[1])}" > {html.escape(data[-1])}</a>'


def sheets_link(data):
    """
    :param data: tuple with link as 2nd field and title as last
    :type data: tuple
    :return:  link with descriptive title formatted for Google Sheets USER_ENTERED input
    :rtype: str
    """
    return f'=HYPERLINK("{html.escape(data[1])}","{html.escape(data[-1])}")'


field_orders = {"HTML links": {"output_order": (html_link,)},
                "HTML link, plaintext url": {"output_order": (html_link, 1)},
                "HTML link, url, timestamp": {"output_order": (html_link, 1,-3)},
                "HTML link, description,url, timestamp": {"output_order": (html_link, -2, 1, -3)},
                "plain url, title,timestamp, description": {"output_order": (1, -1, -3, -2)}, }


def csv_only(urls_titles, filepath):
    import csv
    with open(filepath, mode="w") as file:
        csv.writer(file, dialect='excel', quoting=csv.QUOTE_ALL).writerows(urls_titles)


export_mechanisms = {"HTML/text - window where one can preview, save, copy": None,
                     "CSV - save to CSV file (no preview)": csv_only,
                     "Export to Google Sheets - read help re: configuration": None}


class TabCheckbox(wx.CheckBox):
    """Subclass the checkbox - re: keyboard input - TODO: Look into MacOS specific default behaviour re: keyboard navigation"""

    def __init__(self, *args, **kw):
        super(TabCheckbox, self).__init__(*args, **kw)
        # self.EnableVisibleFocus(True) # causes error on Fedora Linux with python3-wxpython4 package

    def AcceptsFocusFromKeyboard(self):
        return True

    def AcceptsFocus(self):
        return True


class CommonSheet(wx.Frame):

    def __init__(self, *args, **kw):
        # COMMON
        # ensure the parent's __init__ is called
        super(CommonSheet, self).__init__(*args, **kw)

        self.pnl = wx.ScrolledWindow(self, wx.ID_ANY, name="Main pnl Panel as labelled", size=wx.Size(600, 600))
        self.pnl.SetScrollbars(1, 1, 1, 1)
        self.margin = 20
        # list for convenience
        self.panels_sizers = []
        self.pnlA = wx.Panel(self.pnl, name="Panel_A_top")
        self.sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.pnlA.sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.sizer.Add(self.pnlA, wx.SizerFlags().Top())
        # END COMMON

    def set_sizers(self):
        """Create a panel and add to panels property - helps with repetitive layout task"""
        for item in self.panels_sizers:
            pnl, sizer = item
            pnl.SetSizer(sizer)

    def get_sheet_range(self, data):
        """

        >>> self.get_sheet_range([('https://leanpub.com/b/python-craftsman', 'The Python Craftsman', '2024-04-25 21:08:11.336000', "The Python Craftsman series comprises The Python Apprentice, The Python Journeyman, and The Python Master. The first book is primarily suitable for programmers with some experience of programming in another language. If you don't have any experience with p"), ('https://libro.fm/audiobooks/9781508279532-good-and-mad', 'Libro.fm | Good and Mad Audiobook', '2024-04-25 21:05:46.194000', '*Updated with a new introduction* Journalist Rebecca Traister’s New York Times bestselling exploration of the transformative power of female anger and its ability to transcend into a political movement is “a hopeful, maddening compendium of righteous femin'), ('https://uk.bookshop.org/p/books/verified-how-to-think-straight-get-duped-less-and-make-better-decisions-about-what-to-believe-online-mike-caulfield/7439531?ean=9780226822068', 'Verified: How to Think Straight, Get Duped Less, and Make Better Decisions about What to Believe Online a book by Mike Caulfield and Sam Wineburg.', '2024-04-25 21:06:23.047000', 'An indispensable guide for telling fact from fiction on the internet—often in less than 30 seconds. The internet brings information to our fingertips almost instantly. The result is that we often jump to thinking too fast, without taking a few moments to v')])
        'A1:D3'

        :param data:
        :type data:
        :return sheet_range : string detailing in A1 notation a range large enough for data
        :rtype: str
        """

        rows = len(data)
        cols = 0
        for iterabl in data:
            if (len(iterabl) - 1) > cols:
                cols = len(iterabl) - 1

        sheet_range = "A1:"
        sheet_range += [x for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"][cols]  # TODO: generator for this?
        sheet_range += str(rows)

        return sheet_range


class ChooseSheet(CommonSheet):
    """Second dialogue - choose or create a sheet in spreadsheet and save data to it - closing this and previous dialogue"""

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(ChooseSheet, self).__init__(*args, **kw)

        self.id = wx.FindWindowById(self.GetParent().frame_ids["txtbox current ID"], self.GetParent().pnlA).GetLineText(0).strip()

        if self.GetParent().selected_sheet_id == "" or self.GetParent().selected_sheet_id == "Select/create spreadsheet above to replace this text with an ID":
            wx.MessageBox(
                "A spreadsheet has not been specified by ID - create a spreadsheet or selected an existing spreadsheet (if shown) first - an ID will appear in box (not user editable) when selected/created",caption="Spreadsheet not selected/created")
            self.Close()
        elif self.GetParent().selected_sheet_id != "" and self.GetParent().selected_sheet_id != "Select/create spreadsheet above to replace this text with an ID":
            # above shows a spreadsheet has been selected - now to get sheet names
            current_spreadsheet_name = self.GetParent().existing_spreadsheets[self.GetParent().selected_sheet_id][0]
            self.sheet_names = changespreadsheets.get_sheet_names(self.GetParent().selected_sheet_id)
            self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
            main_text = f'\nButtons before the textbox below are existing sheet names\nclicking a button exports to that sheet \nin spreadsheet "{current_spreadsheet_name}"'
            self.pnlA.sizer.Add(wx.StaticText(self.pnlA,
                                              label=main_text),
                                wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
            self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))

            # add existing sheet names
            for sheet in self.sheet_names:
                self.pnlA.sizer.Add(wx.Button(self.pnlA, label=sheet.replace("&", "&&")),
                                    wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
                self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))

            # Create new sheet
            self.pnlA.sizer.Add(wx.StaticText(self.pnlA,
                                              label="Enter new sheet name in textbox below\n(tag(s) prefilled as a suggested sheet name)"),
                                wx.SizerFlags().Border(wx.LEFT, int(self.margin * 2)))
            for tg in self.GetParent().GetParent().tags:
                self.current_tag = tg[1].replace("&&", "&")
            self.pnlA.sizer.Add(wx.TextCtrl(self.pnlA, id=301, name="New sheet name", value=self.current_tag),
                                wx.SizerFlags().Expand().Border(wx.LEFT, int(self.margin * 2)))
            self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
            self.pnlA.sizer.Add(
                wx.Button(self.pnlA, id=300, label="Create sheet using name in textbox above && export to it"),
                wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
            self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
            self.pnlA.sizer.Add(wx.StaticText(self.pnlA,label=f'N.B. Default in this window is clicking a button exports\nto spreadsheet "{current_spreadsheet_name}" \nwith ID of {self.id}\n\nData will be entered in range {self.GetParent().get_sheet_range(self.GetParent().get_non_excluded_data())} of chosen sheet \nwith {len(self.GetParent().data) - len(self.GetParent().get_non_excluded_data())} items excluded from export on previous screen\n\nTo exit WITHOUT exporting: close window without clicking a button.\n'),wx.SizerFlags().Border(wx.LEFT, self.margin * 2))

        self.panels_sizers.extend([(self.pnl, self.sizer), (self.pnlA, self.pnlA.sizer)])
        self.set_sizers()
        self.SetSize(wx.Size(600, 600))
        self.Bind(wx.EVT_BUTTON, self.OnEVTButton)

    def OnEVTButton(self, event):
        def create_status_text(sheetname, spreadsheetname):
            if self.current_tag.find("&") != -1:
                tags = "tag combo"
            else:
                tags = "tag"
            return f'Exported links from {tags} "{self.current_tag}" to sheet "{sheetname}" in "{spreadsheetname}" Google Sheets™ spreadsheet'

        if event.GetEventObject().Id != 300:
            # This Id of NOT 300 means any button NOT creating a new sheet
            self.GetParent().sheet_name = event.GetEventObject().Label
            sheet_name_button_text = f"Choose sheet name/create sheet (current sheet = {event.GetEventObject().Label} )"
            wx.FindWindowById(200, self.GetParent().pnlA).SetLabel(sheet_name_button_text)

            self.GetParent().sheet_range = "'" + event.GetEventObject().Label + "'" + "!" + self.GetParent().sheet_range
            changespreadsheets.main(self.GetParent().get_non_excluded_data(), sheet_id=self.id,
                        sheet_range=self.GetParent().sheet_range)
            self.GetParent().set_sizers()
            self.GetParent().SetSize(wx.Size(600, 601))
            status_text = create_status_text(event.GetEventObject().Label, self.GetParent().title)
            self.GetParent().GetParent().SetStatusText(status_text)
            self.GetParent().Close()

        elif event.GetEventObject().Id == 300:
            name = wx.FindWindowById(301, self.pnlA).GetLineText(0).strip().replace("''", "'")
            sheet_name_button_text = f"Choose sheet name/create sheet (current sheet = {name} )"
            if name in self.sheet_names:
                message = f"The new sheet name you entered already exists in the spreadsheet with id {self.GetParent().selected_sheet_id} - your options:\npick existing sheet\ntry different name\nor different spreadsheet?\n\nN.B. no data export as new sheet name already exists \n& thus conflicts with existing sheet"
                wx.MessageBox(message, parent=self)
            if name not in self.sheet_names:
                self.GetParent().sheet_name = changespreadsheets.set_sheet_name(self.GetParent().selected_sheet_id, name)

                self.GetParent().sheet_range = "'" + name + "'" + "!" + self.GetParent().sheet_range
                changespreadsheets.main(self.GetParent().get_non_excluded_data(), sheet_id=self.id,
                            sheet_range=self.GetParent().sheet_range)
                # not currently used as parent window closed
                wx.FindWindowById(200, self.GetParent().pnlA).SetLabel(sheet_name_button_text)

                self.GetParent().set_sizers()
                self.GetParent().SetSize(wx.Size(600, 601))
                spreadsheet_dict = {k: self.GetParent().existing_spreadsheets[k] for k in
                                    self.GetParent().existing_spreadsheets}
                if self.id in spreadsheet_dict:
                    status_text = create_status_text(name, spreadsheet_dict[self.id])
                self.GetParent().GetParent().SetStatusText(status_text)
                self.GetParent().Close()


class ChooseSpreadsheet(CommonSheet):
    """Initial dialogue - choose or create a spreadsheet to save to - and select data"""

    def __init__(self, *args, **kw):


        # ensure the parent's __init__ is called
        super(ChooseSpreadsheet, self).__init__(*args, **kw)

        self.data = self.GetParent().urls_titles_data
        self.sheet_range = self.get_sheet_range(self.data)

        header_text = "Get started:\n"
        header_text += "create a new sheet or select an existing one\n"
        header_text += "(if there are existing sheets created with this tool)"
        header_area_message = wx.StaticText(self.pnlA, label=header_text)

        file_name = wx.TextCtrl(self.pnlA, id=130, name="New filename", value="New spreadsheet name")
        file_name.SetMinSize(wx.Size(400, 25))

        placeholder_id = "Select/create spreadsheet above to replace this text with an ID"
        self.frame_ids = {"txtbox new spreadsheet": 130, "txtbox current ID": 131 ,"btn create spreadsheet":110, "btn choose/create sheet": 200 }


        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        self.pnlA.sizer.Add(header_area_message, wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        self.pnlA.sizer.Add(wx.StaticText(self.pnlA,
                                          label="Enter new spreadsheet name:"),
                            wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        self.pnlA.sizer.Add(file_name, wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))

        self.pnlA.sizer.Add(
            wx.Button(self.pnlA, id=110, label="Create new spreadsheet (&& automatically get the ID put in box below)"),
            wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        self.existing_spreadsheets = findfiles.search_file()
        if len(self.existing_spreadsheets) > 0:
            self.pnlA.sizer.Add(wx.StaticText(self.pnlA,
                                              label="Existing spreadsheets tick to set as export destination && put ID in box below:"),
                                wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
            for k in self.existing_spreadsheets:
                self.pnlA.sizer.Add(wx.CheckBox(self.pnlA, label=self.existing_spreadsheets[k][0], name=k),
                                    wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
                self.pnlA.sizer.Add(wx.StaticText(self.pnlA,
                                                  label=f'Created on {self.existing_spreadsheets[k][1].replace("T"," at ").split(".")[0]}'),
                                    wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
                self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        elif len(self.existing_spreadsheets) == 0:
            self.pnlA.sizer.Add(wx.StaticText(self.pnlA,
                                              label="This tool can only export to spreadsheets created with it.\nNo spreadsheets created with this tool found - create one above\n"),

                                wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
            self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))


        valid_id_text = wx.StaticText(self.pnlA,
                                      label="When you create or choose spreadsheet above\nspreadsheet ID (not user editable) appears below")
        font = valid_id_text.GetFont()
        font = font.Bold()
        font.PointSize += 1
        valid_id_text.SetFont(font)
        self.pnlA.sizer.Add(valid_id_text,
                            wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        # is there a checbox related to spreadsheets checked
        self.spreadsheet_box_checked = []
        if self.GetParent().selected_sheet_id is not None:
            placeholder_id = self.GetParent().selected_sheet_id

            window_found = wx.FindWindowByName(placeholder_id, self.pnlA)
            # need to check window is not None as sheets deleted between opening can mean a valid ID is not longer valid
            if window_found is not None and len(self.existing_spreadsheets) > 0:
                window_found.SetValue(True)
                # monitor if a box is ticked
                self.spreadsheet_box_checked.append(placeholder_id)
        if placeholder_id not in self.existing_spreadsheets:
            placeholder_id = "Select/create spreadsheet above to replace this text with an ID"
        sheet_ID = wx.TextCtrl(self.pnlA, id=self.frame_ids["txtbox current ID"],style=wx.TE_READONLY, name="Spreadsheet ID", value=placeholder_id)
        sheet_ID.SetMinSize(wx.Size(400, 25))

        self.pnlA.sizer.Add(sheet_ID, wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        """self.pnlA.sizer.Add(wx.Button(self.pnlA,id=111, label="Export to existing sheet using spreadsheet ID"),
                            wx.SizerFlags().Border(wx.LEFT, self.margin * 2))"""
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        self.sheet_name = None
        sheet_name_button_text = f"Choose/create sheet in spreadsheet with above ID && export data to it"
        self.pnlA.sizer.Add(wx.Button(self.pnlA, id=200, label=sheet_name_button_text),
                            wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))

        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 1)))
        exclusion_text = wx.StaticText(self.pnlA,
                                       label="PREVIEW OF DATA TO BE EXPORTED BELOW:\nOptional: keep some bookmarks private\ncheck the boxes of any items below you do NOT want to export\nfor whatever reason (relevancy, accuracy,privacy etc),\nDEFAULT IS TO EXPORT ALL UNCHECKED ITEMS.")
        font = exclusion_text.GetFont()
        font = font.Bold()
        font.PointSize += 1
        exclusion_text.SetFont(font)
        self.pnlA.sizer.Add(exclusion_text,
                            wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        additional_exclusion_text = wx.StaticText(self.pnlA,label="This is 'edit before sending (to Google servers)'\noption. If you should've used this option but didn't:\ndelete in Google Drive/Sheets and try again\nor make the edits there, on Google servers,\nthat you should have made here.")
        self.pnlA.sizer.Add(additional_exclusion_text,
                            wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        for i in range(0, len(self.data)):
            labeltext = ''
            for f in self.data[i]:
                if f is not None:
                    labeltext += f'{f},\n'
            self.pnlA.sizer.Add(wx.CheckBox(self.pnlA, id=1000 + i, label=labeltext, name="Data"),
                                wx.SizerFlags().Border(wx.LEFT, self.margin * 2))

        # Deal with sizers & sizing
        self.panels_sizers.extend([(self.pnl, self.sizer), (self.pnlA, self.pnlA.sizer)])
        self.set_sizers()
        self.SetSize(wx.Size(600, 600))

        self.list_of_data_ids_to_exclude_from_export = []
        self.sheet_name = None

        self.Bind(wx.EVT_BUTTON, self.OnEVTButton)
        self.Bind(wx.EVT_CHECKBOX, self.OnEVTCheckbox)
        self.Bind(wx.EVT_TEXT, self.OnEVTText)

    def get_non_excluded_data(self):
        data = []
        for i in range(0, len(self.data)):
            if i not in self.list_of_data_ids_to_exclude_from_export:
                data.append(self.data[i])  #
        return data

    def OnEVTButton(self, event):
        x_pos, y_pos = self.GetPosition()

        self.selected_sheet_id = wx.FindWindowById(self.frame_ids["txtbox current ID"], self.pnlA).GetLineText(0).strip()
        data = self.get_non_excluded_data()

        self.sheet_range = self.get_sheet_range(data)
        if event.GetEventObject().Id == 110:
            self.title = wx.FindWindowById(130, self.pnlA).GetLineText(0).strip()
            returned_id = changespreadsheets.main(data, title=self.title, sheet_range=self.sheet_range)
            from datetime import datetime
            self.existing_spreadsheets[returned_id] = (self.title,datetime.isoformat(datetime.now()))
            wx.FindWindowById(self.frame_ids["txtbox current ID"], self.pnlA).SetValue(returned_id)
            current_ticked_box = wx.FindWindowByName(self.selected_sheet_id,self.pnlA)
            if current_ticked_box is not None:
                current_ticked_box.SetValue(False)
        if event.GetEventObject().Id == 111:
            id = wx.FindWindowById(self.frame_ids["txtbox current ID"], self.pnlA).GetLineText(0).strip()
            if self.sheet_name is not None:
                self.sheet_range = "'" + self.sheet_name + "'" + "!" + self.sheet_range
            changespreadsheets.main(data, sheet_id=id, sheet_range=self.sheet_range)
        if event.GetEventObject().Id == 200:
            ChooseSheet(self, size=wx.Size(600, 600), pos=wx.Point(x_pos, y_pos), title='Sheet name popup', ).Show()

    def OnEVTText(self, event):
        # if text box changes remember sheet name - no longer relevant if box is readonly
        if event.GetEventObject().Id == 131:
            id = wx.FindWindowById(self.frame_ids["txtbox current ID"], self.pnlA).GetLineText(0).strip()
            if self.GetParent().selected_sheet_id != id:
                self.GetParent().selected_sheet_id = id

    def OnEVTCheckbox(self, event):
        # TODO: this does not replace the current spreadsheets to reflect newly created ones
        this_box = event.GetEventObject().GetName()
        a_box_already_recorded_as_checked = len(self.spreadsheet_box_checked) > 0
        this_box_checkstate = event.GetEventObject().Value
        if this_box == "Data":
            # add or remove ID of line of data from excluded ID list.
            id = event.GetEventObject().Id - 1000
            if this_box_checkstate is True:
                self.list_of_data_ids_to_exclude_from_export.append(id)
            if this_box_checkstate is False:
                self.list_of_data_ids_to_exclude_from_export.remove(id)
        elif this_box != "Data":
            # event.GetEventObject().GetName() is spreadsheet ID for non-data checkboxes
            # This is checked box we are unchecking
            if this_box in self.spreadsheet_box_checked and this_box_checkstate is False:
                wx.FindWindowById(self.frame_ids["txtbox current ID"], self.pnlA).SetValue("Select/create spreadsheet above to replace this text with an ID")
                self.spreadsheet_box_checked.remove(this_box)

            # the checked box is shown, we are checking another not one checked
            elif a_box_already_recorded_as_checked and wx.FindWindowByName(self.spreadsheet_box_checked[0],self.pnlA) != None and this_box_checkstate is True and this_box not in self.spreadsheet_box_checked:
                wx.MessageBox("Another sheet already selected - deselect that first then select one you want",caption="Conflict - deselect other box first")
                event.GetEventObject().SetValue(False)

            # the checked box is NOT shown (so current ID is from making newsheet), we are checking another not one checked
            elif (len(self.spreadsheet_box_checked) == 0) or (a_box_already_recorded_as_checked and wx.FindWindowByName(self.spreadsheet_box_checked[0],
                                   self.pnlA) is None and this_box_checkstate is True and this_box not in self.spreadsheet_box_checked):
                if a_box_already_recorded_as_checked:
                    self.spreadsheet_box_checked.pop(0)

                self.spreadsheet_box_checked.append(this_box)
                self.title = event.GetEventObject().GetLabel()
                wx.FindWindowById(self.frame_ids["txtbox current ID"], self.pnlA).SetValue(this_box)


class MainFrame(wx.Frame):
    """
    Frame that shows the tags list
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(MainFrame, self).__init__(*args, **kw)

        # create set of tags - used to determine if more than one box ticked
        self.tags = set()
        self.db = db_util(None)
        self.margin = 20
        self.multitag_added = False  # to check that multitags have not already been added.
        self.selected_sheet_id = None  # use by Google Sheets export to retrain existing sheet between closing and opening.
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
                                          label="Fields:"),
                            wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.25)))
        field_format_box = wx.Choice(self.pnlA, id=100, choices=[k for k in field_orders],
                                     name="Info format")
        self.pnlA.sizer.Add(field_format_box, wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.25)))
        self.pnlA.sizer.Add(wx.StaticText(self.pnlA,
                                          label="Export via:"),
                            wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        export_mechanism_box = wx.Choice(self.pnlA, id=101, choices=[k for k in export_mechanisms],
                                         name="Export mechanism")
        self.pnlA.sizer.Add(export_mechanism_box, wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.sizer.Add(1, 1, wx.SizerFlags().Border(wx.BOTTOM, int(self.margin * 0.5)))
        self.pnlB.sizer.Add(tags_area_message,
                            wx.SizerFlags().Border(wx.LEFT, self.margin * 2))
        self.pnlA.SetFocus()

        # record initial format choice and resent as needed via EVT_CHOICE
        export_mechanism_window = wx.FindWindowById(101, self.pnlA)
        export_choice_index = export_mechanism_window.GetSelection()
        self.export_choice = export_mechanism_window.GetString(export_choice_index)

        order_window = wx.FindWindowById(100, self.pnlA)
        order_choice_index = order_window.GetSelection()
        self.order_choice = order_window.GetString(order_choice_index)

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

        tags = self.db.get_tag_dict(self.db.get_tags())
        self.multitag_links_dict = self.db.dual_tag_non_zero_dict(double_tag_dict=self.db.get_dual_tag_dict(tags))
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

        self.SetSize(wx.Size(width, height + 1))
        panel.Layout()

    def data_formatter(self, data_piece, output_format):
        output_list = []
        for item in output_format:
            if isinstance(item,int):
                output_list.append(data_piece[item])
            elif repr(type(item)) == "<class 'function'>" and item.__name__ == 'html_link':
                if self.export_choice == "Export to Google Sheets - read help re: configuration":
                    output_list.append(sheets_link(data_piece))
                # if item is a function call it on the data (tuple etc.) and add result to output
                elif self.export_choice != "Export to Google Sheets - read help re: configuration":
                    output_list.append(item(data_piece))
        return tuple(output_list)

    def format_the_data(self, data, output_order):
        return_list = []
        for d in data:
            return_list.append(self.data_formatter(d, output_format=output_order))
        return return_list

    def open_or_export(self, export_choice):
        """Export file or opening window in response to event"""

        global html_page_source
        global pathname
        x_pos, y_pos = self.GetPosition()
        width, height = self.GetSize()
        # pure CSV for export is final format
        csv_choice = [k for k in export_mechanisms][-2]
        sheets_choice = [k for k in export_mechanisms][-1]
        non_html_choices = [csv_choice, sheets_choice]
        html_choice = [k for k in export_mechanisms][0]

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

        self.urls_titles_data = None
        for set_tuple in self.tags:
            tagID = set_tuple[0]
            title = set_tuple[1]
        # searching for && is checking for single tags
        is_dual_tag = [x for x in self.tags][0][1].find("&&") != -1
        # log_main.debug(f"star: {time.time()}")
        if is_dual_tag is False:
            # print("unformatted", self.db.urls_from_tagID(tagID))
            self.urls_titles_data = self.format_the_data(self.db.urls_from_tagID(tagID),
                                               field_orders[self.order_choice]["output_order"])
            # print("formatted as self.urls_titles_data", self.urls_titles_data,len(self.urls_titles_data),"data format length",len(field_orders[self.order_choice]["output_order"]))
            # log_main.debug(f'dualtag= {is_dual_tag}, self.urls_titles_data = {self.urls_titles_data}')
        if is_dual_tag is True:
            self.urls_titles_data = self.format_the_data(self.db.urls_from_combinedtagname(title, self.multitag_links_dict),
                                               field_orders[self.order_choice]["output_order"])
            title = title.replace("&&", "&")
            # log_main.debug(f'dualtag= {is_dual_tag}, self.urls_titles_data = {self.urls_titles_data}')
            # have HTML source in appropriate format - open in new window unless choice is to save to CSV directly

        if export_choice == html_choice:
            html_page_source = full_html(self.urls_titles_data, title)
            myHtmlFrame(self, size=wx.Size(800, 600), pos=wx.Point(x_pos + width, y_pos), title=title).SetPage(
                html_page_source, self.urls_titles_data).Show()
        elif export_choice == sheets_choice:
            # format the data
            # open a window with data
            # either open a new sheet or receive ID of existing sheet
            if os.path.exists("credentials.json") is not True or os.path.isfile("credentials.json") is not True:
                wx.MessageBox(
                    f'Read help file regarding \nnecessary configuration for\n export to Google Sheets\nIf you think credentials.json and\n token.json are present see if deleting both \nand redownloading credentials.json \nprompts successful browser-based authentication.',
                    caption="Need to configure for export to Google Sheets")
            if os.path.exists("credentials.json") is True and os.path.isfile("credentials.json") is True:
                ChooseSpreadsheet(self, size=wx.Size(600, 600), pos=wx.Point(x_pos + width, y_pos),
                                  title='Export to Sheets').Show()

        elif export_choice == csv_choice:
            csv_file_dialog(self.urls_titles_data)

    def OnEVTChoice(self, event):
        export_mechanism_window = wx.FindWindowById(101, self.pnlA)
        export_choice_index = export_mechanism_window.GetSelection()
        self.export_choice = export_mechanism_window.GetString(export_choice_index)
        # print("index", export_choice_index,"choice", self.export_choice)
        order_window = wx.FindWindowById(100, self.pnlA)
        order_choice_index = order_window.GetSelection()
        self.order_choice = order_window.GetString(order_choice_index)
        # print("index", order_choice_index, "choice", self.order_choice)
        if len(self.tags) == 1:
            # only one checkbox checked so changing format likely to indicate a different format wanted
            # so open or export
            self.open_or_export(self.export_choice)

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
                self.open_or_export(self.export_choice)


        elif event.GetEventObject().Name == "multitag_categories" and (
                self.db.specify_file_path() is not None) and event.GetEventObject().GetValue():
            if self.db.is_bookmarks_file():
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
        # pick file & set db instance

        with wx.FileDialog(self, "Open sqlite file", wildcard="sqlite files (*.sqlite)|*.sqlite",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # user changed their mind but no change to interface in that case
            pathname = fileDialog.GetPath()
            if len(pathname) == 0:
                return
            self.multitag_added = False
            # use the pathname just initiate a new database connection
            self.db = db_util(pathname)

        # remove and add back the lower Panel B
        self.tags = set()
        # Clear items from panel B
        self.pnlB.sizer.Clear(delete_windows=True)

        # log_main.debug(self.db.specify_file_path())
        if self.db.is_bookmarks_file():
            # append tags to lower Panel B
            self.pnlB.sizer.Add(wx.StaticText(self.pnlB,
                                              label="Entries with items tagged with tag below\ncheck box to show bookmarked links"),
                                wx.SizerFlags().Align(wx.TOP).Border(wx.LEFT, self.margin * 2))

            tags = self.db.get_tag_dict(self.db.get_tags())
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
            self.SetSize(wx.Size(width, height - 1))
        else:
            self.SetStatusText("Not an appropriate bookmarks file - try another file?")
            self.pnlB.sizer.Add(wx.StaticText(self.pnlB,
                                              label="Last opened file lacks necessary database tables (moz_places and moz_bookmarks)\nIs it a places.sqlite bookmarks file from Firefox browser?\nTry another sqlite file?"),
                                wx.SizerFlags().Border(wx.LEFT, self.margin * 2))

        self.set_sizers()

        self.pnl.Layout()
        # TODO: the following is terrible hack - changing by 1 pixel to get auto-layout working
        self.SetSize(wx.Size(width, height + 1))

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
        width, height = self.GetSize()
        title = "Tagged bookmarks export tool - Help"

        helpframe = wx.Frame(self, size=wx.Size(600, 600), )
        myHtmlFrame(helpframe, size=wx.Size(800, 600), pos=wx.Point(x_pos + width, y_pos), title=title).LoadFile(
            "help.html").Show()


class myHtmlFrame(wx.Frame):
    """
    A Frame of HTML that opens from Main Frame and contains a single HtmlWindow whose source is set with SetPage method
    """

    def __init__(self, *args, **kw):
        super(myHtmlFrame, self).__init__(*args, **kw)
        self.html_win = HtmlWindow(self, size=wx.Size(800, 600))
        self.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.OnClick)
        self.html_win.Bind(wx.EVT_TEXT_COPY, self.OnTextCopy)

    def SetPage(self, *args):
        # bookmarks window - make links available in appropriate format for copying as well as page source
        if len(args) == 2:
            source, urls_titles = args
            self.links = make_list_source_from_urls_titles(urls_titles)
            self.source = source
        self.html_win.SetPage(self.source)
        # log_main.debug(f"end: {time.time()}")
        return self

    def LoadFile(self, *args):
        # just used for help window
        self.html_win.LoadFile(args[0])
        return self

    def OnTextCopy(self, event):
        text = self.html_win.SelectionToText()
        # from random import randint # random int to log event fired
        # log_main.debug("Text copied ",randint(1,100))
        if wx.TheClipboard.Open():
            wx.TheClipboard.Clear()
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()

    def OnClick(self, event):
        """Handles when HTML link is clicked - opens in browser or saves HTML file for href == # """
        special_hrefs = ["#", "##"]
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
                        file.write(self.source.replace(instructional_text, ""))
                except IOError:
                    wx.LogError("Cannot save current data in file '%s'." % pathname)


if __name__ == '__main__':
    # create app, create main frame and show it and start event loop
    app = wx.App()
    frm = MainFrame(None, size=wx.Size(600, 600), title='Tagged bookmarks export tool')
    frm.Show()
    # wx.lib.inspection.InspectionTool().Show()  # uncomment for debugging via inspection tool
    app.MainLoop()
