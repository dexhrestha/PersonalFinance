from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import os
import pickle
import pandas as pd

class Drive():
    def __init__(self,token_path='credentials/g_token.pickle',
                 cred_path='credentials/gdrive-cred.json',port=8088):
        self.drive = None 
        self.token_path = token_path
        self.cred_path = cred_path
        self.port= port
        try:
            self.authenticate()
        except:
            self.drive = None

    def authenticate(self):
        """Authenticate the user and return the Google Drive service."""
        gauth = GoogleAuth()
        gauth.LoadClientConfigFile(self.cred_path)

        # Try to load saved client credentials
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                gauth.credentials = pickle.load(token)

        # If credentials are not available or invalid, perform manual authentication
        if not gauth.credentials or gauth.credentials.invalid:
            # gauth.LocalWebserverAuth(port_numbers=[self.port])  # This will open a new window/tab in your default browser for authentication
            gauth.LocalWebserverAuth()

            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(gauth.credentials, token)

        elif gauth.access_token_expired:
            gauth.Refresh()

        self.drive = GoogleDrive(gauth)
    

    def get_files_from_folder(self,folder_id):
        files_in_folder =  self.drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        files_in_folder = {f['id']:f['title'] for f in files_in_folder}
        return files_in_folder


    def upload_to_drive(self, folder_id, filepath):
        # Get the file name
        file_name = os.path.basename(filepath)
        
        # Get all files in the folder
        files_in_folder = self.get_files_from_folder(folder_id)
        # Check if a file with the same name exists
        for file_id, title in files_in_folder.items():
            if title == file_name:
                # If the file exists, delete it
                file_to_delete = self.drive.CreateFile({'id': file_id})
                file_to_delete.Delete()
                print(f"File '{title}' deleted successfully")

        # Create a new file and upload
        gfile = self.drive.CreateFile({'title': file_name, 'parents': [{'id': folder_id}]})
        gfile.SetContentFile(filepath)
        gfile.Upload()  # Upload the file
        print(f"File '{gfile['title']}' uploaded successfully")

    
    def get_files(self, folder_id):
        """Get a list of files in a specific Google Drive folder."""
        file_list = self.drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
        files = [{'title': file['title'], 'id': file['id']} for file in file_list]
        return files

    def download_file(self,file_id, destination='temp'):
        """Download a single file from Google Drive."""        
        file = self.drive.CreateFile({'id': file_id})
        file_id = file['id']
        file_name = file['title']
        mime_type = file['mimeType']
        
        # Determine the correct download method based on the file type
        if 'application/vnd.google-apps' in mime_type:
            # Export Google Docs/Sheets/Slides to a suitable format
            if mime_type == 'application/vnd.google-apps.document':
                export_mime = 'application/pdf'
            elif mime_type == 'application/vnd.google-apps.spreadsheet':
                export_mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif mime_type == 'application/vnd.google-apps.presentation':
                export_mime = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            else:
                print(f"Cannot export file type: {mime_type}")
                return
            
            print(f"Exporting {file_name}...")
            file.GetContentFile(os.path.join(destination, file_name + '.exported'), mimetype=export_mime)
        else:
            print(f"Downloading {file_name}...")
            file.GetContentFile(os.path.join(destination, file_name))
        
        print(f"Downloaded {file_name} to {destination}")
        return os.path.join(destination, file_name)
    
    def read_excel_file(self,file_id):
        file_path = self.download_file(file_id)
        df =  pd.read_excel(file_path)
        os.remove(file_path)
        return df


if __name__=="__main__":
    g_client = Drive(token_path='credentials/g_token.pickle',cred_path='credentials/gdrive-cred.json')
    print(g_client.download_file('1Q3O3RXfL_2ddAubcvGDt9VqTtD2jsl2w','temp'))
