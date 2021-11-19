import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
import os
from config_con import *


class DROPBOX_MODULE(object):

    def __init__(self):
        self.dbx = dropbox.Dropbox(DROPBOX_TOKEN_ACCOUNT)

    def drop_list_folders(self, FOLDER_NAME):
        try:
            for folder in self.dbx.files_list_folder(FOLDER_NAME).entries:
                print(folder.path_lower)
            return 'ok'
        except Exception as e:
            return str(e)

    def drop_upload_file(self, FILE, PATHTO):
        try:
            with open(FILE, 'rb') as f:
                result = self.dbx.files_upload(f.read(), path=PATHTO, mode=WriteMode('overwrite'))
                PATH_LOCAL = result.path_display
                PATH_ALL = 'https://www.dropbox.com/home' + PATH_LOCAL
            return PATH_ALL
        except Exception as e:
            return str(e)


# d1 = DROPBOX_MODULE()
# FILE = './FILES/1346.json'
# PATHTO = '/INFO/OTHER/TASK_SEX/1346.json'
# r = d1.drop_upload_file(FILE, PATHTO)
# print(r)
