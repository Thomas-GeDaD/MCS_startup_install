import os, subprocess, time
import RPi.GPIO as GPIO

instconf=False
instowire=False
MCSexists=False
MCSasd=False
count=0
pos=0
index=[]
UU=0
###check if autoshutdown is active (If a MCS is availible this Port is always true except on shutdown)
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)
if GPIO.input(5) == 1: 
    MCSasd=True
	
### Check i2c devices	
p = subprocess.Popen(['i2cdetect','-y', '1'], stdout=subprocess.PIPE,)
line = str(p.stdout.read())
linelst=line.split()
for i in linelst:
    if i=="4c"or i=="48" or i=="49":
        instconf=True
    if i=="18":
        instowire=True
    if i== "UU":
        UU+=1
    count+=1

### evaluate if MCS board exists    
if UU>=4 or instconf or instowire:
	if MCSasd:
		print ("board availible")
		MCSexists=True


	


def installconfigtxt():
	try:
		fo1 = open('/boot/config.txt',"a")
		fo1.write ("\n")
		fo1.write ("#MCS-Openplotter config (Do not delete or edit this part)(start)\n")
		fo1.write ("dtoverlay=mcp2515-can1,oscillator=16000000,interrupt=25\n")
		fo1.write ("dtoverlay=spi-bcm2835-overlay\n")
		fo1.write ("dtoverlay=sc16is752-i2c,int_pin=13,addr=0x4c,xtal=14745600\n")
		fo1.write ("dtoverlay=sc16is752-i2c,int_pin=12,addr=0x49,xtal=14745600\n")
		fo1.write ("dtoverlay=sc16is752-i2c,int_pin=6,addr=0x48,xtal=14745600\n")
		fo1.write ("#MCS-Openplotter config (Do not delete or edit this part)(end)\n")
		fo1.close()
		print("config.txt entries created")
	except: print ("cannot create config entrys")
	
	try:
		os.system('rm -f /etc/network/interfaces.d/can*')
		interfaceFile = '/etc/network/interfaces.d/can0'
		file = open(interfaceFile, 'w')
		file.write('#physical can interfaces\nallow-hotplug can0\niface can0 can static\nbitrate 250000\ndown /sbin/ip link set $IFACE down\nup /sbin/ifconfig $IFACE txqueuelen 10000')
		file.close()
	except: print ("cannot create can interface entries")

def installowire(): 
    ######added 1-wire modules
    print('Adding modules to /etc/modules...')
    
    try:
        modulesr = open("/etc/modules","r")
        strg=modulesr.read()
        modulesr.close()
        i2c_dev = strg.find("i2c-dev")
        ds2482 = strg.find("ds2482")
        wire = strg.find("wire")
        
        modules = open("/etc/modules","a")
        #######added i2c-dev
        if (i2c_dev==-1):
            modules.write ("\ni2c-dev")
            print(_("i2c-dev added to modules"))
        else:
            print(_("i2c-dev already exists"))
        #######added ds2482
        if (ds2482==-1):
            modules.write ("\nds2482")
            print(_("ds2482 added to modules"))
        else:
            print(_("ds2482 already exists"))
        #######added wire
        if (wire==-1):
            modules.write ("\nwire")
            print(_("wire added to modules"))
        else:
            print(_("wire already exists"))
        
        modules.close()
            
    except: print ("cannot create modules")



## check if config.txt entries availible
if MCSexists and instconf:
	try:
		fo1r = open('/boot/config.txt', "r")
		configcontent = fo1r.read()
		startpos = configcontent.find("#MCS-Openplotter config (Do not delete or edit this part)(start)")
		fo1r.close()
		print(startpos)
	except:
		print ("Cannot read config.txt")
		
	if startpos == -1:
		installconfigtxt()
	else:
		print("config.txt entries already exists")

## install 1-wire Modules		
if MCSexists and instowire:
	print ("install 1-wire")
	installowire()
	
###############Start I2C 1-Wire device

if MCSexists and instconf:
	time.sleep(10)
	print ("reboot")
	#os.system("sudo reboot")

try:
	os.system("echo '0x18' | sudo tee /sys/class/i2c-adapter/i2c-1/delete_device")
except:
	print ("cannot delete ds2482 device")
try:
	os.system("echo 'ds2482 0x18' | sudo tee /sys/class/i2c-adapter/i2c-1/new_device")
except:
	print ("creating 0X18 DS2482 as new_device not possible")

print ("I2C-1Wire Server started")
########################
