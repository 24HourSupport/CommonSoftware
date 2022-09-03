import subprocess,json,time,hashlib,shutil,os
from packaging import version

latest_driver_link = ""
URL = r"""curl -f -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36' -L https://www.amd.com/en/support/graphics/amd-radeon-6000-series/amd-radeon-6900-series/amd-radeon-rx-6900-xt --referer 'https://www.amd.com/en' | grep -Eo 'https?://\S+?\"' """
co = subprocess.check_output(URL, shell=True).decode('utf-8')
for link in co.splitlines():
    if ".exe" in link and "pro-software" not in link and "minimalsetup" not in link:
        latest_driver_link = link[:link.find(".exe")+4]
        break
time.sleep(30)
Driver_URL = r"curl -f -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36' -L " + latest_driver_link + " --referer 'https://www.amd.com/en' -o amddriver.exe" 
 
co2 = subprocess.check_output(Driver_URL, shell=True)
 
z_extract = "7z x amddriver.exe Config/InstallManifest.json" 
 
co3 = subprocess.check_output(z_extract, shell=True)
 
latest_driver_version = ""
latest_driver_store_version = ""
with open("Config/InstallManifest.json") as f:
    data = json.load(f)
    latest_driver_version = (data['BuildInfo']['ExternalVersion'])
    latest_driver_store_version = ((data['Packages']['Package'][0]['Info']['version']))
shutil.rmtree('Config') 
## Enterprise GPU

for link in co.splitlines():
    if (".exe" in link) and ("-pro-" in link) and ("minimalsetup" not in link):
        latest_driver_link_enterprise = link[:link.find(".exe")+4]
        break
time.sleep(30)
Driver_URL = r"curl -f -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36' -L " + latest_driver_link_enterprise + " --referer 'https://www.amd.com/en' -o amddriverenterprise.exe" 
 
co = subprocess.check_output(Driver_URL, shell=True)
 
z_extract = "7z x amddriverenterprise.exe Config/InstallManifest.json" 
 
co = subprocess.check_output(z_extract, shell=True)
 
latest_driver_version_enterprise = ""
latest_driver_store_version_enterprise = ""
with open("Config/InstallManifest.json") as f:
    data = json.load(f)
    latest_driver_version_enterprise = (data['BuildInfo']['ExternalVersion'])
    latest_driver_store_version_enterprise = ((data['Packages']['Package'][0]['Info']['version']))
 
shutil.rmtree('Config') 

# Updating for all 

def supportedgpus(which):    
    if which == 1:
        x = "amddriver.exe"
    else:
        x = "amddriverenterprise.exe"
    z_extract = "7z x {} Packages/Drivers/Display/WT6A_INF".format(x)
 
    co3 = subprocess.check_output(z_extract, shell=True)
    fileinf = ""
    for file in os.listdir("Packages/Drivers/Display/WT6A_INF"):
        if file.endswith('.inf'):
            fileinf = file
            break
    testlist = []
    with open("Packages/Drivers/Display/WT6A_INF/{}".format(fileinf)) as file:
        lines = file.readlines()
        for line in lines:
            if '"%AMD' in line.upper() and 'legacy' not in line.lower() and 'DEV_' in line.upper() and line[line.find('DEV_')+4:line.find('DEV_')+8] not in testlist:
                testlist.append(line[line.find('DEV_')+4:line.find('DEV_')+8])
    shutil.rmtree('Packages') 
    return testlist

 
with open('amd_gpu.json', 'r+') as f:
    data = json.load(f)
    if latest_driver_version > data["consumer"]["version"]:
        data["consumer"]["version"] = latest_driver_version
        data["consumer"]["win_driver_version"] = latest_driver_store_version
        data["consumer"]["link"] = latest_driver_link
        data["consumer"]["SupportedGPUs"] = supportedgpus(1)
        data["consumer"]["priority"] = "1"
        print("Getting MD5")
        data["consumer"]["MD5"] = hashlib.md5(open("amddriver.exe",'rb').read()).hexdigest()
        print("MD5 got and written")
# version.parse(
    if version.parse(latest_driver_store_version) > version.parse(data["professional"]["win_driver_version"]):
        data["professional"]["version"] = latest_driver_version_enterprise
        data["professional"]["win_driver_version"] = latest_driver_store_version_enterprise
        data["professional"]["link"] = latest_driver_link_enterprise
        data["professional"]["SupportedGPUs"] = supportedgpus(0)
        data["professional"]["priority"] = "2"
        print("Getting MD5")
        data["professional"]["MD5"] = hashlib.md5(open("amddriverenterprise.exe",'rb').read()).hexdigest()
        print("MD5 got and written")
    f.seek(0)
    json.dump(data, f, indent=4)
    f.truncate()     # remove remaining part
    print(data)

os.remove("amddriver.exe")
os.remove("amddriverenterprise.exe")
