import json
import requests
import os
from bs4 import BeautifulSoup
import fnmatch
import os
import subprocess
import shutil

# Supported AMD PCI IDs:

amd_supported = {
    'consumer' : {'DeviceID': ['73AF', # RX 6900 
                               '743F', # RX 6400 
                               '731F', # RX 5700
                               '7340', # RX 5500
                               '66AF', # Radeon VII
                               '744C' # Radeon RX 7900 XT/7900 XTX
                               
                                        ], 
                'priority': '1',
                'description': 'AMD driver used by the vast majority of supported AMD GPUs',
                'link': 'https://www.amd.com/en/support/graphics/amd-radeon-6000-series/amd-radeon-6900-series/amd-radeon-rx-6900-xt',
                'filter_with': ['.exe','drivers.amd'],
                'filter_without': ['minimal','-pro-','rgb']},
    'polaris-vega' : {'DeviceID': ['6867', # Vega 56
                                   '67DF' # Radeon RX 470/480/570/570X/580/580X/590 (lol so specific AMD, goodjob)
                                        ], 
                'priority': '2',
                'description': 'AMD driver driver for Vega and Polaris GPUS',
                'link': 'https://www.amd.com/en/support/graphics/radeon-500-series/radeon-rx-500-series/radeon-rx-580',
                'filter_with': ['.exe','drivers.amd'],
                'filter_without': ['minimal','-pro-','rgb']},
    'professional' : {'DeviceID': ['73A3', # Radeon PRO W6800
                                       '6861' # Radeon PRO WX 9100
                                        ], 
                'priority': '3',
                'description': 'AMD PRO driver used by supported enterprise AMD GPUs',
                'link': 'https://www.amd.com/en/support/graphics/amd-radeon-6000-series/amd-radeon-6900-series/amd-radeon-rx-6900-xt',
                'filter_with': ['.exe','drivers.amd','-pro-'],
                'filter_without': ['minimal','rgb']}
}

def GetDriverLink(url,filter_with,filter_without):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'} 
    reqs = requests.get(url,headers=headers)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    
    urls = []
    for link in soup.find_all('a'):
        potential_link = str(link.get('href'))
        if all([x in potential_link for x in filter_with]):
            if not any([x in potential_link for x in filter_without]):
                return(potential_link)



def download_helper(url, fname):
    if os.path.exists(fname):
        os.remove(fname)
    from tqdm.auto import tqdm
    my_referer = "https://www.amd.com/en/support/graphics/amd-radeon-6000-series/amd-radeon-6700-series/amd-radeon-rx-6700-xt"
    print("Downloading file {}".format(fname.split("\\")[-1]))
    resp = requests.get(url, stream=True, headers={'referer': my_referer,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0'})
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    print("\n")


def GetDriverInfo(driver_url):
    download_helper(driver_url, 'amddriver.exe')
    try:
        shutil.rmtree('Packages')
    except:
        pass
    try:
        shutil.rmtree('Config') 
    except:
        pass
    z_extract = '7z x amddriver.exe Packages/Drivers/Display/WT6A_INF/*.inf' # This doesn't work on Windows for some reason, no idea why. 
    co3 = subprocess.run(z_extract, shell=True,check=True)
    fileinf = ""
    for file in os.listdir("Packages/Drivers/Display/WT6A_INF"):
        if file.endswith('.inf'):
            fileinf = file
            break
    supportGPUList = []
    with open("Packages/Drivers/Display/WT6A_INF/{}".format(fileinf)) as file:
        lines = file.readlines()
        for line in lines:
            if '"%AMD' in line.upper() and 'legacy' not in line.lower() and 'DEV_' in line.upper() and line[line.find('DEV_')+4:line.find('DEV_')+8] not in supportGPUList:
                supportGPUList.append(line[line.find('DEV_')+4:line.find('DEV_')+8])
    shutil.rmtree('Packages') 
    z_extract = "7z x amddriver.exe Config/InstallManifest.json" 
    co = subprocess.run(z_extract, shell=True,check=True)
    with open("Config/InstallManifest.json") as f:
        data = json.load(f)
        latest_driver_version = (data['BuildInfo']['ExternalVersion'])
        latest_driver_store_version = ((data['Packages']['Package'][0]['Info']['version']))
    shutil.rmtree('Config') 
    os.remove('amddriver.exe')
    return supportGPUList, latest_driver_store_version, latest_driver_version

final_json = {}
for branch in amd_supported:
    link = amd_supported[branch]['link']
    filter_with = amd_supported[branch]['filter_with']
    filter_without = amd_supported[branch]['filter_without']
    driver_link = GetDriverLink(link,filter_with,filter_without)
    driver_info = GetDriverInfo(driver_link)
    for confirm_gpu in amd_supported[branch]['DeviceID']:
        if confirm_gpu not in driver_info[0]:
            raise Exception("Expected GPU not in supported branch.") 
    final_json[branch] = {'version': driver_info[2], 'link': driver_link, 'win_driver_version': driver_info[1],'SupportedGPUs': driver_info[0],'MD5': 'N/A', 'priority': amd_supported[branch]['priority'],  'description': amd_supported[branch]['description']}

print(final_json)
with open("amd_gpu.json", "w+") as outfile:
    json.dump(final_json, outfile,indent=2)
