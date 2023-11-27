import json
from packaging import version
import requests
import zipfile
import shutil
import os
import re

# Full credit to MechanoPixel for figuring out how Intel's API works. 


# Supported Intel PCI IDs:

intel_supported = {
    'consumer' : {'DeviceID': ['3185', # Gemini Lake 
                               '4555', # Elkhart Lake
                               '9840', # Lakefield 1.5
                               '9841', # Lakefield 2
                               '4E55', # Jasperlake
                               '5912', # Kaby Lake
                               '5917', # Kaby Lake-R
                               '3E92', # Coffee Lake
                               '3E98', # Coffee Lake-R
                               '9BC5', # Comet Lake
                               '8A51' # Ice Lake
                                        ], 
                'priority': '2',
                'description': 'Intel GPU driver for 6th-10th gen graphics.'},
    'arc_consumer' : {'DeviceID': ['9A70', # Tiger Lake-H 
                                   '5692', # DG2 -M
                                   '56A0', # DG2
                                   'A780', # Raptor Lake
                                   '46D0', # Alder Lake-N
                                   '4C8A' # Rocket Lake
                                        ], 
                'priority': '1',
                'description': 'Intel GPU driver for consumer Arc and Xe graphics.'},
    'arc_professional' : {'DeviceID': ['56B1', # Arc Pro A40
                                       '56B0' # Arc Pro A30M
                                        ], 
                'priority': '3',
                'description': 'Intel GPU driver for PROFESSIONAL Arc-Pro graphics.'}
}
def download_helper(url, fname):
    from tqdm.auto import tqdm
    print("Downloading file {}".format(fname.split("\\")[-1]))
    resp = requests.get(url, stream=True, headers={
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

download_helper('https://dsadata.intel.com/data/en', 'idsa-en.zip')

def clean_string(input_string):
    # Remove everything but numbers and dots
    cleaned_string = re.sub(r'[^0-9.]', '', input_string)

    # Remove dots without numbers after them
    cleaned_string = re.sub(r'\.(?![0-9])', '', cleaned_string)

    return cleaned_string

with zipfile.ZipFile("idsa-en.zip","r") as zip_ref:
    zip_ref.extractall("intel-extract-work")

os.remove("idsa-en.zip")

with open("intel-extract-work/software-configurations.json", 'r') as f:
  data = json.load(f)








def GetLatestRelease(device_id):
    latest_release = '0'
    latest_release_link = ''
    latest_release_link_supported_gpus = []
    for release in data:
        if f'VEN_8086&DEV_{device_id[0].upper()}' in release['Components'][0]['DetectionValues']:
            found_version = clean_string(release['Version'])
            for possible_url in release['Files']:
                if '.exe' in possible_url['Url']:
                    if version.parse(found_version) > version.parse(latest_release):
                        latest_release = found_version
                        latest_release_link = possible_url['Url']
                        latest_release_link_supported_gpus = release['Components'][0]['DetectionValues']
    filtered_supported_gpus = []
    for gpu in latest_release_link_supported_gpus:
        filtered_supported_gpus.append(gpu[gpu.find('DEV_')+4:gpu.find('DEV_')+8].upper())
    filtered_supported_gpus = sorted(filtered_supported_gpus)
    for other_gpu in device_id:
        if other_gpu not in filtered_supported_gpus:
            print(other_gpu)
            raise Exception('Oh no') 
    return latest_release,latest_release_link, filtered_supported_gpus

intel_gpu = {}

for branch in intel_supported:
    info = GetLatestRelease(intel_supported[branch]['DeviceID'])
    intel_gpu[branch] = {"version": info[0],
                          "link": info[1],
                          "SupportedGPUs": info[2],
                          "MD5": 'N/A' ,
                          "priority": intel_supported[branch]['priority'],
                          "description": intel_supported[branch]['description'],
                          }

shutil.rmtree('intel-extract-work')

out_file = open("intel_gpu.json", "w+")
  
json.dump(intel_gpu, out_file, indent = 2)

print(intel_gpu)
    
