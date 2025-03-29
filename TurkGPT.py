import sys
import sqlite3
import ollama
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPlainTextEdit, QPushButton, QListWidget, QHBoxLayout, QSplitter, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt

class ChatbotApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TürkChat Yardımcı Asistan")
        self.setGeometry(100, 100, 800, 500)

        self.init_db()
        
        main_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(250)
        
        self.new_chat_button = QPushButton("Yeni Sohbet")
        self.new_chat_button.clicked.connect(self.new_chat)
        left_layout.addWidget(self.new_chat_button)
        
        self.delete_chat_button = QPushButton("Eski Sohbeti Sil")
        self.delete_chat_button.clicked.connect(self.delete_chat)
        left_layout.addWidget(self.delete_chat_button)
        
        self.rename_chat_button = QPushButton("Sohbet Adını Değiştir")
        self.rename_chat_button.clicked.connect(self.rename_chat)
        left_layout.addWidget(self.rename_chat_button)
        
        self.chat_list = QListWidget()
        self.chat_list.itemClicked.connect(self.load_chat)
        left_layout.addWidget(self.chat_list)
        
        splitter.addWidget(left_panel)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(300)
        self.chat_display.setPlaceholderText("Yanıt burada görünecek...")
        right_layout.addWidget(self.chat_display)
        
        self.user_input = QPlainTextEdit()
        self.user_input.setMinimumHeight(60)
        self.user_input.setPlaceholderText("Mesajınızı buraya yazın...")
        self.user_input.setMaximumHeight(100)
        right_layout.addWidget(self.user_input)
        
        self.send_button = QPushButton("Gönder")
        self.send_button.clicked.connect(self.get_response)
        right_layout.addWidget(self.send_button)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 600])

        self.load_chats()
        self.current_chat_id = None

    def init_db(self):
        self.conn = sqlite3.connect("chatbot.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT
            )
        """)
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                sender TEXT,
                content TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats(id)
            )
        """)
        self.conn.commit()

    def load_chats(self):
        self.chat_list.clear()
        self.cursor.execute("SELECT id, title FROM chats")
        for chat_id, title in self.cursor.fetchall():
            self.chat_list.addItem(f"{chat_id}: {title}")

    def new_chat(self):
        self.cursor.execute("INSERT INTO chats (title) VALUES (?)", ("Yeni Sohbet",))
        self.conn.commit()
        self.load_chats()

    def delete_chat(self):
        if self.current_chat_id is None:
            return
        
        reply = QMessageBox.question(self, "Sohbeti Sil", "Bu sohbeti silmek istediğinizden emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.cursor.execute("DELETE FROM messages WHERE chat_id=?", (self.current_chat_id,))
            self.cursor.execute("DELETE FROM chats WHERE id=?", (self.current_chat_id,))
            self.conn.commit()
            self.load_chats()
            self.chat_display.clear()
            self.current_chat_id = None

    def rename_chat(self):
        if self.current_chat_id is None:
            return
        
        # Yeni sohbet adı girmek için input dialog gösteriyoruz
        new_title, ok = QInputDialog.getText(self, "Sohbet Adını Değiştir", "Yeni sohbet adını girin:")
        
        if ok and new_title:
            self.cursor.execute("UPDATE chats SET title=? WHERE id=?", (new_title, self.current_chat_id))
            self.conn.commit()
            self.load_chats()
        
    def load_chat(self, item):
        chat_id = int(item.text().split(": ")[0])
        self.current_chat_id = chat_id
        self.chat_display.clear()
        self.cursor.execute("SELECT sender, content FROM messages WHERE chat_id=?", (chat_id,))
        for sender, content in self.cursor.fetchall():
            self.chat_display.append(f"{sender}: {content}")

    def get_response(self):
        user_text = self.user_input.toPlainText().strip()
        if not user_text:
            return

        if self.current_chat_id is None:
            self.new_chat()
            self.cursor.execute("SELECT last_insert_rowid()")
            self.current_chat_id = self.cursor.fetchone()[0]

        user_message = f"""
    <div style='border: 1px solid gray; padding: 8px; border-radius: 5px; background-color:rgb(103, 103, 103);'>
        🧑‍💻 <b>Sen:</b> {user_text}
    </div>
    <br>
    """
        self.chat_display.append(user_message)
        self.user_input.clear()

        self.cursor.execute("INSERT INTO messages (chat_id, sender, content) VALUES (?, ?, ?)",
                            (self.current_chat_id, "Sen", user_text))
        self.conn.commit()

        messages = [
            {"role": "system", "content": "Sen Çırpan Yazılım'ın geliştirdiği yapay zeka modelisin"},
            {"role": "user", "content": user_text}
        ]

        response = ollama.chat(model="codellama:7b", messages=messages)
        bot_response = response['message']['content']

        formatted_response = ""
        in_code_block = False
        lines = bot_response.split("\n")
        
        for line in lines:
            if line.startswith("```"):
                in_code_block = not in_code_block
                if not in_code_block:
                    formatted_response += "</div><br>"
                else:
                    formatted_response += "<div style='background-color:rgb(13, 13, 13); color: #f8f8f2; padding: 10px; border-radius: 5px; font-family: monospace; white-space: pre-wrap;'>"
            else:
                formatted_response += line + "<br>" if in_code_block else line + " "
        
        bot_message = f"🤖 <b>TürkChat:</b> {formatted_response}<br>"
        self.chat_display.append(bot_message)

        self.cursor.execute("INSERT INTO messages (chat_id, sender, content) VALUES (?, ?, ?)",
                            (self.current_chat_id, "TürkChat", bot_response))
        self.conn.commit()

        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatbotApp()
    window.show()
    sys.exit(app.exec())
