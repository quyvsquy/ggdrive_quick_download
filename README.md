# ggdrive_quick_download
Download folder from google drive without zip, edited from [***jonathanTIE***](https://github.com/jonathanTIE/googledrive-copy-downloader)
## How to use: 
First, you need to add a Google application credentials(clients_secrets.json) that can access the Google drive API from your account.

To do that, the quickest way is to :
* Go to : https://developers.google.com/drive/api/v3/quickstart/python
* Click on enable drive API
* Download client configuration (credentials.json)
* Replace the one in the folder with the script (in the same place)

Finally, run this command `python3 qdownload.py` and follow step.
## Feature:
* Download folder without zip.
* Work with google files(sheet, docs,...).
