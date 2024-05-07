# copyright - modified by github.com/byjosh web@byjosh.co.uk
# but extensively based on code samples in Google documentation licensed
# under the Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# e.g. samples at https://developers.google.com/sheets/api/quickstart/python

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
#SAMPLE_SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
#SAMPLE_RANGE_NAME = "Class Data!A2:E"

""" You can find help docs relating to the following tasks at https://developers.google.com/workspace/guides/get-started
and in the sidebar for https://developers.google.com/sheets/api/quickstart/python

To use this 3 things need to be done at https://console.cloud.google.com/apis/dashboard under the APIs and Service part
1. Set up OAuth authentication screen and add yourself (and anyone you want to use the tool) as a test user
2. Create and download OAuth 2.0 Client ID and save this in the same folder as this file as credentials.json
3. Under Enabled APIs search for Google Sheets and enable that
As this app is not read only the scope of "https://www.googleapis.com/auth/spreadsheets" is needed and that is sensitive (as well as creating sheets it can read, edit, delete all your account's spreadsheets)
As the app uses a sensitive scope to enable its use in general without being added as a test user as above
would need the app to go through verification outlined here https://support.google.com/cloud/answer/13463073
The spreadsheet ID needed in this code can be found in the web interface by going to the sheet and 
after the final forward slash in https://docs.google.com/spreadsheets/d/ everything before the next forward slash is the ID
So if the URL was https://docs.google.com/spreadsheets/d/1-ABC123def/edit#gid=0 then 1-ABC123def would be the ID 
in reality the ID will be much longer and more random

"""

def rearrange_fields_for_output(data,dataorder,outputorder):
    """
    Move this to main file - data should come pre-ordered
    takes indexable iterables and returns another with the fields rearranged using list comprehension
    ("https://example.com","Example - Home Page", "Home page of the famous example.com - as used in all the best documentation")
     and ("url","title","description") and ("title","description","url")

     >>> rearrange_fields_for_output(("https://example.com","Example - Home Page", "Home page of the famous example.com - as used in all the best documentation"),("url","title","description"),("title","description","url"))
     ('Example - Home Page', 'Home page of the famous example.com - as used in all the best documentation', 'https://example.com')


    :param data
    :param dataorder
    :param fieldorder


    """
    return tuple([data[dataorder.index(field)] for field in outputorder])

def test(a: int, b: int) -> int:
    pass

def main(data,**kwargs):
  """mode,datadict
  parse in whether we are creating a new sheet (title supplied) or updating existing sheet (id supplied)#
  parse in the data to export urls, title - keys of data, field order (need to think about field order - probably invariant in data - but variable in output - by building lines)
  :param kwargs : dict of title or sheet_id
  :param data : dict


  """
  # convert any tuples to lists
  data = [list(x) for x in data]


  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  def create(title):
      """
      Creates the Sheet the user has access to.
      Load pre-authorized user credentials from the environment.
      TODO(developer) - See https://developers.google.com/identity
      for guides on implementing OAuth2 for the application.
      """


      # pylint: disable=maybe-no-member
      try:
          service = build("sheets", "v4", credentials=creds)
          spreadsheet = {"properties": {"title": title}}
          spreadsheet = (
              service.spreadsheets()
              .create(body=spreadsheet, fields="spreadsheetId")
              .execute()
          )
          print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
          return spreadsheet.get("spreadsheetId")
      except HttpError as error:
          print(f"An error occurred: {error}")
          return error

  def update_values(spreadsheet_id, range_name, value_input_option, _values):
      """
      Creates the batch_update the user has access to.
      Load pre-authorized user credentials from the environment.
      TODO(developer) - See https://developers.google.com/identity
      for guides on implementing OAuth2 for the application.
      """

      # pylint: disable=maybe-no-member
      try:
          service = build("sheets", "v4", credentials=creds)
          values = [
              [
                  # Cell values ...
              ],
              # Additional rows ...
          ]
          values = _values
          body = {"values": values}
          result = (
              service.spreadsheets()
              .values()
              .update(
                  spreadsheetId=spreadsheet_id,
                  range=range_name,
                  valueInputOption=value_input_option,
                  body=body,
              )
              .execute()
          )
          print(f"{result.get('updatedCells')} cells updated.")
          return result
      except HttpError as error:
          print(f"An error occurred: {error}")
          return error

  def hyperlink(url,title):
      """ Move to main file - this should be agnostic as to format of data
      Hyperlink works if href and title doublequoted in singlequoted string"""
      return '=HYPERLINK("' + f'{url }' + '"," ' + f'{title}' + '")'

  try:
    service = build("sheets", "v4", credentials=creds)
    sheetID = ""
    if "sheet_id" in kwargs:
        sheetID = kwargs["sheet_id"]
    if "sheet_id" not in kwargs and "title" in kwargs:
        sheetID = create(kwargs["title"])
    range_name = kwargs["sheet_range"]
    update_values(sheetID, range_name,"USER_ENTERED",data,)
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=sheetID, range=range_name,valueRenderOption="FORMULA" )
        .execute()
    )

    values = result.get("values", [])

    if not values:
      print("No data found.")
      return

    print("Result:- ",result)
    for row in values:
      # Print columns A and E, which correspond to indices 0 and 4.
      print(f"{row}")
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()