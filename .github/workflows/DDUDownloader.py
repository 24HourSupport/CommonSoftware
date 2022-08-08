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


def ddu_download():
    import os
    download_helper(
        'https://raw.githubusercontent.com/Wagnard/display-drivers-uninstaller/WPF/display-driver-uninstaller/Display%20Driver%20Uninstaller/My%20Project/AssemblyInfo.vb',
        "AssemblyInfo.vb")

    my_file = open("AssemblyInfo.vb", "r")

    content = my_file.readlines()

    Latest_DDU_Version_Raw = ""

    for DDU_Version_Candidate in content:
        if 'AssemblyFileVersion' in DDU_Version_Candidate:
            Latest_DDU_Version_Raw = DDU_Version_Candidate[
                                     DDU_Version_Candidate.find('("') + 2:DDU_Version_Candidate.find('")')]
    countofloop = 0
    
    while not exists('https://www.wagnardsoft.com/DDU/download/DDU%20v' + Latest_DDU_Version_Raw + '.exe'):  # Normal error checking would not catch the error that would occur here.
        # You don't really need to understand this, basically
        # I have been looking at commit history, and there are instances where
        # he updates the github repos with a new version but doesn't make a release
        # yet, so this accounts for that possibility. Why is it so complicated?
        # It accounts for stuff like this:

        # 18.0.4.0 -> 18.0.3.9

        # 18.0.4.7 -> 18.0.4.6

        # Doesn't work for all cases (and I don't think it's possible for it to do so)
        # but it works 99.99% of the time.
        nums = Latest_DDU_Version_Raw.split(".")

        skip = 0

        for ind in range(skip, len(nums)):
            curr_num = nums[-1 - ind]
            if int(curr_num) > 0:
                nums[-1 - ind] = str(int(curr_num) - 1)
                break
            else:
                nums[
                    -1 - ind] = "9"  # DDU seems to stop at 9th versions: https://www.wagnardsoft.com/content/display-driver-uninstaller-ddu-v18039-released

        Latest_DDU_Version_Raw = '.'.join(nums)
        countofloop += 1
        if countofloop > 5:
            raise ValueError('Unable to find DDU version after 5 tries.')
        time.sleep(2)
    ddu_zip_path = "DDU.exe"
    download_helper(
            'https://www.wagnardsoft.com/DDU/download/DDU%20v' + Latest_DDU_Version_Raw + '.exe',
            ddu_zip_path
        )
    os.remove("AssemblyInfo.vb") 
    versionz = {"version" : Latest_DDU_Version_Raw}
    import json
    json_object = json.dumps(versionz, indent=4)
    with open("DDUVersion.json", "w") as outfile:
        outfile.write(json_object)

ddu_download()