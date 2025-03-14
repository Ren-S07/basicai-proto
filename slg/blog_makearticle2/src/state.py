from langgraph.graph import MessagesState

class AgentState(MessagesState):
    #target_keyword: str
    write_word: str
    feedback: str
    remake_flag: bool

initial_state = {
    "messages": [
        ("human", "以下の情報をもとにして、顧客ペルソナへの認知を目的としたブログ記事のアウトラインを作成して。"),
    ],
    "write_word": "btob デジタル マーケティング"
}

import uuid
# スレッドIDの発行
thread_id = str(uuid.uuid4())

config = {"configurable": {
    "thread_id": thread_id,
    "siteId": "c15000000001",
    "companyId": 1,
    "productId": 1,
    "personaId": 1,
    }
}
