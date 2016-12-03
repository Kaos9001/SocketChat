import socket
import select
import threading
import sys

class Client:
	def __init__(self, timeout, buffer_size):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.settimeout(timeout)
		self.buffer_size = buffer_size
	def get_input(self):
		self.user_input[0] = input(self.name + ": ")
		self.user_input[1] = True
	def connect(self, host, port):
		self.socket.connect((host,port))
		self.name =  input("Select a nickname: ")
		name = bytes("NICK " + socket.gethostbyname(socket.gethostname()) + " " + self.name, "utf-8")
		self.socket.send(name)
		self.user_input = [None, False]
		t = threading.Thread(target=self.get_input)
		t.start()
		while 1:
			socket_list = [self.socket]
			ready_read, ready_write, error = select.select(socket_list, [], [], 0)
			for sock in ready_read:
				if sock == self.socket:
					try:
						data = self.socket.recv(self.buffer_size)
						if not data:
							sock.close()
							input("Disconnected. Press enter to quit.")
							sys.exit()
						else:
							print(data.decode("utf-8"))
					except Exception as e:
						print(e)
						sock.close()
						input("Disconnected. Press enter to quit.")
						sys.exit()
			if self.user_input[1]:
				data = self.user_input[0]
				self.socket.send(bytes(data, "utf-8"))
				self.user_input[1] = 0
				t = threading.Thread(target=self.get_input)
				t.start()

bob = Client(2, 4096)
try:
	bob.connect("localhost", 9001)
except Exception as e:
	print(e)
	input()