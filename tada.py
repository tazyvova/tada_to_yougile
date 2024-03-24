import requests
import time
from requests.compat import urljoin, quote_plus

# docs https://tada-team.github.io/tdproto-docs-ru/basics.html
class tada:

    def __init__(self, token, id_team):
        self.__headers = {'content-type': 'application/json',
                          'Accept-Charset': 'UTF-8', 'token': token}
        self.id_team = id_team
        self.__url_base = 'https://web.tada.team/api/v4/teams/'
        self.anti_ddos_timer = 3
        self.message_limit = 10
        self.task_limit = 10

    def addos(self):
        time.sleep(self.anti_ddos_timer)

    def get_contacts(self):
        req_url = urljoin(
            urljoin(self.__url_base, self.id_team+'/'), 'contacts/')
        r = requests.get(url=req_url, headers=self.__headers)
        self.addos()
        return r.json()

    def get_tasks(self, limit=None, offset=0):
        req_url = urljoin(urljoin(self.__url_base, self.id_team+'/'), 'tasks/')
        if limit is None:
            limit = self.task_limit
        pars = {
            'short': True,
            'limit': limit,
            'offset': offset
        }
        r = requests.get(url=req_url, headers=self.__headers, params=pars)
        self.addos()
        return r.json()

    def get_task_details(self, task_jid):
        req_url = urljoin(
            urljoin(urljoin(self.__url_base, self.id_team+'/'), 'chats/'), task_jid)
        r = requests.get(url=req_url, headers=self.__headers)
        self.addos()
        return r.json()

    def get_chat_details(self, chat_jid):
        req_url = urljoin(
            urljoin(urljoin(self.__url_base, self.id_team+'/'), 'chats/'), chat_jid)
        r = requests.get(url=req_url, headers=self.__headers)
        self.addos()
        return r.json()

    def get_messages(self, jid, limit=None, offset=0):
        req_url = urljoin(urljoin(urljoin(
            urljoin(self.__url_base, self.id_team+'/'), 'chats/'), jid+'/'), 'messages/')
        if limit is None:
            limit = self.message_limit
        pars = {
            'limit': limit,
            'offset': offset
        }
        r = requests.get(url=req_url, headers=self.__headers, params=pars)
        self.addos()
        return r.json()
