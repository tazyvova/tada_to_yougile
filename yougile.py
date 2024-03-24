import requests
import json
import time
from requests.compat import urljoin, quote_plus

# docs https://ru.yougile.com/api-v2#/
class yougile:

    def __init__(self, token, def_columnId):
        self.__headers = {'content-type': 'application/json',
                          'Accept-Charset': 'UTF-8', 'Authorization': token}
        self.def_columnId = def_columnId
        self.__url_base = 'https://ru.yougile.com/api-v2/'
        self.anti_ddos_timer = 3
        self.message_limit = 50
        self.task_limit = 100
        self.chat_limit = 100

    def addos(self):
        time.sleep(self.anti_ddos_timer)

    def get_token(self, login, password, companyId):
        req_url = urljoin(urljoin(self.__url_base, 'auth/'), 'keys/')
        body_dict = {'login': login,
                     'password': password, 'companyId': companyId}
        r = requests.get(url=req_url, headers=self.__headers,
                         data=json.dumps(body_dict))
        self.addos()
        return r.json()

    def get_company_id(self, login, password, company_name):
        req_url = urljoin(urljoin(self.__url_base, 'auth/'), 'companies/')
        body_dict = {'login': login,
                     'password': password, 'name': company_name}
        r = requests.post(url=req_url, headers=self.__headers,
                          data=json.dumps(body_dict))
        self.addos()
        return r.json()

    def get_users_list(self):
        req_url = urljoin(self.__url_base, 'users/')
        r = requests.get(url=req_url, headers=self.__headers)
        self.addos()
        return r.json()

    def get_tasks(self, limit=None, offset=0):
        req_url = urljoin(self.__url_base, 'tasks/')
        if limit is None:
            limit = self.task_limit
        pars = {
            'limit': limit,
            'offset': offset
        }
        r = requests.get(url=req_url, headers=self.__headers, params=pars)
        self.addos()
        return r.json()

    def get_chats(self, limit=None, offset=0):
        req_url = urljoin(self.__url_base, 'group-chats/')
        if limit is None:
            limit = self.chat_limit
        pars = {
            'limit': limit,
            'offset': offset
        }
        r = requests.get(url=req_url, headers=self.__headers, params=pars)
        self.addos()
        return r.json()

    def post_new_task(self, task_name, columnId, description):
        req_url = urljoin(self.__url_base, 'tasks/')
        body_dict = {"title": task_name,
                     "columnId": columnId, "description": description}
        r = requests.post(url=req_url, headers=self.__headers,
                          data=json.dumps(body_dict))
        self.addos()
        return r.json()

    def post_new_chat(self, title, chat_members):
        req_url = urljoin(self.__url_base, 'group-chats/')
        body_dict = {"title": title, "users": chat_members}
        r = requests.post(url=req_url, headers=self.__headers,
                          data=json.dumps(body_dict))
        self.addos()
        return r.json()

    def change_task(self, chatId, description):
        req_url = urljoin(urljoin(self.__url_base, 'tasks/'), chatId)
        body_dict = {"description": description}
        r = requests.put(url=req_url, headers=self.__headers,
                         data=json.dumps(body_dict))
        self.addos()
        return r.json()

    def get_messages(self, chatId, limit=None, offset=0):
        req_url = urljoin(
            urljoin(urljoin(self.__url_base, 'chats/'), chatId+'/'), 'messages')
        if limit is None:
            limit = self.message_limit
        pars = {
            'limit': limit,
            'offset': offset
        }
        r = requests.get(url=req_url, headers=self.__headers, params=pars)
        self.addos()
        return r.json()

    def post_new_message(self, chatId, text, label):
        req_url = urljoin(
            urljoin(urljoin(self.__url_base, 'chats/'), chatId+'/'), 'messages')
        body_dict = {
            "text": text
            #     "label": str(label)
        }
        r = requests.post(url=req_url, headers=self.__headers,
                          data=json.dumps(body_dict))
        self.addos()
        return r
