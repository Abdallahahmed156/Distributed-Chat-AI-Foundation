import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from config import HOST, PORT


clients = []
names = []


class ChatServer:
    def __init__(self):
        # إعداد واجهة الـ GUI
        self.window = tk.Tk()
        self.window.title("Server Monitor - Distributed Chat")
        self.window.geometry("500x400")

        self.log_area = scrolledtext.ScrolledText(self.window, state='disabled', bg="black", fg="green")
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(self.window, text="Active Connections: 0", font=("Arial", 10, "bold"))
        self.status_label.pack(pady=5)

        # إعداد الـ Network
        self.clients = [] # قائمة الـ Sockets
        self.names = []   # قائمة الأسماء
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('0.0.0.0', 29999))
        self.server.listen()

        self.log_message("[SERVER STARTED] Listening for connections...")

        # تشغيل الـ Thread المسؤول عن قبول الاتصالات الجديدة
        accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
        accept_thread.start()

        self.window.mainloop()

    def log_message(self, message):
        """دالة لتحديث سجل الخادم بالرسائل الجديدة"""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.yview(tk.END)
        self.log_area.config(state='disabled')

    def broadcast(self, message, sender_socket):
        """إرسال الرسالة لكل المتصلين ما عدا المرسل"""
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    self.remove_client(client)

    def accept_connections(self):
        while True:
            client_socket, addr = self.server.accept()
            self.log_message(f"[NEW CONNECTION] Connected with {str(addr)}")
            
            # نطلب الاسم من العميل فور اتصاله
            client_socket.send("NAME".encode('utf-8'))
            name = client_socket.recv(1024).decode('utf-8')
            
            self.names.append(name)
            self.clients.append(client_socket)
            
            self.log_message(f"[IDENTITY] Client Name: {name}")
            self.status_label.config(text=f"Active Connections: {len(self.clients)}")
            
            # إذاعة خبر دخول شخص جديد للكل
            self.broadcast(f"{name} joined the chat!".encode('utf-8'), client_socket)
            
            # تشغيل Thread خاص لكل عميل للتعامل مع رسائله
            thread = threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True)
            thread.start()

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024)
                self.log_message(f"[MESSAGE] Received: {message.decode('utf-8')}")
                self.broadcast(message, client_socket)
            except:
                self.remove_client(client_socket)
                break

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            index = self.clients.index(client_socket)
            name = self.names[index]
            self.broadcast(f"{name} left the chat!".encode('utf-8'), client_socket)
            self.clients.remove(client_socket)
            self.names.pop(index)
            client_socket.close()
            self.log_message(f"[DISCONNECT] {name} disconnected.")
            self.status_label.config(text=f"Active Connections: {len(self.clients)}")

if __name__ == "__main__":
    ChatServer()