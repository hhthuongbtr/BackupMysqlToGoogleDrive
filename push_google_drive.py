#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: k.scherban@gmail.com
# license: GPL v.2 or higher

import sys
import logging
import httplib2
from mimetypes import guess_type

# Following libraries can be installed by executing:
# sudo pip install --upgrade google-api-python-client
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient.errors import ResumableUploadError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage


# Log only oauth2client errors
logging.basicConfig(level="ERROR")

# Path to token json file, it should be in same directory as script
token_file = sys.path[0] + '/auth_token.txt'

# Copy your credentials from the APIs Console
CLIENT_ID = '250053787781-44qvgbjjs844c3gvrdjlhcfr2l6vb2am.apps.googleusercontent.com'
CLIENT_SECRET = 'NRVGs3z7arhBOMP-ttsMKfXB'
# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive.file'
# Redirect URI for installed apps, can be left as is
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


# Get mime type and name of given file
def file_ops(file_path):
    mime_type = guess_type(file_path)[0]
    mime_type = mime_type if mime_type else 'text/plain'
    file_name = file_path.split('/')[-1]
    return file_name, mime_type


def create_token_file(token_file):
# Run through the OAuth flow and retrieve credentials
    flow = OAuth2WebServerFlow(
        CLIENT_ID,
        CLIENT_SECRET,
        OAUTH_SCOPE,
        redirect_uri=REDIRECT_URI
        )
    authorize_url = flow.step1_get_authorize_url()
    print('Go to the following link in your browser: ' + authorize_url)
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage = Storage(token_file)
    storage.put(credentials)
    return storage


def authorize(token_file, storage):
# Get credentials
    if storage is None:
        storage = Storage(token_file)
    credentials = storage.get()
# Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    credentials.refresh(http)
    http = credentials.authorize(http)
    return http


def upload_file(file_path, file_name, mime_type):
    folder_id = '0B17sjMjBXJloX3J2RTlUX19rczA'
    file_metadata = {
      'name' : file_name,
      'parents': [ folder_id ]
    }
# Create Google Drive service instance
    drive_service = build('drive', 'v3', http=http)
    media = MediaFileUpload(file_path,
                            mimetype=mime_type,
                            resumable=True)
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    return 'File ID: %s' % file.get('id')

if __name__ == '__main__':
# Check if file provied as argument and exists
    if len(sys.argv) != 2:
        print("One file should be provided as argument")
        sys.exit(1)
    else:
# Path to the file to upload
        file_path = sys.argv[1]
        print file_path
    try:
        with open(file_path) as f: pass
    except IOError as e:
        print(e)
        sys.exit(1)
# Check if token file exists, if not create it by requesting authorization code
    try:
        with open(token_file) as f: pass
    except IOError:
        http = authorize(token_file, create_token_file(token_file))
# Authorize, get file parameters, upload file and print out result URL for download
    http = authorize(token_file, None)
    file_name, mime_type = file_ops(file_path)
# Sometimes API fails to retrieve starting URI, we wrap it.
    try:
        print(upload_file(file_path, file_name, mime_type))
    except ResumableUploadError as e:
        print("Error occured while first upload try:", e)
        print("Trying one more time.")
        print(upload_file(file_path, file_name, mime_type))
