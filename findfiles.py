# copyright - modified by github.com/byjosh web@byjosh.co.uk
# but extensively based on code samples in Google documentation licensed
# under the Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# e.g. samples at https://developers.google.com/drive/api/guides/search-files

import os.path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from auth_flow import get_valid_credential

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def search_file():
  """Search file in drive location

  """
  creds = get_valid_credential()

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