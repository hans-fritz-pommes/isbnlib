#!/usr/bin/env python3
# flake8:noqa
# pylint:skip-file
# isort:skip_file
# fmt:off
# copied from: https://github.com/xlcnd/isbnlib/pull/120


from urllib.request import urlopen
from datetime import datetime, timezone
from time import sleep
from xml.dom import minidom
import urllib.error
import logging
import os

LOGGER = logging.getLogger(__name__)

RANGEFILEURL = 'https://www.isbn-international.org/export_rangemessage.xml'
M_DATE_FMT = '%a, %d %b %Y %H:%M:%S %Z'
MASKFILE = 'data4mask.py'
INFOFILE = 'data4info.py'


HEADER = """# flake8:noqa
# pylint:skip-file
# isort:skip_file
# fmt:off
# Produced by 'generate.py'@'{generatetime}'

#                   WARNING
# THIS FILE WAS PRODUCED BY TOOLS THAT AUTOMATICALLY
# GATHER THE RELEVANT INFORMATION FROM SEVERAL SOURCES
#            DON'T EDIT IT MANUALLY!

"""


MASKBODY = """
ranges={ranges}
RDDATE='{rddate}'
"""


INFOBODY = """
countries={countries}
identifiers={identifiers}
RDDATE='{rddate}'
"""


def ruletriples(node):
    rules = [] 
    for rule in node:
        start, end = rule.getElementsByTagName('Range')[0].firstChild.nodeValue.split('-')
        length = rule.getElementsByTagName('Length')[0].firstChild.nodeValue
        rules.append(tuple(map(int, [start, end, length])))
    return tuple(rules)


def group_identifiers(identifiers):
    """Group indentifier prefixes by length."""
    groups = {}
    for k in identifiers:
        _, group = k.split('-')
        if len(group) in groups:
            groups[len(group)].append(k)
        else:
            groups[len(group)] = [k]
    keys = list(groups.keys())
    keys.sort()
    return tuple([tuple(groups[k]) for k in keys])


def clean(s, style='mask'):
    """Perform formatting to match isbntools-dev ouput."""
    # This isn't strictly necessary, but makes it easy to diff the output
    s = s.replace("', '", "','").replace('), (', '),(')
    if style == 'info':
        s = s.replace("': '", "':'")
    return s

def restore():
    for file in[MASKFILE,INFOFILE]:
        if os.path.exists(file+'.old') and os.path.isfile(file+'.old'):
            f=open(file+'.old','rb')
            g=open(file,'wb')
            g.write(f.read())
            f.close()
            g.close()
            os.remove(file+'.old')

def update():
    generatetime = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    retrys=0
    while retrys<2:
        try:
            r = urlopen(RANGEFILEURL)
            print('Accessing "'+RANGEFILEURL+'"')
            break
        except urllib.error.HTTPError:
            retrys+=1
    if retrys==2:
        raise TimeoutError('Too many failed retrys accessing "'+RANGEFILEURL+'"')

    rm_old_exists=False

    for file in[MASKFILE,INFOFILE]:
        if os.path.exists(file) and os.path.isfile(file):
            if os.path.exists(file+'.old') and os.path.isfile(file+".old"):
                os.remove(file+".old")
            os.rename(file,file+".old")

    f=open('RangeMessage.xml','wb')
    f.write(r.read())
    f.close()
    print("RangeMessage.xml downloaded in "+str(retrys+1)+" tries")

    dom = minidom.parse('RangeMessage.xml')
    nodes = dom.getElementsByTagName('Group')
    messagedate = dom.getElementsByTagName('MessageDate')[0]
    rddate = datetime.strptime(messagedate.firstChild.nodeValue, M_DATE_FMT)
    rddate = datetime.strftime(rddate, '%Y%m%d')
    ranges = {}
    countries = {}
    for node in nodes:
        prefix = node.getElementsByTagName('Prefix')[0].firstChild.nodeValue
        agency = node.getElementsByTagName('Agency')[0].firstChild.nodeValue
        rules = node.getElementsByTagName('Rule')
        ranges[prefix] = ruletriples(rules)
        countries[prefix] = agency

    identifiers = group_identifiers(countries.keys())

    data = {
        'generatetime': generatetime,
        'ranges': ranges,
        'countries': countries,
        'identifiers': identifiers,
        'rddate': rddate}

    maskdata = clean((HEADER + MASKBODY).format(**data), 'mask')
    infodata = clean((HEADER + INFOBODY).format(**data), 'info')
        
    with open(MASKFILE, 'w',encoding="utf-8") as mask:
        mask.write(maskdata)
        mask.close()
        print("MASKFILE written")

    with open(INFOFILE, 'w',encoding="utf-8") as info:
        info.write(infodata)
        info.close()
        print("INFOFILE written")
    
    os.remove("RangeMessage.xml")


if __name__ == '__main__':
    update()
