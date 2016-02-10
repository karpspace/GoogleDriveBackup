#!/usr/bin/python


#Imports 
from random import randint
from peewee import *
from datetime import *
import time
import os
import re
import subprocess

db = SqliteDatabase('backup.db') # db file
allBackups = []
server = "" #server name
actualDate = time.strftime("%d_%m_%Y")

mainBackupFolder = "" #google.drive folder id 


class backupEntry(Model):
	date = DateField()
	folderId = CharField()

	class Meta:
		database = db

class backupMe(object):
	
	def __init__(self):
		self.backupId = ""
		self.foldersToBackup = [
			#example ("nameOfSubdirectory","path","doesItNeedCompression")
			("Documents","~/Documents",True)
		]

	def getBackupEndId(self):
		for backup in backupEntry.select().order_by(backupEntry.date.desc()):
			allBackups.append([str(backup.date),backup.folderId]) 
		
		allBackups.sort(key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'))
		if len(allBackups) >= 8:
			return allBackups[-8]
		else:
			return False


	def getBackupDates(self):
		for backup in backupEntry.select().order_by(backupEntry.date.desc()):
			print str(backup.date) + " " + backup.folderId

	def createFolder(self,name,path,parent,needsCompress):
		idFold = os.popen("drive folder -t " + name + " -p " + parent + " | grep Id:").read()
		match = re.findall(r'[a-zA-z0-9]{25,}', str(idFold))
		if needsCompress:
			folders = os.listdir(path)
			for f in folders:
				os.popen("tar -zcvf "+ path +"/"+ f +".gz "+ path +"/"+f).read()
				os.popen("drive upload -f " + path +"/"+ f +".gz " + " -p " + match[0]).read()
				os.popen("rm -f " + path +"/"+ f +".gz ")
				print("rm -f " + path +"/"+ f +".gz ")
		else:
			os.popen("drive upload -f " + path  + " -p " + match[0]).read()
		return match[0]

	def printFolders(self):
		return True

	def createFolderStructure(self):
		idFold = os.popen("drive folder -t " + server + "_" +actualDate+" -p " + mainBackupFolder + " | grep Id:").read()
		mainFolder = re.findall(r'[a-zA-z0-9]{25,}', str(idFold))
		mainFolderId = mainFolder[0]
		for folder in self.foldersToBackup:
			self.createFolder(folder[0],folder[1],mainFolderId,folder[2])
		self.addBackupDate(time.strftime("%Y-%m-%d"), mainFolderId)
		lastUpdate = self.getBackupEndId()
		if not lastUpdate:
			print "No dates"
		else:
			backup = self.getBackupEndId()
			backupId = backup[1]
			self.removeBackup(backupId)
	
	def addBackupDate(self, date, folderId):
		backupNew = backupEntry(date=date, folderId = folderId)	
		backupNew.save()

	def removeBackup(self, idBack):
		idFold = os.popen("drive delete -i "+ idBack).read()
		print "Id to be removed " + idBack
		print "Removed"

bckMe = backupMe()
bckMe.createFolderStructure()
bckMe.getBackupEndId()

