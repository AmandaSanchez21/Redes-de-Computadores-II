#!/usr/bin/python3
# Amanda Sánchez García

from socket import *
from threading import Thread
import ast 
import operator
import http.client
import struct
import time
import urllib.request

operators = {
	ast.Add: operator.add,
	ast.Sub: operator.sub,
	ast.Mult: operator.mul,
	ast.Div: operator.floordiv,
	ast.Mod: operator.mod
}

server = "atclab.esi.uclm.es"

TYPE = 8
CODE = 0 
CHECKSUM = 0 
ID = 0
SEQNUMBER = 88 

# Paso 0

def connect():
	sock = socket(AF_INET, SOCK_STREAM)
	sock.connect((server, 2000))
	msg = bytes()
	msg += sock.recv(1024)

	sock.close() 
	msg_decoded = msg.decode()
	print("\n", msg_decoded, "\n")

	return msg_decoded.split('\n')[0]


# Paso 1 
def step1(identifier):
	sock1 = socket(AF_INET, SOCK_DGRAM)
	sock1.bind(('', 7777))
	msg1 = identifier + ' 7777'
	msg_to_send = msg1.encode()
	sock1.sendto(msg_to_send, (server,2000))

	sock1.settimeout(4)
	msg = bytes()
	msg, client = sock1.recvfrom(1024)
	msg_received = msg.decode()
	print (msg_received)

	return msg_received.split('\n')[0]


# Paso 2

def step2(port):
	sock2 = socket (AF_INET, SOCK_STREAM)
	sock2.connect((server, int(port)))
	message = bytes()
	seguir = True

	while seguir == True:
		message = sock2.recv(1024)
		expresion = message.decode()

		if expresion[0:1]=='(' or expresion[0:1]=='[' or expresion[0:1]=='{':
			while balanceada(expresion)==False:
				expresion += sock2.recv(1024).decode()

			print (expresion)
			expresion = cambiar_a_parentesis(expresion)
			resultado = arithmeticEval(expresion)

			solucion = '(' + (str(resultado)) + ')'
			print(solucion + "\n")
			sock2.send(solucion.encode())

		else:
			seguir = False

	sock2.close()
	print("\n" + expresion)

	return expresion.split('\n')[0]


def balanceada(exp): 
	if exp.count('(')!=exp.count(')') or exp.count('[')!=exp.count(']') or exp.count('{')!=exp.count('}'):
		return False
	else: 
		return True


def arithmeticEval(s):
	node = ast.parse(s, mode='eval')

	def eval(node):
		if isinstance(node, ast.Expression):
			return eval(node.body)
		elif isinstance (node, ast.Str):
			return node.s
		elif isinstance(node, ast.Num):
			return node.n
		elif isinstance(node, ast.BinOp):
			return operators[type(node.op)](eval(node.left), eval(node.right))
		else: 
			raise TypeError(node)
	return eval(node.body)

	#Función basada en el código encontrado en: http://www.programcreek.com/python/example/7593/ast.BinOp

def cambiar_a_parentesis(exp):
	exp = exp.replace('[', '(')
	exp = exp.replace('{', '(')
	exp = exp.replace(']', ')')
	exp = exp.replace('}', ')')
	exp = exp.replace(' ', '')

	return exp


# Paso 3

def step3 (port2):
	r = http.client.HTTPConnection(server, 5000)
	r.request("GET", "/" + port2)
	step4 = r.getresponse().read().decode()
	print (step4)

	return step4.split('\n')[0]

# Paso 4

def step4 (step3):
	sock4 = socket(AF_INET, SOCK_RAW, getprotobyname("ICMP"))
	header = struct.pack("!BBHHH", TYPE, CODE, CHECKSUM, ID, SEQNUMBER) 
	timestamp = struct.pack("!d", time.time()) + step3.encode()
	checksum = cksum(header+timestamp)
	packet = struct.pack("!BBHHH", TYPE, CODE, checksum, ID, SEQNUMBER) + timestamp
	sock4.sendto(packet, (server, 80))
	print(sock4.recv(2048))
	msg = (sock4.recv(2048)[28:]).decode()
	print(msg)
	sock4.close()
	

	return msg.split('\n')[0]

#Function got from: #https://bitbucket.org/arco_group/python-net/src/tip/raw/icmp_checksum.py
def cksum(data):

	def sum16(data):
		if len(data) % 2:
			data += '\0'.encode()

		return sum(struct.unpack("!%sH" % (len(data) // 2), data))

	retval = sum16(data)
	retval = sum16(struct.pack('!L', retval))
	retval = (retval & 0xFFFF) ^ 0xFFFF

	return retval

# Paso 5

def step5(port4):
	sock5 = socket(AF_INET, SOCK_STREAM)
	sock5.connect((server, 9000))
	_message = port4  + " " + str(48500)
	sock5.send(_message.encode())

	proxy = socket(AF_INET, SOCK_STREAM)
	proxy.bind(('', 48500))
	proxy.listen(35)
	Thread(target = thread, args = (proxy,)).start()
	
	msg = sock5.recv(1024)
	print(msg.decode())
	sock5.close()

def thread(proxy):

	while True:
		sockClient, address = proxy.accept()
		Thread(target = _http, args = (sockClient,)).start()
		
		
def _http(sockClient):

	msg = sockClient.recv(1024)
	msg2 = msg.split()
	url_needed = msg2[1].decode()

	download = urllib.request.urlopen(url_needed)
	download = download.read()
	sockClient.send(download)
	sockClient.close()




def main():
	id = connect()
	port = step1(id)
	port2 = step2(port)
	port3 = step3(port2)
	port4 = step4(port3)
	step5(port4)


main() 
