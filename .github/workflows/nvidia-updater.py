import urllib.request, json
from datetime import datetime, timezone




driver_links = {'consumer' : r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=98&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u', 'professional': r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=109&pfid=925&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u'
             ,   'r390' : r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=11&pfid=698&osID=57&languageCode=1033&beta=0&isWHQL=1',
                'r470_consumer' :  r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=85&pfid=627&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u'
                , 'r470_professional' : r'https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup&psid=74&pfid=751&osID=57&languageCode=1033&beta=0&isWHQL=1&dltype=-1&dch=1&u'}
updated_driver_details = {}
for driver in driver_links:

    uf = urllib.request.urlopen(driver_links[driver])
    html = uf.read()
    res = json.loads(html.decode('utf-8'))
    updated_driver_details[driver] = [float(res["IDS"][0]['downloadInfo']['Version']), res["IDS"][0]['downloadInfo']['DownloadURL']]

#print(updated_driver_details)


with open('nvidia_gpu.json', 'r+') as f:
    data = json.load(f)
    for driver_in_repo in data:
      if driver_in_repo != "Last_Checked":
        if float(data[driver_in_repo]['version']) < updated_driver_details[driver_in_repo][0]:
            data[driver_in_repo]['version'] = str(updated_driver_details[driver_in_repo][0])
            data[driver_in_repo]['link'] = updated_driver_details[driver_in_repo][1]
            f.seek(0)
    f.seek(0)
    data["Last_Checked"]["version"] = 'UTC: ' + str(datetime.now(timezone.utc).strftime("%d/%m/%Y %I%p"))
    json.dump(data, f, indent=4)
    f.truncate()     # remove remaining part
    print(data)
