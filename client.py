import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog
from config import HOST, PORT

class ChatClient:
    def __init__(self):
        # 1. إعداد الـ Network
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.client.connect(('127.0.0.1', 29999))
        except Exception as e:
            print(f"Unable to connect to server: {e}")
            return
       

        # 2. إعداد واجهة الـ GUI
        self.window = tk.Tk()
        self.window.title("Distributed Messenger")
        self.window.geometry("400x500")

        # منطقة عرض الرسائل
        self.chat_area = scrolledtext.ScrolledText(self.window, state='disabled', wrap=tk.WORD)
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # منطقة الكتابة
        self.input_frame = tk.Frame(self.window)
        self.input_frame.pack(padx=10, pady=5, fill=tk.X)

        self.msg_entry = tk.Entry(self.input_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", lambda event: self.write_message()) # الإرسال بـ Enter

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.write_message)
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # 3. طلب الاسم عند البداية
        self.name = simpledialog.askstring("Name Selection", "Please enter your nickname:", parent=self.window)
        if not self.name:
            self.name = "Anonymous"

        self.display_message(f"--- Welcome to the chat, {self.name}! ---")
        # 4. تشغيل خيط الاستقبال
        self.running = True
        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def display_message(self, message):
        """إظهار الرسالة في واجهة المستخدم"""
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.yview(tk.END)
        self.chat_area.config(state='disabled')

    def receive_messages(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == "NAME":
                    self.client.send(self.name.encode('utf-8'))
                else:
                    self.display_message(message)
            except:
                self.display_message("[ERROR] Connection to server lost.")
                self.client.close()
                break

    def write_message(self):
        msg = self.msg_entry.get()
        if msg:
            full_message = f"{self.name}: {msg}"
            self.client.send(full_message.encode('utf-8'))
            # إظهار رسالتي أنا أيضاً في شاشتي
            self.display_message(f"You: {msg}")
            self.msg_entry.delete(0, tk.END)

    def on_closing(self):
        self.running = False
        self.client.close()
        self.window.destroy()

if __name__ == "__main__":
    ChatClient()