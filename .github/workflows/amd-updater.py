import subprocess,json,time
URL = r"""curl -f -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36' -L https://www.amd.com/en/support/graphics/amd-radeon-6000-series/amd-radeon-6900-series/amd-radeon-rx-6900-xt --referer 'https://www.amd.com/en' | grep -Eo 'https?://\S+?\"' """
co = subprocess.check_output(URL, shell=True).decode('utf-8')
dictionary_of_drivers = {}
for link in co.splitlines():
    if ".exe" in link and "pro-software" not in link and "minimalsetup" not in link:
        damnthisshit = (link.split('-'))
        for comeon in damnthisshit:
            if comeon.count('.') >= 2 and ".com" not in comeon:
                dictionary_of_drivers[comeon] = link
latest_driver_link = (dictionary_of_drivers[max(dictionary_of_drivers)])
latest_driver_version = max(dictionary_of_drivers)
time.sleep(30)
windows_driver_version = r"""wget -U 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36' -qO- """ + "https://www.amd.com/en/support/kb/release-notes/rn-rad-win-" + latest_driver_version.replace('.','-') + """ | sed -e 's/<[^>]*>//g'"""
windows_driver_version_output = subprocess.check_output(windows_driver_version, shell=True).decode('utf-8')
latest_driver_store_version = ""
for possible_driver_version in windows_driver_version_output.splitlines():
    if "Windows Driver Store" in possible_driver_version:
        latest_driver_store_version = possible_driver_version[possible_driver_version.find("Windows Driver Store Version ")+29:possible_driver_version.find(")")]
 
 
print(latest_driver_link)
print(latest_driver_version)
print(latest_driver_store_version)


with open('amd_gpu.json', 'r+') as f:
    data = json.load(f)
    if latest_driver_version > data["consumer"]["version"]:
        data["consumer"]["version"] = latest_driver_version
        data["consumer"]["win_driver_version"] = latest_driver_store_version
        data["consumer"]["link"] = latest_driver_link
    json.dump(data, f, indent=4)
    f.truncate()     # remove remaining part
    print(data)
