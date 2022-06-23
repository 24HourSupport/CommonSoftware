import requests, subprocess,os
def download_helper(url, fname):
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


def latest_windows_version(majorversion):
    download_helper("https://raw.githubusercontent.com/pbatard/Fido/master/Fido.ps1",
                    "Fido.ps1")
    p = str(subprocess.Popen(
        "powershell.exe -ExecutionPolicy Bypass -file {directorytofido} -Win {version} -Rel List".format(
            version=majorversion, directorytofido=("Fido.ps1")),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate())
    dictionarytest = {}
    for release in p.split('\\n'):
        release = release.replace('build', 'Build')
        if "Build" in release:
            dictionarytest[release[3:release.index("(Build") - 1]] = \
                release[release.index("(Build") + 7:release.rfind("-", release.index("(Build"))].split(".", 1)[0]

    list2 = []
    for release in list(dictionarytest.values()):
        if int(release) not in list2:
            list2.append(int(release))

    return list2

jsonmain = {}

for release in [11, 10, 8.1, 8, 7]:
    jsonmain[release] = latest_windows_version(release)
    print(str(release) + " " + str(len(jsonmain[release])))
    if len(jsonmain[release]) < 1:
        raise ValueError('A very specific bad thing happened.')
if len(jsonmain) < 1:
        raise ValueError('A very specific bad thing happened. 2')
print((jsonmain))



import json

with open('WindowsReleases.json', 'w') as fp:
    json.dump(jsonmain, fp)

os.remove("Fido.ps1")