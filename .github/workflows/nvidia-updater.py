import urllib.request, json, subprocess, os
from datetime import datetime, timezone
import time

def NVIDIADriverHandle():
  driver_links = {
                'consumer' : [1, r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=98&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u',
                            'NVIDIA game ready driver used by the vast majority of consumer NVIDIA GPUs'], 
                'professional':[2, r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=109&pfid=925&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u',
                              'NVIDIA driver used by supported professional NVIDIA GPUs (Quadro, Tesla, A series)'],   
                'consumer_studio' : [3,r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=101&pfid=816&osID=57&languageCode=1033&beta=0&isWHQL=0&dltype=-1&dch=1&upCRD=1&sort1=0',
                                    'NVIDIA studio driver used by the vast majority of consumer NVIDIA GPUs'],                                  
                'r470_consumer' :  [4,r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=85&pfid=627&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u',
                                  'NVIDIA driver branch used by consumer Kepler NVIDIA GPUs'], 
                'r470_professional' : [5,r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=74&pfid=751&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u',
                                      'NVIDIA driver branch used by professional Kepler NVIDIA GPUs']
    ,
                'datacenter' : [6,r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=118&pfid=923&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u',
                                'NVIDIA driver branch used by supported datacenter GPUs (DGX, HGX, EGX, vGPUs)'],
                'datacenter_kepler' : [7,r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=91&pfid=762&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u',
                                      'NVIDIA driver branch used by Kepler datacenter GPUs']                  
  }
  from urllib.request import urlopen, Request

  updated_driver_details = {}
  for driver in driver_links:
      uf = urlopen(Request(driver_links[driver][1], headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}))
      # uf = urllib.request.urlopen(driver_links[driver][1])
      html = uf.read()
      res = json.loads(html.decode('utf-8'))
      updated_driver_details[driver] = [float(res["IDS"][0]['downloadInfo']['Version']), res["IDS"][0]['downloadInfo']['DownloadURL'], driver_links[driver][0], driver_links[driver][2]]
  
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


  print(updated_driver_details)
  with open('nvidia_gpu.json', 'r+') as f:
      data = json.load(f)
      for driver_in_repo in data:
        if driver_in_repo in updated_driver_details:
          if float(data[driver_in_repo]['version']) < updated_driver_details[driver_in_repo][0]:
              data[driver_in_repo]['version'] = str(updated_driver_details[driver_in_repo][0])
              data[driver_in_repo]['priority'] = str(updated_driver_details[driver_in_repo][2]) # Used for AutoDDU to determine what driver to use if multiple supports a GPU. The lower the number the higher the priority.
              data[driver_in_repo]['link'] = updated_driver_details[driver_in_repo][1]
              data[driver_in_repo]['description'] = updated_driver_details[driver_in_repo][3]
              data[driver_in_repo]['SupportedGPUs'] = figureoutsupportedgpus(updated_driver_details[driver_in_repo][1])
              f.seek(0)
      f.seek(0)
      json.dump(data, f, indent=4)
      f.truncate()     # remove remaining part
      #print(data)

#Sometimes NVIDIA servers give bad results, I'm sick and tired of getting emails of failed runs
# Set the maximum number of tries
MAX_TRIES = 180

# Load the error count from a JSON file
with open('error_count_nvidia.json', 'r') as f:
    error_count = json.load(f)

# Try running the code up to the maximum number of tries
for try_count in range(MAX_TRIES):
    try:
        NVIDIADriverHandle()
        # Reset the error count if the code runs successfully
        error_count = 0
        with open('error_count_nvidia.json', 'w') as f:
            json.dump(error_count, f)
        break
    except KeyError:
        time.sleep(10)
        # Increase the error count and check if it has exceeded the limit
        error_count += 1
        with open('error_count_nvidia.json', 'w') as f:
            json.dump(error_count, f)
        if error_count > 30:
            raise KeyError("NVIDIA server errors have occurred more than 30 times.")
