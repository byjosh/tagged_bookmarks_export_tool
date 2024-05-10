# copyright - modified by github.com/byjosh web@byjosh.co.uk
# but extensively based on code samples in Google documentation licensed
# under the Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# e.g. samples at https://developers.google.com/drive/api/guides/search-files

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def search_file():
  """Search file in drive location

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """


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

  try:
    # create drive api client
    service = build("drive", "v3", credentials=creds)
    files = []
    page_token = None
    while True:
      # pylint: disable=maybe-no-member
      response = (
          service.files()
          .list(
              q="mimeType='application/vnd.google-apps.spreadsheet' and trashed = False",
              spaces="drive",
              fields="nextPageToken, files(id, name,createdTime)",
              pageToken=page_token,
          )
          .execute()
      )
      #for file in response.get("files", []):
        # Process change
        #print(f'Found file: {file.get("name")}, {file.get("id")}')
      files.extend(response.get("files", []))
      page_token = response.get("nextPageToken", None)
      if page_token is None:
        break

  except HttpError as error:
    print(f"An error occurred: {error}")
    files = None

  return {file['id']:(file['name'],file['createdTime']) for file in files}


if __name__ == "__main__":
  search_file()