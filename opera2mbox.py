#!/usr/bin/python3
import os
import sys
import mailbox
import configparser


user = os.getlogin()
home = "/home/"+user

#-- Opera --#
path =  home+"/.opera/mail/"
mails = "store"
config = "accounts.ini"

#-- Thunderbird --#
thunder = home+"/.thunderbird/"
TbPath = ""

lines = []
TBirdConf = {}
OperaConf = {}
MigrateMbs = []


def checkTbird():
    
    tpd = ""
    tbInfo = []
    
    if not os.path.exists(thunder):
        print("Path to Thunderbird not found")
        print("Path: "+thunder)
        return False
    
    for dirs in os.listdir(thunder):
        d = dirs.split(".")
        if len(d) > 1 and os.path.isdir(thunder+dirs) and (d[1] == "default"):
            TbPath = thunder+dirs
            
    getTbirdConfig(TbPath)


            
def getTbirdConfig(p):
    
    prefs = p+"/prefs.js"
    token = ["directory","hostname","name","type","userName"]
    
    if not os.path.exists(prefs):
        return 0
    
    fp = open(prefs,"r")
    
    for line in fp:
        
        if ");" in line:
            ln = line.rstrip().replace(");","").replace("user_pref(","")
            data = ln.split(",")
            
            if 'mail.server' in data[0]:
                conf = data[0].strip('"').split(".")
                if conf[3] in token:
                    if conf[2] not in TBirdConf:
                        TBirdConf[conf[2]] = {}
                    TBirdConf[conf[2]][ conf[3]]=data[1].replace('"','').strip()
                    


def getMbox(account):
    md = path+mails+"/"+account
    if not os.path.exists(md):
        print("Path not found: "+md)
        return False
    
    os.chdir(md)
    mdir = os.getcwd()
    
    getMboxFiles(mdir)
    

def copyMboxFiles(opera,tbird):
    
    if not os.path.exists(tbird+"/Migration"):
        tBox = mailbox.mbox(tbird+"/Migration")
    else:
        print("The mailbox Migration exists! \nPlease remove it before starting the migration")
        sys.exit()
    
    for root, dirs, files in os.walk(opera):
        
        for fn in files:
            mb = mailbox.mbox(root+"/"+fn)
            for message in mb:
                tBox.add(message)
                tBox.flush()

def migrateMailboxes():
    
    if len(MigrateMbs) < 1:
        print("Noting to migrate")
        sys.exit()
    
    for mig in MigrateMbs:
        copyMboxFiles(mig["From"],mig["To"])
    
    


def configInfo():
    opmailConfig = configparser.ConfigParser(allow_no_value=True)
    if os.path.exists(path+config):
        fp = open(path+config,'r')
        
        for line in fp:
            lines.append(line)
        lines.pop(0)
        # print(lines)
        
        opmailConfig.read_string(''.join(lines))
        
        if len(opmailConfig.sections()) > 0:
        
            for section in opmailConfig.sections():
                if section != 'Accounts':
                    OperaConf[section] = {}
                    OperaConf[section]["name"] = opmailConfig.get(section,'Account Name',raw=False).strip()
                    OperaConf[section]["type"] = opmailConfig.get(section,'Incoming Protocol',raw=False).strip()
                    OperaConf[section]["directory"] = path+mails+"/"+section.lower()
                
        
    else:
        print("no Opera config file found")
        sys.exit()


    if not (os.path.exists(path+mails)):
        print("No Opera installtion found")
        print("check the path")
        sys.exit()
    


configInfo()

checkTbird()

if len(TBirdConf) > 0:
    print("Your Thunderbird Accounts")
    print("-------------------------")
    for key in TBirdConf.keys():
        print("Account: " + key)
        print("\tName: "+TBirdConf[key]["name"])
        print("\tType: "+TBirdConf[key]["type"])
    print("-------------------------\n")

if len(OperaConf) > 0:
    print("Your Opera Accounts")
    print("-------------------")
    for key in OperaConf.keys():
        print("Account: " + key)
        print("\tName: "+OperaConf[key]["name"])
        print("\tType: "+OperaConf[key]["type"])
   
print("\n-------------------------------\n")
print("Checking for Accounts to Migrate")
print("\n## Note: only POP-Accounts are to migrate! ##\n")    

for key in TBirdConf.keys():
    for k in OperaConf.keys():
        if TBirdConf[key]["name"] == OperaConf[k]["name"] and TBirdConf[key]["type"] == "pop3" and TBirdConf[key]["type"].rstrip("3") == OperaConf[k]["type"].lower():
            print("Migrate fom Opera:"+OperaConf[k]["directory"]+"  to Thunderbird:  " + TBirdConf[key]["directory"])
            MigrateMbs.append({"From":OperaConf[k]["directory"],"To":TBirdConf[key]["directory"]})
            
print()
print("Do you want to migrate?")
print("yes or no")
inp = input('-> ')
if inp == "yes":
    migrateMailboxes()
else:
    print("Not answered with 'yes'")
    print("Migration is aborted")
       
