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
 
co2 = subprocess.check_output(Driver_URL, shell=True)
 
z_extract = "7z x intel.zip Graphics/iigd_dch.inf" 

co3 = subprocess.check_output(z_extract, shell=True)

z_extract = "7z x readme.txt" 

co3 = subprocess.check_output(z_extract, shell=True)

r = "Graphics/iigd_dch.inf"
with open(r, "r", encoding='utf-16') as reaaaad: # Fuck you Intel with this UTF-16 shit
	lines = reaaaad.readlines()
ListOfSupportedGPUs = list()
for line in lines:
    if "DEV_" in line:
        ListOfSupportedGPUs.append(line[line.find("DEV_")+4:line.find("DEV_")+8])
print(ListOfSupportedGPUs) 



r = "readme.txt"
with open(r, "r", encoding='utf-16') as reaaaad: # Fuck you Intel with this UTF-16 shit
	lines = reaaaad.readlines()
for line in lines:
    if "Driver Version" in line:
        latest_driver_version = line[line.find("Driver Version: ")+len("Driver Version: "):].rstrip()
print(latest_driver_version) 




with open('intel_gpu.json', 'r+') as f:
    data = json.load(f)
    if version.parse(latest_driver_version) > version.parse(data["consumer"]["version"]):
        data["consumer"]["version"] = latest_driver_version
        data["consumer"]["link"] = latest_driver_link.replace("zip", "exe")
        data["consumer"]["SupportedGPUs"] = str(ListOfSupportedGPUs)
        print("Getting MD5")
        data["consumer"]["MD5"] = hashlib.md5(open("intel.zip",'rb').read()).hexdigest()
        print("MD5 got and written")
    f.seek(0)
    json.dump(data, f, indent=4)
    f.truncate()     # remove remaining part
    print(data)

shutil.rmtree('Graphics') 
os.remove("intel.zip")
