'''

    Udp File transfer is simple project to show how file is transfer using Udp socket
                       Copyright (C) 2018 Rahul Dangi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''



import socket as sk
from socket import *
import os
import sys
import hashlib
import time

SERVER_NAME = "INS"

'''
Ask for server ip to send data to server through UDP
'''
os.system('cls' if os.name == 'nt' else 'clear')
print("starting application.....\n")
time.sleep(1)
print()
print("\t\tWelcome to the UDP File Transfer Client...")
time.sleep(0.2)
print('''
                              UDP/1.0
            copyrights 2018 reserved by Som Durgesh Gupta''')
time.sleep(0.1)
print('''
    This server is designed by Rahul Dangi from JK Lakshmipat University,
    Jaipur.

            Project Name: UDP File transfer system
''')
time.sleep(0.9)
print()
serverIp = None
def getserverIp():
    "ask for server ip to enter"
    print("==========================ENTER SERVER-IP==========================")
    time.sleep(0.5)
    print("\t Enter ip of server - you want to connect\n",
          "\t IP must be valid ip\n")
    time.sleep(0.5)
    global serverIp
    serverIp = input("Udp server-ip> ")
getserverIp()

# Variables used for UDP transfer
host = "" # For client ip
clientPort = 10001 # client bind port
serverAddr = None
buffer = 1024 # Buffer size of client
data = "" # Data from server
filePath = os.getcwd()+ "\\ClientFiles" # Path where files are stored
saveToFile = "" # filename from server to save
COUNTER = 0 #no of times file retried to download
SENDFILE = "" #send file from server

#list of all commands
LIST = "LIST" # Request for list of files
FILE = "FILE" # Request for file to send
NACK = "NACK" # Positive acknowledge regarding file transfer
PACK =  "PACK" # Negatie acnowledge regarding file transfer
CHECK = "CHECK" # Receive checksum from server

#Getting ip of server
host = sk.gethostbyname(sk.gethostname())

#Create server socket
clientSocket = None
def initSocket():
    "Initialize client socket for connecting to server"
    print("Initializing server socket...")
    global clientSocket
    global serverAddr
    global serverIp
    serverAddr = (serverIp,10000)
    clientSocket = None #if second attempts come
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind((host,clientPort))
initSocket()

#checking for client directory and creating it if not exist
if not os.path.exists(filePath):
    os.mkdir(filePath) #creating if not exists

def requestList():
    'Request list of files from the server'
    print("Sending request to server for list of files....")
    try:
        clientSocket.sendto("LIST".encode("utf-8"), serverAddr)
    except Exception:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\tConnection failed to server...")
        print("\tMaybe ip is wrong...")
        print("\tOr maybe server is closed now...")
        print()
        clientSocket.close() #closing socket first
        getserverIp() #asking to enter ip again
        initSocket() #configure socket again
        return
    print("list of files request has been sent to server.")
    listenForList() #listen for list of files from server
    return

def listenForList():
    'Wait for list of files by server on request by client'
    print("Waiting for server to send list of files...")
    global serverAddr
    data, serverAddr = clientSocket.recvfrom(buffer)
    time.sleep(0.5)
    print("List of files is received...")
    os.system('cls' if os.name == 'nt' else 'clear')
    allFiles = data.decode("utf-8").strip() # converting data into string of files
    filesList = list(allFiles.split("\t"))
    time.sleep(0.5)
    print("\n\n*******************FILES AVAILABLE ON SERVER************************\n")
    count = 0
    for item in filesList:
        time.sleep(0.1)
        if item.strip() != "":
            count += 1
            print("\t\t",count,". -> ", item, "\n")
    if count == 0:
        print("\t\tNO FILES AVAILABLE")
        return
    time.sleep(0.5)
    print("==========================ENTER FILENAME==========================")
    print("\t filename to download the file.\n",
          "\t Enter name of the file from above list of files...\n")
    time.sleep(0.5)
    sendFile = input("Udp > ")
    global SENDFILE
    SENDFILE = sendFile #for later acknowledge
    saveToFile = filePath+os.sep+sendFile.split('/')[-1]
    print("Sending file name to server....")
    sendFile = "FILE "+ sendFile
    clientSocket.sendto(sendFile.encode("utf-8"), serverAddr)

    # goto listen for file
    listenForFile(saveToFile)
    return

def listenForFile(fileName):
    'Wait for file to download and download file from server'
    os.system('cls' if os.name == 'nt' else 'clear')
    fileName = fileName.replace('/','\\')
    print("Waiting for downloading the file...")
    global serverAddr
    data = None
    try:
        global clientSocket
        global serverAddr
        clientSocket.settimeout(2)
        data, serverAddr = clientSocket.recvfrom(buffer)
    except timeout:
        print("Server Busy.")
        print("Server time out...Please try after some time...")
        print("File downloading failed...")
        return
    response = data.decode("utf-8")
    rchecksum = ""
    # if checksum is coming than handle it differently
    if response[:5] == CHECK:
        print("Receiving checksum...")
        rchecksum = response[5:].strip()
        time.sleep(0.5)
    else:
        time.sleep(0.5)
        print("Server reponse -", response)
        print("File not exist on server....")
        print()
        return
    print("checksum received.")
    print(fileName)

    file = None
    fileData = None
    try:
        global serverSocket
        clientSocket.settimeout(2)
        fileData, serverAddr = clientSocket.recvfrom(buffer)
        file = open(fileName, "wb+") #Creating file
    except timeout:
        print("Server Busy.")
        print("Server time out...Please try after some time...")
        print("File downloading failed...")
        time.sleep(0.5)
        return
    print("Downloading ", fileName+"...")
    try:
        while True:
            file.write(fileData)
            clientSocket.settimeout(2)
            fileData, serverAddr = clientSocket.recvfrom(buffer)
    except timeout:
        file.close()

    # Creating checksum for checking correctness of file
    checkSum = hashlib.md5(open(fileName, "rb").read()).hexdigest()
    if rchecksum == checkSum:
        global COUNTER
        COUNTER = 0 #setting counter to zero - file is downloaded
        time.sleep(0.5)
        print("File Downloading Completed! -",os.path.getsize(fileName), "bytes downloaded.")
        pack = PACK + " " + SENDFILE
        clientSocket.sendto(pack.encode("utf-8"), serverAddr)
        time.sleep(0.5)
    else:
        print("checksum error..")
        return
        os.remove(fileName)
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Error on server...")
        print("File downloading failed.")
        time.sleep(0.5)
        if(COUNTER < 5):
            COUNTER += 1 #increasing counter
            print("Retrying to download the file...")
            time.sleep(0.5)
            nack = NACK + " " + SENDFILE
            clientSocket.sendto(nack.encode("utf-8"), serverAddr)
            listenForFile(fileName) #download file again

def options():
    'Gives user option to do file transfer.'
    while True:
        time.sleep(0.5)
        print("\n==========================ENTER COMMAND==========================")
        print("\t 'listf' to see list of files available on server\n",
              "\t 'close' to close the application\n")
        time.sleep(0.5)
        command = input("Udp > ")
        if command == "listf":
            requestList()
        elif command == "close":
            closeApp()
        else:
            print("Udp > Command Error")
            continue

def closeApp():
    "Close this application"
    time.sleep(0.5)
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Udp is going to close...")
    print("Closing socket to server...")
    print("Server disconnected....")
    clientSocket.close() #closing socket
    print("system exiting...")
    sys.exit() #exiting from the system
    print()
    print("\t\tBYE - SEE YOU NEXT TIME")
    print()


#////////////////////////////START CODE///////////////////////////////////////
options() #showing options to the user
