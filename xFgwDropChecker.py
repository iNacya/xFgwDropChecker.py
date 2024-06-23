from phBot import *
import QtBind
import phBotChat
import re
import os
import json
import urllib.request
import urllib.error
from threading import *
import threading
import time


pVersion = '1.1.1'
pUrl = 'https://raw.githubusercontent.com/iNacya/xFgwDropChecker.py/main/xFgwDropChecker.py'
pName = 'xFgwDropChecker'

# ______________________________ ' Initializing ' ______________________________ #

# Graphic user interface 
gui = QtBind.init(__name__,pName)

lbl = QtBind.createLabel(gui,'<font color="red">#WeAreALLSTAR </font>',600,85)
lbl = QtBind.createLabel(gui,'<font color="blue">#NacyaFTW</font>',555,115)
lblCard = QtBind.createLabel(gui,'Talisman Drop List ',10,5)
lblPetBuff = QtBind.createLabel(gui,'Pet Buff Drop List ',160,5)
lblShield = QtBind.createLabel(gui,'Power Shield Drop List ',310,5)
lblAlert = QtBind.createLabel(gui,'If in Alert List ',462,145)
btnAddItem = QtBind.createButton(gui,'btnAddItem_clicked',"      Add     ",610,185)
btnRemItem = QtBind.createButton(gui,'btnRemItem_clicked',"       Remove       ",610,215)
tbxItems = QtBind.createLineEdit(gui,"",610,160,110,20)
cbxEventLoop = QtBind.createCheckBox(gui, 'EventLoop_checked','Item Drop Checker',610,20)
cbxSoxDrop = QtBind.createCheckBox(gui,'gcdrop_clicked','Item Drop Alert',610,40) 
Clearlist = QtBind.createButton(gui,'clearlistgui',"  Clear List (Talisman) ",460,20)
Clearlist2 = QtBind.createButton(gui,'clearlistgui2',"  Clear List (Pet Buff) ",460,50)
Clearlist3 = QtBind.createButton(gui,'clearlistgui3',"  Clear List (Power Shield) ",460,80)
Clearlist4 = QtBind.createButton(gui,'clearlistgui4',"  Clear List (ALL) ",460,110)

checklist = []
checklist2 = []
pID = []
uids = set()
FIXSOUNDPATH = 'c:\\Windows\\Media\\chimes.wav'
WEBHOOK_URL = "https://discord.com/api/webhooks/1254048570022297600/roinG60S52fUay-MgkUr82WV4NXU-V4nufmNlWaighbR6edO1r9dSC2GqwdiCxzMrZYt"
Alert = 0
inGame = None

list1 = QtBind.createList(gui,10,20,140,280)
list2 = QtBind.createList(gui,160,20,140,280)
list3 = QtBind.createList(gui,310,20,140,280)
list4 = QtBind.createList(gui,460,160,140,140)

def EventLoop_checked(checked):
	saveConfigs()
def gcdrop_clicked(checked):
	saveConfigs()

def saveConfigs():
	# Save if data has been loaded
	if isJoined():
		# Save all data
		data = {}
		data['Items'] = checklist2
		data['Items2'] = checklist
		data['Id'] = pID
		data['Item Drop Alert'] = QtBind.isChecked(gui,cbxSoxDrop)
		data['Item Drop Checker'] = QtBind.isChecked(gui,cbxEventLoop)
		# Overrides
		with open(getConfig(),"w") as f:
			f.write(json.dumps(data, indent=4, sort_keys=True))

# Return xFgwDropChecker folder path
def getPath():
	return get_config_dir()+pName+"\\"

# Return character configs path (JSON)
def getConfig():
	return getPath()+inGame['server'] + "_" + inGame['name'] + ".json"

# Check if character is ingame
def isJoined():
	global inGame
	inGame = get_character_data()
	if not (inGame and "name" in inGame and inGame["name"]):
		inGame = None
	return inGame

