import json
dafile = json.load(open("PCI-IDS.json"))
keylist = list(dafile.keys())
for vendor in list(dafile.keys()):
        if vendor != '8086' and vendor != '1002' and vendor != '10de' and vendor != '121a':
            # 1002 = AMD ; 8086 = Intel ; 10de = NVIDIA ; 121a = Voodoo (unlikely but I mean.. doesn't hurt?)
            del dafile[vendor]


with open("PCI-IDS.json", "w") as jsonFile:
        json.dump(dafile, jsonFile)
