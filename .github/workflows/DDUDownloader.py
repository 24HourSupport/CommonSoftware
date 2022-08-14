import requests
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


def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok
import subprocess,shutil

def ddu_download():
    import os
    from urllib.request import Request, urlopen
    req = Request('https://www.wagnardsoft.com/DDU/currentversion2.txt', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0'})
    webpage = (urlopen(req, timeout=10).read())
    ddulatesturl = ('https://www.wagnardsoft.com/DDU/download/DDU%20v' + webpage.decode("utf-8")+ '.exe')
    ddu_zip_path = "DDU.exe"
    download_helper(
            ddulatesturl,
            ddu_zip_path
        )
    versionz = {"version" : webpage.decode("utf-8")}
    import json
    json_object = json.dumps(versionz, indent=4)
    with open("DDUVersion.json", "w") as outfile:
        outfile.write(json_object)
        outfile.close()
    os.mkdir('DDUTesting')

    ddu_extracted_path = 'DDUTesting'
    comazz= ddu_zip_path + " -o{}".format(ddu_extracted_path) + " -y"
    subprocess.run([ddu_zip_path,"-o", ddu_extracted_path,"-y"], shell=True,check=True)
    # Moves everything one directory up, mainly just to avoid crap with versioning, don't want to have to deal with
    # version numbers in the DDU method doing the command calling.
    where_it_is = os.path.join('DDUTesting',ddu_extracted_path, "DDU v{}".format(webpage.decode("utf-8")))
    file_names = os.listdir(where_it_is)

    for file_name in file_names:
        shutil.move(os.path.join(where_it_is, file_name), ddu_extracted_path)
    shutil.rmtree('DDUTesting')

ddu_download()