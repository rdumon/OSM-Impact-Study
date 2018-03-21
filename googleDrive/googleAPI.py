"""
Module responsible for creating folders and files
"""
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class googleAPI:

    gauth = None
    
    def __init__(self):
        self.gauth = GoogleAuth()
        self.gauth.LocalWebserverAuth()

    def upload_GoogleDrive(self,filename = '',filelocation = '', dir_id = '', filetype = ''):
    
        drive = GoogleDrive(self.gauth)
        file = drive.CreateFile({'title':filename, 'mimeType':filetype,
                "parents": [{"kind": "drive#fileLink","id": dir_id}]})

        file.SetContentFile(filelocation)
        file.Upload()
        print("Uploaded to Google Drive: " + filename)

    # finds a folder and creates one if it does not exits 
    def createFolder(self,foldername = '', dir_id = ''):

        drive = GoogleDrive(self.gauth)

        if dir_id == '':
            file = drive.CreateFile({'title':foldername, 'mimeType':'application/vnd.google-apps.folder'})
            file.Upload()
            return file['id']

        file = drive.CreateFile({'title':foldername, 'mimeType':'application/vnd.google-apps.folder',"parents": [{"kind": "drive#fileLink","id": dir_id}]})
        file.Upload()
        return file['id']


