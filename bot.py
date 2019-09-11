#! /usr/bin/env python
import config
import socket
import re
from datetime import datetime


def socket_connect(host, port):
	s = socket.socket()
	s.connect((host, port))
	return s


def twitch_connect(username, pw, channel):
	s.send("PASS {}\r\n".format(pw).encode("utf-8"))
	s.send("NICK {}\r\n".format(username).encode("utf-8"))
	s.send("JOIN {}\r\n".format(channel).encode("utf-8"))
	

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
	
	
def _message_formatter(timestamp, username, msg):
	max_msg_len = 49
	max_usr_len = 25
	max_timestamp_len = 19
	formatted = ""
	joiner = "|\n|" + " " * max_timestamp_len + "|" +" " * max_usr_len + "|"
	row_len = 0
	for i, letter in enumerate(msg):
		if i % max_msg_len == 0 and i != 0:
			formatted += joiner + letter
			row_len = 1
		else:
			formatted += letter
			row_len += 1
	if row_len <= max_msg_len:
		formatted += " " * max(max_msg_len - row_len, 0) + "|"
	padding = " " * max((max_usr_len - len(username)), 0)
	date_user_part = "|{}|{}{}|".format(
		timestamp.strftime("%Y-%m-%d %H:%M:%S"),
		username, 
		padding
	)
	row = "\n|{}|{}|{}|".format(
		"-" * max_timestamp_len, 
		"-" * max_usr_len, 
		"-" * max_msg_len
	)
	message = date_user_part + formatted + row
	return message


class ChatMessage:
	def __init__(self, raw):
		msg_regex = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
		self.raw = raw
		self.message = msg_regex.sub("", raw).rstrip()
		self.username = re.search(r"\w+", raw).group(0)
		self.timestamp = datetime.utcnow()
	
	def __repr__(self):
		return "{}:  {}".format(self.username, self.message)
		
	def print_formatted(self):
		print(_message_formatter(self.timestamp, self.username, self.message))


if __name__ == "__main__":
	channel = "#" + input("Enter the name of the channel to join: ")
	
	print("Connecting to Twitch chat...")
	s = socket_connect(config.host, config.port)
	
	print("Connection successful! Authenticating...")
	twitch_connect(config.username, config.password, channel)
	print("Authenticated!\nListening to socket stream...\n")
	message_counter = 0
	while True:
		raw_response = s.recv(2048).decode("utf-8", "ignore")
		if raw_response == "PING :tmi.twitch.tv\r\n":
			print(raw_response)
			s.send(("PONG :tmi.twitch.tv\r\n").encode("utf-8")) 
		else:
			message_counter += 1
			try:
				ChatMessage(raw_response).print_formatted()
			except Exception as e:
				print(e)
				print(raw_response)
				print("\n\n\n\n")
