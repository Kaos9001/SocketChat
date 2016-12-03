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
					print ("Connection from: " + address[0]) # Add login warning
				else:
					try:
						data = sock.recv(self.buffer_size)
						if data:
							self.parse(data, sender=sock)
						else:
							if sock in self.socklist:
								self.socklist.remove(sock) # Add offline
								print(sock.getpeername() + " is offline")
					except Exception as e:
						print(e)
						if sock in self.socklist:
							self.socklist.remove(sock)
							print(sock.getpeername() + " is offline")
	def parse(self, data, sender=None):
		commands = data.decode("utf-8").split()
		try:
			if commands[0] == "QUIT":
				for sock in self.socklist:
					sock.close()
				sys.exit()
			elif commands[0] == "KICK":
				for sock in self.socklist:
					if sock.getpeername()[0] == "".join(commands[1:]) or self.names[sock.getpeername()[0]] == "".join(commands[1:]):
						sock.close()
						break
				else:
					if sender != None:
						sender.send(bytes("".join(commands[1:]) + " is not connected.", "utf-8"))
			elif commands[0] == "NICK":
				self.names[commands[1]] = " ".join(commands[2:])
			elif commands[0] == "MESSAGE":
				for sock in self.socklist:
					if sock.getpeername()[0] == commands[1] or self.names[sock.getpeername()[0]] == commands[1]:
						sock.send(bytes("".join(commands[2:]), "utf-8"))
						break
			elif commands[0] == "RAW":
				self.broadcast(None, " ".join(commands[1:]))
			else:
				name = sender.getpeername()[0]
				if name in self.names:
					name = self.names[name]
				message = "\r" + name + ": " + " ".join(commands)
				self.broadcast(sender, message)
		except Exception as e:
			sender.send(bytes(str(e), "utf-8"))
	def broadcast(self, from_sock, message):
		print(message)
		for sock in self.socklist:
			if sock != self.socket and sock != from_sock:
				try:
					sock.send(bytes(message, "utf-8"))
				except Exception as e:
					print(e)
					print(2)
					sock.close()
					if sock in self.socklist:
						self.socklist.remove(sock)



chat = Chat(9001, 5, 4096)
try:
	chat.run()
except Exception as e:
	print(e)
	input()



