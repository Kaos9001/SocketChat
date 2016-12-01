import socket
import select

class Chat:
	def __init__(self,port, max_open_conns, buffer_size):
		self.port = port
		self.host = "0.0.0.0"
		self.buffer_size = buffer_size
		self.max = max_open_conns
		self.socket = self.make_socket()
		self.socklist = [self.socket]
		self.names = {}
	def make_socket(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((self.host, self.port))
		return s
	def run(self):
		print("Starting on host " + socket.gethostbyname(socket.gethostname()) + ":" + str(self.port))
		self.socket.listen(self.max)
		print("Done.")
		print("Waiting for connections...")
		while True:
			ready_read, ready_write, error = select.select(self.socklist, [], [], 0)
			for sock in ready_read:
				if sock == self.socket:
					conn, address = self.socket.accept()
					self.socklist.append(conn)
					print ("Connection from: " + address[0])
					self.broadcast(conn, "/!join")
				else:
					try:
						data = sock.recv(self.buffer_size)
						if data:
							self.broadcast(sock, data.decode("utf-8"))
						else:
							if sock in self.socklist:
								self.socklist.remove(sock)
							self.broadcast(sock, "/!offline")
					except Exception as e:
						if sock in self.socklist:
							self.socklist.remove(sock)
						self.broadcast(sock, "/!offline")
	def check_commands(self, from_sock, data):
		if data.split()[0] == "/!nick":
			print(from_sock.getpeername()[0] + " set his name as '" + " ".join(data.split()[1:]) + "'")
			self.names[from_sock.getpeername()[0]] = " ".join(data.split()[1:])
			return True
		return False
	def broadcast(self, from_sock, data):
		if self.check_commands(from_sock, data):
			return
		name = from_sock.getpeername()[0]
		if name in self.names:
			name = self.names[name]
		if data == "/!offline":
			message = name + " is offline"
		if data == "/!join":
			message = name + " joined the chat"
		else:
			message = "\r" + name + ": " + data
		print(message)
		for sock in self.socklist:
			if sock != self.socket and sock != from_sock:
				try:
					sock.send(bytes(message, "utf-8"))
				except Exception as e:
					print(e)
					sock.close()
					if sock in self.socklist:
						self.socklist.remove(sock)



chat = Chat(9001, 5, 4096)
try:
	chat.run()
except Exception as e:
	print(e)
	input()



