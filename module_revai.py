from rev_ai.models import CustomVocabulary
from rev_ai import apiclient
import time
from config_con import *
from module_main_fuctions import *

client = apiclient.RevAiAPIClient(REV_API)


class REV_AI(object):

    def __init__(self):
        self.client = apiclient.RevAiAPIClient(REV_API)
        self.status = None

    def convert_start(self, path):
        try:
            job_id = self.client.submit_job_local_file(filename=path, language='ru').id
            print(job_id)
            time.sleep(2)
            self.status = str(self.client.get_job_details(job_id).status)
            return job_id
        except Exception as e:
            print(e)
            return e


    def convert1(self, job_id):
        job_id = job_id
        if self.status == 'JobStatus.TRANSCRIBED':
            text = self.client.get_transcript_text(job_id)
            time.sleep(2)
            text2 = (text[25:])
            return text2
        elif self.status == 'JobStatus.FAILED':
            return 'FAILED'
        else:
            self.status = str(self.client.get_job_details(job_id).status)
            print(f'Current status: {self.status}')
            time.sleep(2)
            return self.convert1(job_id)



# def decorator(func):
#     def wrapper():
#         func()
#
#     return wrapper


# job_id = client.submit_job_local_file(filename=f'./FILES/TEST/audio2.ogg', language='ru').id
# print(job_id)
# job_id = 'rCfgZDUUam7Z'
# job_details = client.get_job_details(job_id)
# print(job_details.)
















