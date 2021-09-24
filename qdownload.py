# -*- coding: utf-8 -*-
from googleapiclient import errors
from colorama import init,Fore,Back,Style
from termcolor import colored
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from httplib2 import Http
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import sys
import re

SCOPES = 'https://www.googleapis.com/auth/drive'
def main():
    """
    Download folder content from google dirve without zipping.
    """
    init()

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)
    print(colored('* Directory to save - enter to use current directory', 'blue'))
    folderName = input("   - Path: ")
    if not folderName:
        folderName = "./"
    if not os.path.exists(folderName):
        os.makedirs(folderName)
    print(colored('* GDrive Folder/File ID: ','blue'))
    id = input("   - ID  : ")
    while not id:
        id = input("   - ID  : ")

    try:
        getID = service.files().get(fileId=id,fields='id, name, mimeType, size').execute()
        
        file_id = getID['id']
        filename = no_accent_vietnamese(getID['name'])
        mime_type = getID['mimeType']
        if mime_type == 'application/vnd.google-apps.folder':
            print("Get",colored(filename, 'cyan'))
            download_folder(service, file_id, folderName, "",0)
        elif not os.path.isfile(f'{folderName}/{filename}'):
            print("Get",colored(filename, 'cyan'))
            download_file(service, file_id, folderName, filename, mime_type)
        else:
            print("Get",colored(filename, 'cyan'))
            remote_size = getID['size']
            local_size = os.path.getsize(f'{folderName}/{filename}')
            if (str(remote_size) == str(local_size)):
                print(colored('File existed!', 'magenta'))
            else:
                print(colored('Local File corrupted', 'red'))
                os.remove(f'{folderName}{filename}')
                download_file(service, file_id, folderName, filename, mime_type)

        # download_folder(service, id,folderName,"")

    except errors.HttpError as error:
        print('An error occurred: {}'.format(error))

def download_folder(service, folder_id, location, folder_name, sizeTab):
    sizeTab += 1
    if not os.path.exists(location + folder_name):
        os.makedirs(location + folder_name)
    location += f"{folder_name}/"

    result = []
    files = service.files().list(
            q=f"'{folder_id}' in parents",
            fields='files(id, name, mimeType, size)').execute()
    result.extend(files['files'])
    result = sorted(result, key=lambda k: k['name'])

    total = len(result)
    print(" "*sizeTab,colored('Folder is empty!', 'red')) if total ==0   else\
        print(" "*sizeTab,colored('START DOWNLOADING', 'yellow'))

    current = 1
    for item in result:
        file_id = item['id']
        filename = no_accent_vietnamese(item['name'])
        mime_type = item['mimeType']
        print('-'*sizeTab, colored(filename, 'cyan'), colored(mime_type, 'cyan'),f'({current}/{total})')
        current += 1
        if mime_type == 'application/vnd.google-apps.folder':
            download_folder(service, file_id, location, filename, sizeTab)
        elif not os.path.isfile(f'{location}{filename}'):
            download_file(service, file_id, location, filename, mime_type)
        else:
            remote_size = item['size']
            local_size = os.path.getsize(f'{location}{filename}')
            if (str(remote_size) == str(local_size)):
                print(" "*sizeTab,colored('File existed!', 'magenta'))
            else:
                print(" "*sizeTab,colored('Local File corrupted', 'red'))
                os.remove(f'{location}{filename}')
                download_file(service, file_id, location, filename, mime_type)

def download_file(service, file_id, location, filename, mime_type):
    def support_download_file(name, type_format):
        fwrite = open(f"{location}/{filename}{name}", 'wb')
        request = service.files().export_media(fileId=file_id,mimeType=type_format) if name != "" else\
            service.files().get_media(fileId=file_id)
        response = request.execute()
        fwrite.write(response)

    if mime_type == "application/vnd.google-apps.spreadsheet":
        support_download_file(".xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif mime_type == "application/vnd.google-apps.document":
        support_download_file(".docx","application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    elif mime_type != "application/vnd.google-apps.form":
        support_download_file("",None)

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def no_accent_vietnamese(s):
    s = re.sub('[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub('[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub('[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub('[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub('[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub('[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub('[ìíịỉĩ]', 'i', s)
    s = re.sub('[ÌÍỊỈĨ]', 'I', s)
    s = re.sub('[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub('[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub('[ỳýỵỷỹ]', 'y', s)
    s = re.sub('[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub('[Đ]', 'D', s)
    s = re.sub('[đ]', 'd', s)
    return s

if __name__ == '__main__':
    # python3 qdownload.py
    main()
