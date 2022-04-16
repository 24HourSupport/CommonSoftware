import urllib.request, json, subprocess, os
from datetime import datetime, timezone




driver_links = {'consumer' : r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=98&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u', 'professional': r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=109&pfid=925&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u'
             ,   'r390' : r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=11&pfid=698&osID=57&languageCode=1033&beta=0&isWHQL=1',
                'r470_consumer' :  r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=85&pfid=627&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u'
                , 'r470_professional' : r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=74&pfid=751&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u',
                'consumer_studio' : r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=101&pfid=816&osID=57&languageCode=1033&beta=0&isWHQL=0&dltype=-1&dch=1&upCRD=1&sort1=0'
               , 'datacenter' : r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=118&pfid=923&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u'
               , 'datacenter_kepler' : r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=91&pfid=762&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u'}
                
updated_driver_details = {}
for driver in driver_links:

    uf = urllib.request.urlopen(driver_links[driver])
    html = uf.read()
    res = json.loads(html.decode('utf-8'))
    updated_driver_details[driver] = [float(res["IDS"][0]['downloadInfo']['Version']), res["IDS"][0]['downloadInfo']['DownloadURL'], None]

def figureoutsupportedgpus(url):

      Driver_URL = r"curl -f -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36' -L " + url + " -o nvidiadriver.exe" 
      co2 = subprocess.check_output(Driver_URL, shell=True)
      z_extract = "7z x nvidiadriver.exe ListDevices.txt" 
      co3 = subprocess.check_output(z_extract, shell=True)
      testlist = []
      with open("ListDevices.txt") as file:
        lines = file.readlines()
        for line in lines:
            if 'DEV_' in line.upper() and line[line.find('DEV_')+4:line.find('DEV_')+8] not in testlist:
                testlist.append(line[line.find('DEV_')+4:line.find('DEV_')+8])
      os.remove('ListDevices.txt') 
      os.remove("nvidiadriver.exe") 
      return testlist




for driver in updated_driver_details:
  updated_driver_details[driver][2] = figureoutsupportedgpus(updated_driver_details[driver][1])

print(updated_driver_details)
with open('nvidia_gpu.json', 'r+') as f:
    data = json.load(f)
    for driver_in_repo in data:
      if driver_in_repo != "Last_Checked":
        if float(data[driver_in_repo]['version']) < updated_driver_details[driver_in_repo][0]:
            data[driver_in_repo]['version'] = str(updated_driver_details[driver_in_repo][0])
            data[driver_in_repo]['link'] = updated_driver_details[driver_in_repo][1]
            data[driver_in_repo]['SupportedGPUs'] = updated_driver_details[driver_in_repo][2]
            f.seek(0)
    f.seek(0)
    json.dump(data, f, indent=4)
    f.truncate()     # remove remaining part
    #print(data)
