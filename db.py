from dataclasses import dataclass
from typing import Optional

@dataclass
class Chat:
    chat_id: int
    role: Optional[str]
    tone: str

    def get_chat(cur, chat_id):
        cur.execute("SELECT * FROM chats WHERE chat_id = ?", (chat_id,))
        fields = cur.fetchone()
        if fields is None:
            return None
        return Chat(*fields)
    
    def insert_chat(con, chat_id, role, tone):
        cur = con.cursor()
        if not Chat.get_chat(cur, chat_id):
            cur.execute("INSERT INTO chats(chat_id, role, tone) VALUES(?, ?, ?)", (chat_id, role, tone))
            con.commit()


    def update_role(con, chat_id, role):
        cur = con.cursor()
        cur.execute("UPDATE chats SET role = ? WHERE chat_id = ?", (role, chat_id))
        con.commit()

    def update_tone(con, chat_id, tone):
        cur = con.cursor()
        cur.execute("UPDATE chats SET tone = ? WHERE chat_id = ?", (tone, chat_id))
        con.commit()

def create_tables(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats(
        chat_id int,
        role text,
        tone text,
        PRIMARY KEY(chat_id)
    )
    """)

