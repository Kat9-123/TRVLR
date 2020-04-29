from time import time

start_time = time()

from time import sleep
from random import randint
from ctypes import windll
windll.user32.SetProcessDPIAware()

from threading import Thread

from pynput.keyboard import Key, Listener

from tkinter import Tk, Label, StringVar
import tkinter.font as tkFont

from binascii import b2a_base64
from hashlib import sha256
from cryptography.fernet import Fernet

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP

from imaplib import IMAP4_SSL
from email import message_from_bytes



print("Importing took:", time() - start_time, "Seconds")



# ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789
random_string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
rand_list = []

height = 48
width = 174


bgtext = ""
fgtext = ""


keytext = ""

keylong = 0

write = False

login = False

exitapp = False



for i in range(height):
	v = ""
	for a in range(width):
	    v += random_string[randint(0, len(random_string) - 1)] # Comment this for no background
	    #v += " " # Uncomment this for no background
	rand_list.append(v)






def UIUpdate():
	global bgtext, fgtext, keylong, exitapp
	bglist = list(bgtext)

	for i in range(len(fgtext)):
		for x in range(len(fgtext[i])):
			bglist[((x + 2884 - keylong // 2) + (width + 1) * i)] = fgtext[i][x]

	text = "".join(bglist)

	Var_Text.set(text)

	if exitapp == True:
		root.destroy()
		exit()
	root.after(1, UIUpdate)

def BGUpdate():
	global bgtext, exitapp
	bgtext = ""
	for o in range(len(rand_list)):
		temp = [rand_list[o][(i - 1) % len(rand_list[o])] for i, x in enumerate(rand_list[o])]
		bgtext += "".join(temp) + "\n"
		rand_list[o] = temp
	sleep(1)
	if exitapp == True:
		exit()
	BGUpdate()


def FGUpdate():
	global keytext

	def on_press(key):
		global keytext, write, exitapp, login
		global server_name, server_password, enc_key
		k = str(key).replace("'", "")

		if k == "Key.backspace":
			if login == False and len(keytext) > 16 or login == True:

				if keytext[-1:] == "\n":
					keytext = keytext[:-1]
				keytext = keytext[:-1] # REMOVE CHAR
		if k == "Key.space":
			k = " "
		if k == "[`]" or k == "`":
			if login == True:
				write = not write
				if write == True:
					edit_key(Get())
				else:
					keytext = ""
			k = "" # READ MSG

		if k == "\\\\":
			k = "\\"

		if k == "[^]":
			k = "^"

		if k == "Key.delete": # REMOVE ALL TEXT
			keytext = ""

		if k == "Key.enter": # ADD LINE
			k = "\r\n"


		if k == "Key.ctrl_l":
			if keytext != "" and login == True:	
				print("send")
				Send(keytext)
				edit_key("-= MESSAGE SENT =-")
				write = True
			if login == False:
				listkey = keytext.split("\r\n")
				keytext = ""
				print(listkey)
				server_name = listkey[2].lower() + ".@gmail.com"
				server_password = listkey[3].lower()
				enc_key = b2a_base64(bytes.fromhex(sha256(listkey[4].lower().encode()).hexdigest())).decode()[:-1]
				print(server_name, server_password, enc_key)
				edit_key("-= LOGGED IN =-")
				write = True
				login = True # SEND



		if k == "Key.esc":
			print("exit")

			exitapp = True
			exit() # EXIT

		if "Key" in k:
			k = ""


		k = k.upper()
		# keytext[:-1] + k + "_"
		keytext += k 
		if write == False:
			edit_key(keytext)

	def edit_key(text):
		global fgtext, keylong

		if text != "":
			keylist = text.split("\r\n")

			keylong = 0
			for i in keylist:
				if len(i) > keylong:
					keylong = len(i)

			keylist.insert(0, "")
			keylist.append("")
			for i in range(len(keylist)):
				space = ""
				for x in range((keylong - len(keylist[i])) + 3):
					space += " "
				keylist[i] = "   " + keylist[i] + space

			fgtext = keylist
			return keylist
		else:
			fgtext = ""

	def start_listener():
		try:
			with Listener(on_press=on_press) as listener:
				listener.join()
		except Exception as e:
			pass
		if exitapp == False:
			start_listener()

	keytext = "-= LOG IN =-\r\n\r\n"
	edit_key(keytext)
	start_listener()






def Send(message):

	box = IMAP4_SSL("imap.gmail.com")
	box.login(server_name, server_password)
	box.select('Inbox')
	typ, data = box.search(None, 'ALL')
	id_list = data[0].split() 


	box.store(id_list[-1], '+FLAGS', '\\Deleted')
	box.expunge()


	msg = MIMEMultipart()
	msg['From'] = server_name
	msg['To'] = server_name
	msg['Subject'] = 'MSG'
	msg.attach(MIMEText(Fernet(enc_key).encrypt(message.encode()).decode()[8:], 'plain'))
	server = SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(server_name, server_password)
	text = msg.as_string()
	server.sendmail(server_name, server_name, text)
	server.quit()

def Get():
	def get_body(msg):
		if msg.is_multipart():
			return get_body(msg.get_payload(0))
		else:
			return msg.get_payload(None,True)
	prev_MSG = ""



	mail = IMAP4_SSL("imap.gmail.com")
	mail.login(server_name,server_password)
	mail.select('inbox')
	type, data = mail.search(None, 'ALL') 

	id_list = data[0].split()   
	typ, data = mail.fetch(id_list[-1], '(RFC822)' )



	raw = message_from_bytes(data[0][1])
	#Date = raw["Date"].upper()
	cur_MSG = get_body(raw).decode() 

	if prev_MSG != cur_MSG:
		prev_MSG = cur_MSG
		print(cur_MSG)
		#return "RECEIVED ON \r\n" + Date +":\r\n\r\n" + Fernet(enc_key).decrypt(("gAAAAABe" + cur_MSG).encode()).decode()
		return "RECEIVED:\r\n\r\n" + Fernet(enc_key).decrypt(("gAAAAABe" + cur_MSG).encode()).decode()



bgThread = Thread(target=BGUpdate)
bgThread.start()
fgThread = Thread(target=FGUpdate)
fgThread.start()


root = Tk()


root.configure(bg="#0c0c0c")
root.attributes("-fullscreen", True)
root.config(cursor='none')

fontStyle = tkFont.Font(family="Consolas", size=10)

Var_Text = StringVar()



mainLabel = Label(textvariable=Var_Text, bg="#0c0c0c", fg="#ff8000", font=fontStyle)
mainLabel.pack()


UIUpdate()
root.mainloop()
