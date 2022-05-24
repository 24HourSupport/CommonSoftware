# Credit to https://github.com/oko for creating this beautiful parser so I didn't have to. Whoever designed this formatting has to hate everyone.
# Who in their right fucking mind decided to use INDENTATION to mark this??? WHAT THE FUCK THIS IS SUCH A STUPID DESIGN DECISION
# Seriously, FUCK YOU PCI-IDS. WHY WHY WHY WHY WHY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Thank you for doing this Mister Oko, your work saved me a lot of headaches: https://github.com/oko/pci2json

import click
import json


class Vendor(object):
    def __init__(self, vid, name=None):
        self.vid = vid
        self.name = name
        self.devs = []

    def __repr__(self):
        return f"{self.vid} {self.name}" + ("\n" + "\n".join([repr(d) for d in self.devs]) if self.devs else "")

    def json(self):
        devs = {}
        for d in self.devs:
            devs.update(d.json())
        return {
            self.vid: {
                "name": self.name,
                "devices": devs
            }
        }


class Device(object):
    def __init__(self, ven, did, name=None):
        self.ven = ven
        self.ven.devs.append(self)
        self.did = did
        self.name = name
        self.subs = []

    def __repr__(self):
        return f"\t{self.did} {self.name}" + ("\n" + "\n".join([repr(s) for s in self.subs]) if self.subs else "")

    def json(self):
        subs = {}
        for s in self.subs:
            subs.update(s.json())
        return {
            self.did: {
                "name": self.name,
                "subsystems": subs,
            }
        }


class Subsys(object):
    def __init__(self, dev, svid, sdid, name=None):
        self.dev = dev
        self.dev.subs.append(self)
        self.svid = svid
        self.sdid = sdid
        self.name = name

    def __repr__(self):
        return f"\t\t{self.svid} {self.sdid} {self.name}"

    def json(self):
        return {
            self.id(): {
                "name": self.name,
                "subsys_vendor_id": self.svid,
                "subsys_device_id": self.sdid,
            }
        }

    def id(self):
        return f"{self.svid} {self.sdid}"


@click.command('pci2json')
@click.argument('pci_ids', type=click.File(mode='r', encoding='utf-8'))
@click.argument('json_out', type=click.File(mode='w', encoding='utf-8'))
def pci2json(pci_ids, json_out):
    all_lines = pci_ids.readlines()
    vendors = []
    vendor = None
    device = None
    subsys = None
    for line in all_lines:
        if "known device classes" in line:
            break
        if line.startswith('#'):
            continue
        if not line.strip():
            continue

        if line[0] != '\t':
            if vendor is not None:
                vendors.append(vendor)
            vendor = Vendor(*line.strip().split(maxsplit=1))
        if line[0] == '\t' and line[1] != '\t':
            device = Device(vendor, *line.strip().split(maxsplit=1))
        if line[0:2] == '\t\t':
            subsys = Subsys(device, *line.strip().split(maxsplit=2))

    vendict = {}
    for v in vendors:
        vendict.update(v.json())
    json.dump(vendict, json_out, indent=2)

    print(f"dumped {len(vendors)} vendors to {json_out.name}")


if __name__ == "__main__":
    pci2json()
    dafile = json.load(open("PCI-IDS.json"))
    keylist = list(dafile.keys())
    for vendor in list(dafile.keys()):
        if vendor != '8086' and vendor != '1002' and vendor != '10de' and vendor != '121a':
            # 1002 = AMD ; 8086 = Intel ; 10de = NVIDIA ; 121a = Voodoo (unlikely but I mean.. doesn't hurt?)
            del dafile[vendor]
    print(dafile.keys())


    with open("PCI-IDS.json", "w") as jsonFile:
        json.dump(dafile, jsonFile)
