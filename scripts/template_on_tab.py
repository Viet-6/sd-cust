import modules.scripts as scripts
import gradio as gr
import os

from modules import script_callbacks

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import os
import shutil

SCOPES1 = ['https://www.googleapis.com/auth/drive']

SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = '/content/publics/client_secrets.json'
FOLDER_ID = '' # If you want to upload the file to a specific folder

def upload_to_drive(file_path):
    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {'name': os.path.basename(file_path), 'mimeType': 'application/zip'}
    if FOLDER_ID:
        file_metadata['parents'] = [FOLDER_ID]

    media = MediaFileUpload(file_path, mimetype='application/zip', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media,
                                        fields='id').execute()
    print(F'File ID: {file.get("id")}')

    file_path = '/kaggle/working/id.txt'  # Replace with the desired file path
    # Open the file in write mode
    with open(file_path, 'w') as f:
        f.write(file.get("id"))

# Example usage: 


def save():

    folder_name = '/content/gdrive'
    my_archive = '/content/my_archive'
    shutil.make_archive(my_archive, 'zip', folder_name)
    upload_to_drive('/content/my_archive.zip')
    
    return

def delete():
    # Build the credentials object
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES1)

    # Create a Drive API service instance
    service = build('drive', 'v3', credentials=credentials)

    # The specific file ID to keep in My Drive
    file_to_keep_id = ""

    file_path = '/kaggle/working/id.txt'
    with open(file_path, 'r') as file:
        file_to_keep_id = file.read()

    try:
        # Search for all files in My Drive.
        query = ""
        results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        # Loop through each file and delete if it's not the target file.
        for item in items:
            if item['id'] != file_to_keep_id:
                # Delete the file.
                service.files().delete(fileId=item['id']).execute()

    except Exception as e:
        print(f"An error occurred: {e}")
    


def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            btn = gr.Button(value="Save")
            btn2 = gr.Button(value="Delete")
            # TODO: add more UI components (cf. https://gradio.app/docs/#components)
        btn.click(save)
        btn2.click(delete)
        return [(ui_component, "Extension Template", "extension_template_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)