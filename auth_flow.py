# copyright - modified by github.com/byjosh web@byjosh.co.uk
# but extensively based on code samples in Google documentation licensed
# under the Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# e.g. samples at https://developers.google.com/drive/api/guides/search-files

# This file is provide an auth function for use in other Google Sheets related files in this project
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def get_valid_credential():
    """Returns a value for creds - after handling auth
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    def run_auth_flow():
        """Run authorisation flow - in theory only needed in file responsible for selecting original spreadsheet"""
        flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
        creds = flow.run_local_server(port=0)
        return creds


    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as error:
                print("Had an error ", error)
                creds = run_auth_flow()
        else:
            creds = run_auth_flow()
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds




if __name__ == "__main__":
  get_valid_credential()