import subprocess,json,time,hashlib,shutil,os
 
latest_driver_link = ""
URL = r"""curl -f -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36' -L https://www.amd.com/en/support/graphics/amd-radeon-6000-series/amd-radeon-6900-series/amd-radeon-rx-6900-xt --referer 'https://www.amd.com/en' | grep -Eo 'https?://\S+?\"' """
co = subprocess.check_output(URL, shell=True).decode('utf-8')
for link in co.splitlines():
    if ".exe" in link and "pro-software" not in link and "minimalsetup" not in link:
        latest_driver_link = link[:link.find(".exe")+4]
        break
time.sleep(30)
Driver_URL = r"curl -f -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36' -L " + latest_driver_link + " --referer 'https://www.amd.com/en' -o amddriver.exe" 
 
co = subprocess.check_output(Driver_URL, shell=True)
 
z_extract = "7z x amddriver.exe Config/InstallManifest.json" 
 
co = subprocess.check_output(z_extract, shell=True)
 
latest_driver_version = ""
latest_driver_store_version = ""
with open("Config/InstallManifest.json") as f:
    data = json.load(f)
    latest_driver_version = (data['BuildInfo']['ExternalVersion'])
    latest_driver_store_version = ((data['Packages']['Package'][0]['Info']['version']))
 
 
 
with open('amd_gpu.json', 'r+') as f:
    data = json.load(f)
    if latest_driver_version > data["consumer"]["version"]:
        data["consumer"]["version"] = latest_driver_version
        data["consumer"]["win_driver_version"] = latest_driver_store_version
        data["consumer"]["link"] = latest_driver_link
        print("Getting MD5")
        data["consumer"]["MD5"] = hashlib.md5("amddriver.exe").hexdigest()
        print("MD5 got and written")
    f.seek(0)
    json.dump(data, f, indent=4)
    f.truncate()     # remove remaining part
    print(data)
shutil.rmtree('/Config/InstallManifest.json')
os.remove("amddriver.exe")
