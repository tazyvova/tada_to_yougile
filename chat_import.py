import re
from datetime import datetime as dt
from yougile import yougile
from tada import tada


class from_tada_to_yougile:

    # creating usefull yougile chat dict
    def create_tada_contact_dict(self, tada_cont_list, yougile_users_list):
        tada_cont_dict = {}
        for tada_cont in tada_cont_list:
            matched_id = None
            for yougile_cont in yougile_users_list:
                if yougile_cont['realName'] == tada_cont['display_name'] or yougile_cont['email'] == tada_cont['contact_email']:
                    matched_id = yougile_cont['id']
                    break
            tada_cont_dict[tada_cont['jid']] = {
                "display_name": tada_cont['display_name'],
                "contact_email": tada_cont['contact_email'],
                "contact_phone": tada_cont['contact_phone'],
                "yougile_user_id": matched_id
            }
        return tada_cont_dict

    # creating usefull yougile tasks dict
    def create_yougile_task_dict(self):
        yougile_task_dict = {}
        yougile_taks_offset = 0
        yougile_task_list = self.yg.get_tasks(offset=yougile_taks_offset)
        while yougile_task_list['paging']['count'] > 0:
            for yougile_task_head in yougile_task_list['content']:
                if 'description' in yougile_task_head.keys():
                    re_result = re.search(
                        ".*({'jid': '([^']{38})'})$|^([^ ]{38})$", yougile_task_head['description'])
                    if re_result:
                        tada_task_jid = re_result.group(
                            2) or re_result.group(3)
                        if 'columnId' in yougile_task_head.keys():
                            yougile_columnId = yougile_task_head['columnId']
                        else:
                            yougile_columnId = self.yg.def_columnId
                        yougile_task_dict[tada_task_jid] = {
                            "id": yougile_task_head['id'],
                            "title": yougile_task_head['title'],
                            "columnId": yougile_columnId,
                            "description": yougile_task_head['description']}
            yougile_taks_offset = yougile_taks_offset + \
                yougile_task_list['paging']['count']
            yougile_task_list = self.yg.get_tasks(offset=yougile_taks_offset)
        print(
            f"Linked {str(len(yougile_task_dict))} yougile tasks from {str(yougile_taks_offset)}")
        return yougile_task_dict

    # creating usefull yougile chat dict
    def create_yougile_chat_dict(self):
        yougile_chat_dict = {}
        yougile_chat_offset = 0
        yougile_chat_list = self.yg.get_chats(offset=yougile_chat_offset)
        while yougile_chat_list['paging']['count'] > 0:
            for yougile_chat_head in yougile_chat_list['content']:
                if 'title' in yougile_chat_head.keys():
                    re_result = re.search(
                        ".*({'jid': '([^']{38})'})$|^([^ ]{38})$", yougile_chat_head['title'])
                    if re_result:
                        tada_chat_jid = re_result.group(
                            2) or re_result.group(3)
                        yougile_chat_dict[tada_chat_jid] = {
                            "id": yougile_chat_head['id'],
                            "title": yougile_chat_head['title']}
            yougile_chat_offset = yougile_chat_offset + \
                yougile_chat_list['paging']['count']
            yougile_chat_list = self.yg.get_chats(offset=yougile_chat_offset)
        print(
            f"Linked {str(len(yougile_chat_dict))} yougile chats from {str(yougile_chat_offset)}")
        return yougile_chat_dict

    def __init__(self, tada_token, tada_id_team, yougile_token, yougile_def_columnId, yougile_def_userID, prepare_tasks=1, prepare_chats=1):
        self.td = tada(
            tada_token,
            tada_id_team
        )
        self.yg = yougile(
            yougile_token,
            yougile_def_columnId  # getting column where to send new tasks
        )
        #reorganize contacts dict to access it with a jid
        if tada_token and tada_id_team and yougile_token and yougile_def_columnId:
            tada_contact_list_result = self.td.get_contacts()['result']
            yougile_users_list_result = self.yg.get_users_list()['content']
            self.tada_cont_dict = self.create_tada_contact_dict(
                tada_contact_list_result, yougile_users_list_result)
            if prepare_tasks == 1:
                self.yougile_task_dict = self.create_yougile_task_dict()
            if prepare_chats == 1:
                self.yougile_chat_dict = self.create_yougile_chat_dict()
        self.yougile_def_userID = yougile_def_userID

    def upd_yougile_task_dict(self, tada_task):
        cur_tada_task_jid = tada_task["jid"]
        if 'description' in tada_task.keys():
            yougile_task_descripton = tada_task['description'] + \
                str({'jid': cur_tada_task_jid})
        else:
            yougile_task_descripton = str({'jid': cur_tada_task_jid})
        if not cur_tada_task_jid in self.yougile_task_dict:
            # create new yougile task
            new_task_res = self.yg.post_new_task(
                tada_task['display_name'], self.yg.def_columnId, yougile_task_descripton)
            yougile_task_id = new_task_res['id']
            # add new yougile task into dict
            self.yougile_task_dict[cur_tada_task_jid] = {
                "id": yougile_task_id,
                "title": tada_task['display_name'],
                "columnId": self.yg.def_columnId,
                "description": yougile_task_descripton}
            print('Added task '+tada_task['display_name'])
        else:
            yougile_task_id = self.yougile_task_dict[cur_tada_task_jid]['id']
            if yougile_task_descripton != self.yougile_task_dict[cur_tada_task_jid]['description']:
                self.yg.change_task(yougile_task_id, yougile_task_descripton)
                self.yougile_task_dict[cur_tada_task_jid]['description'] = yougile_task_descripton
                print('Changed description' +
                      self.yougile_task_dict[cur_tada_task_jid]['description']+' to '+yougile_task_descripton)  # debug
        return yougile_task_id

    def get_yougile_chat_dict(self, tada_chat):
        notif_disable = {"notified": False}
        cur_tada_chat_jid = tada_chat["jid"]
        yougile_chat_title = tada_chat['display_name'] + \
            str({'jid': cur_tada_chat_jid})
        if not cur_tada_chat_jid in self.yougile_chat_dict:
            yougile_chat_members = {}
            yougile_chat_members[self.yougile_def_userID] = notif_disable
            for tada_member in tada_chat['members']:
                yougile_user_id = self.tada_cont_dict[tada_member['jid']
                                                      ]['yougile_user_id']
                if yougile_user_id:
                    yougile_chat_members[yougile_user_id] = notif_disable
            # create new yougile chat
            new_chat_res = self.yg.post_new_chat(
                yougile_chat_title, yougile_chat_members)
            yougile_chat_id = new_chat_res['id']
            # add new yougile chat into dict
            self.yougile_chat_dict[cur_tada_chat_jid] = {
                "id": yougile_chat_id,
                "title": yougile_chat_title}
            print('Added chat '+tada_chat['display_name'])
        else:
            yougile_chat_id = self.yougile_chat_dict[cur_tada_chat_jid]['id']
        return yougile_chat_id

    def _get_last_yougile_mess_num(self, yougile_chatId):
        mess_offset = 0
        mess_list = self.yg.get_messages(
            chatId=yougile_chatId, offset=mess_offset)
        while mess_list['paging']['next']:
            mess_offset = mess_offset+self.yg.message_limit
            mess_list = self.yg.get_messages(
                chatId=yougile_chatId, offset=mess_offset)
        else:
            last_mess_num = mess_offset+mess_list['paging']['count']
        return last_mess_num

    def __post_messages_to_yougile(self, tada_chat_jid, yougile_chat_id, limit, offset):
        tada_mess_list = self.td.get_messages(
            jid=tada_chat_jid, limit=limit, offset=offset)["result"]["messages"]
        for tada_mess in tada_mess_list:
            tada_sender = self.tada_cont_dict[tada_mess['from']]
            yougile_mess_text = f"[{dt.strptime(tada_mess['created'],'%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')}]{tada_sender['display_name']}({tada_sender['contact_email']if tada_sender['contact_email'] else tada_sender['contact_phone']}): {tada_mess['push_text']}"
            new_mess_res = self.yg.post_new_message(
                yougile_chat_id, yougile_mess_text, tada_mess["num"])
            print(str(new_mess_res.status_code) +
                  ':' + yougile_mess_text)  # debug

    def load_task(self, cur_tada_task_jid):
        tada_task = self.td.get_task_details(cur_tada_task_jid)["result"]
        tada_last_mess_num = tada_task["last_message"]["num"]

        cur_yougile_task_id = self.upd_yougile_task_dict(tada_task)
        yougile_last_mess_num = self._get_last_yougile_mess_num(
            cur_yougile_task_id)

        if yougile_last_mess_num != tada_last_mess_num:
            # debug
            print(
                f"Task {tada_task['display_name']} messages {yougile_last_mess_num}/{tada_last_mess_num}")
        else:
            print(f"Loaded {tada_task['display_name']}")

        self.load_all_mess(cur_tada_task_jid, tada_last_mess_num,
                           cur_yougile_task_id, yougile_last_mess_num)

    def load_chat(self, cur_tada_chat_jid):
        tada_chat = self.td.get_task_details(cur_tada_chat_jid)["result"]
        tada_last_mess_num = tada_chat["last_message"]["num"]

        cur_yougile_chat_id = self.get_yougile_chat_dict(tada_chat)
        yougile_last_mess_num = self._get_last_yougile_mess_num(
            cur_yougile_chat_id)

        if yougile_last_mess_num != tada_last_mess_num:
            # debug
            print(
                f"Task {tada_chat['display_name']} messages {yougile_last_mess_num}/{tada_last_mess_num}")
        else:
            print(f"Loaded {tada_chat['display_name']}")

        self.load_all_mess(cur_tada_chat_jid, tada_last_mess_num,
                           cur_yougile_chat_id, yougile_last_mess_num)

    def load_all_mess(self, cur_tada_jid, tada_last_mess_num, cur_yougile_id, yougile_last_mess_num):
        tada_mess_offset = tada_last_mess_num-self.td.message_limit-yougile_last_mess_num
        while tada_mess_offset > 0:
            self.__post_messages_to_yougile(
                cur_tada_jid, cur_yougile_id, self.td.message_limit, tada_mess_offset)
            tada_mess_offset = tada_mess_offset-self.td.message_limit
        else:
            self.__post_messages_to_yougile(
                cur_tada_jid, cur_yougile_id, tada_mess_offset+self.td.message_limit, 0)

    def load_all_tasks(self, tada_tasks_offset_start=0):
        tada_tasks_offset = tada_tasks_offset_start
        tada_tasks_list = self.td.get_tasks(offset=tada_tasks_offset)[
            "result"]["objects"]
        while len(tada_tasks_list) > 0:
            for tada_task_dict in tada_tasks_list:
                self.load_task(tada_task_dict["jid"])
            tada_tasks_offset = tada_tasks_offset+self.td.task_limit
            tada_tasks_list = self.td.get_tasks(offset=tada_tasks_offset)[
                "result"]["objects"]
