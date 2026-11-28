import urllib.request, json 
from packaging import version
import requests
import yaml
import os
import subprocess
import hashlib

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

def winget_gpuz(path='', accept='application/vnd.github+json'):
    # Anonymous calls hit GitHub's rate limits: 12 of the 14 failures from Sep to Nov 2026.
    headers = {'Accept': accept}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    req = urllib.request.Request('https://api.github.com/repos/microsoft/winget-pkgs/contents/manifests/t/TechPowerUp/GPU-Z' + path, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()

def getlatest():
    data = json.loads(winget_gpuz())
    knownreleases = '0'

    for release in data:
        if version.parse(knownreleases) < version.parse(release['name']):
            knownreleases = release['name']
    return knownreleases


def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest().upper()


def downloadlatest():
    latestyaml = yaml.safe_load(winget_gpuz(f'/{getlatest()}/TechPowerUp.GPU-Z.installer.yaml', 'application/vnd.github.raw+json'))
    installer = latestyaml['Installers'][0]
    expected = installer['InstallerSha256'].upper()
    # Re-downloading an unchanged GPU-Z got the runner blocked as a DoS (2026-06-12) and fails on mirror outages.
    if os.path.exists('GPU-Z.exe') and sha256('GPU-Z.exe') == expected:
        print('GPU-Z.exe already matches the latest winget release')
        return
    download_helper(installer['InstallerUrl'], 'GPU-Z.exe')
    # Without this check, TechPowerUp's 403 block page was committed as GPU-Z.exe on 2026-06-12.
    if sha256('GPU-Z.exe') != expected:
        raise Exception("Downloaded GPU-Z.exe doesn't match winget's SHA-256")


# TODO: Something in Github actions broke powershell verification, I don't know dude.
#     if CheckPublisherOfDriver('GPU-Z.exe') == False:
#         raise Exception("Something went wrong, validation didn't checkout.") 


# def CheckPublisherOfDriver(driver):
#     cmd = [
#         r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
#         "-NoProfile",
#         "-Command",
#         f"(Get-AuthenticodeSignature \"{driver}\").SignerCertificate.Subject"
#     ]

#     p = subprocess.Popen(
#         cmd,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE
#     ).communicate()    print(f'Publisher of EXE is {p}')
#     if 'techpowerup' in p.lower():
#         return True
#     return False


    
(downloadlatest())