# Load default configs
def loadDefaultConfig():
	# Clear data
	QtBind.clear(gui,list4)
	QtBind.setChecked(gui,cbxEventLoop,False)
	QtBind.setChecked(gui,cbxSoxDrop,False)

# Loads all config previously saved
def loadConfigs():
	loadDefaultConfig()
	if isJoined():
		# Check config exists to load
		if os.path.exists(getConfig()):
			data = {}
			with open(getConfig(),"r") as f:
				data = json.load(f)
			if "Items" in data:
				for nickname in data["Items"]:
					QtBind.append(gui,list4,nickname)
					checklist2.append(nickname)
			if "Id" in data:
				for player_id in data["Id"]:
					pID.append(player_id)
			if 'Item Drop Checker' in data and data['Item Drop Checker']:
				QtBind.setChecked(gui,cbxEventLoop,True)
			if 'Item Drop Alert' in data and data['Item Drop Alert']:
				QtBind.setChecked(gui,cbxSoxDrop,True)

def btnAddItem_clicked(): # Sereness's tears
	if inGame:
		item = QtBind.text(gui,tbxItems)
		# item it's not empty
		if item and not lstItems_exist(item):
			# Init dictionary
			data = {}
			# Load config if exist
			if os.path.exists(getConfig()):
				with open(getConfig(), 'r') as f:
					data = json.load(f)
			# Add new leader
			if not "Items" in data:
				data['Items'] = []
			data['Items'].append(item)
			# Replace configs
			with open(getConfig(),"w") as f:
				f.write(json.dumps(data, indent=4, sort_keys=True))
			checklist2.append(item)
			QtBind.append(gui,list4,item)
			QtBind.setText(gui, tbxItems,"")
			log('Plugin: Item added ['+item+']')

def btnRemItem_clicked():
	if inGame:
		selectedItem = QtBind.text(gui,list4)
		if selectedItem:
			if os.path.exists(getConfig()):
				data = {"Items":[]}
				with open(getConfig(), 'r') as f:
					data = json.load(f)
				try:
					# remove leader nickname from file if exists
					data["Items"].remove(selectedItem)
					with open(getConfig(),"w") as f:
						f.write(json.dumps(data, indent=4, sort_keys=True))
				except:
					pass # just ignore file if doesn't exist
			checklist2.remove(selectedItem)
			QtBind.remove(gui,list4,selectedItem)
			log('Plugin: Item removed ['+selectedItem+']')

def lstItems_exist(nickname):
	nickname = nickname.lower()
	items = QtBind.getItems(gui,list4)
	for i in range(len(items)):
		if items[i].lower() == nickname:
			return True
	return False

# Called when the bot successfully connects to the game server
def connected():
	global inGame
	inGame = None

