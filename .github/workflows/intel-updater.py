import subprocess,json,time,hashlib,shutil,os
from packaging import version
latest_driver_link = ""
latest_driver_version = ""
URL = r"""curl -f -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36' -L https://www.intel.com/content/www/us/en/download/19344/intel-graphics-windows-dch-drivers.html | grep -Eo 'https?://\S+?\"' """
co = subprocess.check_output(URL, shell=True).decode('utf-8')
for link in co.splitlines():
    if ".zip" in link:
        latest_driver_link = link[:link.find(".zip")+4]
        break

print(latest_driver_link)

time.sleep(30)
Driver_URL = r"curl -f -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36' -L " + latest_driver_link + " -o intel.zip" 
 
os.mkdir('IntelMess')


co2 = subprocess.check_output(Driver_URL, shell=True)
 
z_extract = "7z x intel.zip -oIntelMess" 

co3 = subprocess.check_output(z_extract, shell=True)

# z_extract = "7z x intel.zip readme.txt" 

# co3 = subprocess.check_output(z_extract, shell=True)

from pathlib import Path
ListOfSupportedGPUs = list()


print(Path('IntelMess').rglob('*.inf'))

for file in Path('IntelMess').rglob('*.inf'):
    with open(file, "r", encoding='utf-16') as reaaaad: # Fuck you Intel with this UTF-16 shit
        lines = reaaaad.readlines()
    for line in lines:
        if "DEV_" in line and line[line.find("DEV_")+4:line.find("DEV_")+8] not in ListOfSupportedGPUs:
            ListOfSupportedGPUs.append(line[line.find("DEV_")+4:line.find("DEV_")+8])
print(ListOfSupportedGPUs) 


acceptedversionchars = ['0', '1', '2', '3', '4', '5' ,'6', '7','8','9','.']
latest_driver_version = ""
for filtering in list(latest_driver_link.split('/')[-1]):
    if filtering in acceptedversionchars:
        latest_driver_version = latest_driver_version + filtering
print(latest_driver_version) 




with open('intel_gpu.json', 'r+') as f:
    data = json.load(f)
    if latest_driver_version != data["consumer"]["version"]:
        data["consumer"]["version"] = latest_driver_version
        data["consumer"]["link"] = latest_driver_link.replace("zip", "exe")
        data["consumer"]["SupportedGPUs"] = str(ListOfSupportedGPUs)
        print("Getting MD5")
        data["consumer"]["MD5"] = "N/A"
        print("MD5 got and written")
    f.seek(0)
    json.dump(data, f, indent=4)
    f.truncate()     # remove remaining part
    print(data)

shutil.rmtree('IntelMess') 
os.remove("intel.zip")

