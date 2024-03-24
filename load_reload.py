from chat_import import from_tada_to_yougile
from debugvalues import debug

oper = from_tada_to_yougile(
    tada_token=debug.tada_token,                        #tadabot token
    tada_id_team=debug.tada_id_team,                    #team token
    yougile_token=debug.yougile_token,                  #yougile auth token
    yougile_def_columnId=debug.yougile_def_columnId,    #yougile target column
    yougile_def_userID=debug.yougile_def_userID,        #yougile chat can't be empty
    prepare_tasks=0,
    prepare_chats=1
)
oper.load_all_tasks
oper.load_chat
oper.load_task