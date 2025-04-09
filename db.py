import sqlite3
from datetime import datetime


def init_db():
    connect = sqlite3.connect("./database/chat.db")

    # 对话表
    connect.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # 消息表
    connect.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conv_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(convo_id) REFERENCES conversations(id)
        )
        """
    )

    connect.commit()
    connect.close()


if __name__ == "__main__":
    init_db()
