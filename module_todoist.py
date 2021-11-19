from todoist.api import TodoistAPI
from config_con import *
from module_main_fuctions import MODULE_MAIN
import os


TODOLIST_API = os.environ.get('TODOLIST_API')
m1 = MODULE_MAIN()
api = TodoistAPI(TODOLIST_API)


class TODOIS_MODULE(object):

    def __init__(self):
        self.PROJECT_Inbox = 2274604287
        self.PROJECT_TEST = 2274604468
        self.PROJECT_ALL = 2274844218
        self.LABEL_IT = 2158326746
        self.LABEL_SEX = 2158364220
        self.LABEL_MUSIC = 2158364215
        self.LABEL_OTHER = 2158364628

    def task_add_simple(self, task_project='', task_name='default_task777', task_text='default_task77777777', task_labels=''):
        api.sync()
        # task_labels = [TODOLIST_LABEL_FAMILY]
        task_project = TODOLIST_PROJECT_TEST
        try:
            result = api.items.add(content=task_name, project_id=task_project, description=task_text, labels=task_labels)
            api.commit()
            # print(result['id'])
            return result['id']
        except Exception as error:
            return error

    def task_add_reminder(self, task_project='', task_name='default_task', task_text='default_task', task_labels='', date='завтра'):
        api.sync()
        task_due_date = {
            "string": date,
            "lang": "ru"
        }
        task_project = TODOLIST_PROJECT_TEST
        try:
            result = api.items.add(content=task_name, project_id=task_project, description=task_text, labels=task_labels, due=task_due_date)
            api.commit()
            return result['id']
        except Exception as error:
            return None

    def add_comment_text(self, task_id, task_comment):
        api.sync()
        try:
            result = api.notes.add(item_id=task_id, content=task_comment)
            print(result)
            api.commit()
            return 'ok'
        except Exception as error:
            return error

    def add_comment_file(self, task_id, task_comment, task_type, task_attachment):
        api.sync()
        task_id = task_id
        task_attachment = {
            'file_name': f'{task_comment}.pdf',
            'file_type': task_type,
            'file_url': task_attachment,
            "upload_state": "completed"
        }
        try:
            api.notes.add(item_id=task_id, content=task_comment, file_attachment=task_attachment)
            api.commit()
            return 'ok'
        except Exception as error:
            return error

    def add_comment_file2(self):
        try:
            file_attachment = {
                "file_type": "text",
                "file_name": "File1.doc",
                "file_url": "https://www.dropbox.com/s/hlfw37plc7lcrzh/21073_50886609.doc?dl=0",
                "upload_state": "completed"
            }
            api.sync()
            api.notes.add(item_id=TODOLIST_TASK_SEX, content='task_comment', file_attachment=file_attachment)
            api.commit()
            api.sync()
            return 'ok'
        except Exception as error:
            return error


    def filter_add(self):
        api.sync()
        filter = api.filters.add('Filter2', 'due')
        api.commit()

    def task_get_all(self):
        api.sync()
        result1 = api.completed.get_all()
        result2 = api.items.all()
        result3 = api.items.get_completed(TODOLIST_PROJECT_ALL)
        result5 = api.projects.all(2274844218)
        result6 = api.items.delete()
        result7 = api.items.get()

    def projects_get_all(self):
        api.sync()
        result = api.state['projects']
        return result


    def project_get_info(self, project='IT', option=2):
        api.sync()
        result = []
        info = api.projects.get_data(project)
        if option == 1:
            for item in info['sections']:
                section_id = item['id']
                section_name = item['name']
                result.append([section_name, section_id])
            return result
        if option == 2:
            for task in info['items']:
                task_id = task['id']
                task_name = task['content']
                result.append([task_name, task_id])
            return result
        else:
            return 'NA'


    def delete_all(self):
        api.sync()
        # for filter in api.state['filters'][:]:
        #     print(filter)
            # filter.delete()
            # api.commit()
        # for label in api.state['labels'][:]:
        #     print(label)
            # label.delete()
            # api.commit()
        # for reminder in api.state['reminders'][:]:
        #     reminder.delete()
        #     api.commit()
        for note in api.state['notes'][:]:
             note.delete()
             api.commit()
        for note in api.state['project_notes'][:]:
            note.delete()
            api.commit()
        for item in api.state['items'][:]:
            pr_id = item['project_id']
            item = api.items.get()
            api.sync()
            if pr_id == TODOLIST_PROJECT_OTHER:
                api.sync()
                item.delete()
                api.commit()
        for project in api.state['projects'][:]:
            if project['name'] == 'TEST':
                 project.item.delete()
                 api.commit()

    def uploads_add(self):
        api.sync()
        try:
            result = api.uploads.add('https://www.dropbox.com/s/dvk6pc6vqjop8ei/Kupibilet_ru_3304551585.pdf')
            return result
        except Exception as error:
            return error

    def uploads_get(self):
        api.sync()
        try:
            result = api.uploads.get()
            return result
        except Exception as error:
            return error

    def section_info(self, section_id=''):
        api.sync()
        info = api.state['sections']
        print(info)
        try:
            result = api.sections.get_by_id(section_id)
            return result
        except Exception as error:
            return error

    def note_delete(self):
        all = api.state['notes']
        # api.notes.delete()
        for note in all:
            task = note['item_id']
            id = note['id']
            if task == TODOLIST_TASK_SEX:
                note.delete()
                api.commit()
                print('Success!')

# "Todoist: default_task22" <add.comment.35737651.5205549837.NTUwOTljNGJbo7WvqoBuQejz5kr0_7FF@todoist.net>

# https://todoist.com/showTask?id=5205469170
# image = 'image/jpeg'
# exe = 'application/x-msdos-program'
# rar = 'application/vnd.rar'
#
#


# t1 = TODOIS_MODULE()
# t1.add_comment_text(task_id=TODOLIST_TASK_OTHER, task_comment='sasd')


# if i['item_id'] == '5275731331' or '5302503083':
#     print(i)



# result = td1.add_comment_file(task_id=TODOLIST_TASK_SEX, task_comment=comment, task_type=type, task_attachment=path)
# print(result)




# # # print(td1.uploads_add())
# # # task_id = td1.task_add_simple()
# # # print(f'https://todoist.com/showTask?id={task_id}')
# #
# #
# result = td1.add_comment(TODOLIST_TASK_IT_INFO, task_comment='aaaaaaaaaaaaa')
# print(result)
# print(result[0][1])
# result2 = td1.section_info(result[0][1])
# print(result2)



# api.sync()
#
# all = api.notes.get()
# api.notes.delete()
# for i in all:
#     print(i)
#     print(i.get('id'))
#     try:
#         id = i.get('id')
#         item = api.items.get_by_id(id)
#         item.delete()
#         api.commit()
#         print('Success!')
#     except Exception as error:
#         print(error)