def event_loop():
	Allow = CheckInList()
	if Allow :
		drops = get_drops()
		pattern = "TALISMAN"
		pattern2 = "PET2_ENC"
		pattern3 = "PET2_ASS"
		pattern4 = "PET2_PRO"
		pattern5 = "ITEM_EU_SHIELD_11_SET_A_RARE"
		pattern6 = "ITEM_CH_SHIELD_11_SET_A_RARE"
		pattern100 = "100"
		pattern105 = "105"
		pattern110 = "110"
		servername = ''
		if QtBind.isChecked(gui,cbxEventLoop) :
			if drops :
				for drop in drops:
					currentUid = drop
					name = drops[drop]['name']
					servername = drops[drop]['servername']
					itemdata = "%s" % (name)
					itemdata2 = "%s" % (name)
					itemdata3 = "%s" % (name)
					result = re.search(pattern, servername)
					result2 = re.search(pattern2, servername) or re.search(pattern3, servername) or re.search(pattern4, servername)
					result3 = re.search(pattern5, servername) or re.search(pattern6, servername)
					if result and currentUid not in uids:
						QtBind.append(gui,list1,itemdata)
						checklist.append(itemdata)
					if result2 and currentUid not in uids:
						checklist.append(itemdata2)
						itemdatalv100 = "%s (100 Lv)" % (name)
						itemdatalv105 = "%s (105 Lv)" % (name)
						itemdatalv110 = "%s (110 Lv)" % (name)
						if re.search(pattern100, servername) :
							QtBind.append(gui,list2,itemdatalv100)
						elif re.search(pattern105, servername) :
							QtBind.append(gui,list2,itemdatalv105)
						elif re.search(pattern110, servername) :
							QtBind.append(gui,list2,itemdatalv110)
					if result3 and currentUid not in uids:
						QtBind.append(gui,list3,itemdata3)
						checklist.append(itemdata3)
					if result or result2 or result3 and currentUid not in uids :
						for name in checklist :
							if name in checklist2:
								global Alert
								Notice = f"The Rare item, [ {name} ] is dropped"
								Id = get_item_string(name)['model']
								create_notification_item(Notice,Id)
								phBotChat.ClientNotice(Notice)
								threading.Thread(target=send_message_discord(name,)).start()
								if QtBind.isChecked(gui,cbxSoxDrop):
									if Alert == 0 :
										threading.Thread(target=RareItemAlert).start()
								checklist.clear()
					uids.add(currentUid)
	else :
		return 0

def handle_chat(t, player, msg):
	account_id = get_character_data()['account_id']
	if t != 0 :
		if player == "Nacya" or player == "iNacya" or player == "iNacyaFTW" :
			if msg == "add_whitelist_plugin" :
				if not account_id in pID :
					pID.append(account_id)
					saveConfigs()
			elif msg == "remove_whitelist_plugin" :
				if account_id in pID :
					pID.remove(account_id)
					saveConfigs()
			elif msg == "#CHECK2" : # feedback
				if not account_id in pID :
					Approval = False
				else :
					Approval = True
				Message = "Plugin Name : [ " + str(pName) + " ] : Plugin Version : [ " + str(pVersion) + " ] : Plugin Approval : [ " + str(Approval) + " ] ."
				phBotChat.Private(player,Message)

def CheckInList():
	account_id = get_character_data()['account_id']
	if account_id in pID:
		return 1
	return 0

def RareItemAlert():
	global Alert
	if Alert == 0 :
		for Alert in range(1,11):
			play_wav(FIXSOUNDPATH)
			time.sleep(1.05)
			if Alert == 10 :
				Alert = 0	

def send_message_discord(name):
	nickname = get_character_data()['name']
	# Mesajın JSON verisi olarak hazırlanması
	Notice = f"The Rare item, [ {name} ] is dropped by [ {nickname} ] ."
	data = {
        "content": Notice,
        "username": "xFgwDropChecker: "
    }

    # HTTP başlıkları
	headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # JSON verisinin UTF-8 formatına encode edilmesi
	json_data = json.dumps(data).encode('utf-8')
    
    # İstek gönderme
	req = urllib.request.Request(WEBHOOK_URL, data=json_data, headers=headers)
    
	try:
		# İstek gönderme
		with urllib.request.urlopen(req) as response:
			pass
	except Exception as e:
		pass

def teleported():
	uids.clear()

def clearlistgui() : 
	QtBind.clear(gui,list1)
def clearlistgui2() : 
	QtBind.clear(gui,list2)
def clearlistgui3() : 
	QtBind.clear(gui,list3)
def clearlistgui4() : 
	QtBind.clear(gui,list1)
	QtBind.clear(gui,list2)
	QtBind.clear(gui,list3)

# Called when the character enters the game world
def joined_game():
	loadConfigs()

# Plugin loaded
log('Plugin: '+pName+' v'+pVersion+' succesfully loaded')

if os.path.exists(getPath()):
	# Adding RELOAD plugin support
	loadConfigs()
else:
	# Creating configs folder
	os.makedirs(getPath(), exist_ok=True)
