import urllib.request, json 
from packaging import version
import requests
import yaml
import os
import subprocess

def download_helper(url, fname):
    from tqdm.auto import tqdm
    print("Downloading file {}".format(fname.split("\\")[-1]))
    resp = requests.get(url, stream=True, headers={
        'User-Agent': 'winget/xx'}) # https://github.com/microsoft/winget-pkgs/issues/32777#issuecomment-953652832
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

def getlatest():
    with urllib.request.urlopen("https://api.github.com/repos/microsoft/winget-pkgs/contents/manifests/t/TechPowerUp/GPU-Z") as url:
        data = json.load(url)
    knownreleases = '0'

    for release in data:
        if version.parse(knownreleases) < version.parse(release['name']):
            knownreleases = release['name']
    return knownreleases


def downloadlatest():
    download_helper(f'https://raw.githubusercontent.com/microsoft/winget-pkgs/master/manifests/t/TechPowerUp/GPU-Z/{getlatest()}/TechPowerUp.GPU-Z.installer.yaml', 'GPU-Z.installer.yaml')
    with open("GPU-Z.installer.yaml", "r") as stream:
        latestyaml = yaml.safe_load(stream)
    os.remove('GPU-Z.installer.yaml')
    download_helper(latestyaml['Installers'][0]['InstallerUrl'], 'GPU-Z.exe')
    if CheckPublisherOfDriver('GPU-Z.exe') == False:
        raise Exception("Something went wrong, validation didn't checkout.") 


def CheckPublisherOfDriver(driver):
    p = str(subprocess.Popen(
            "powershell.exe (Get-AuthenticodeSignature '{driver}').SignerCertificate.subject".format(driver=driver),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
    if 'techpowerup' in p.lower():
        return True
    return False

(downloadlatest())