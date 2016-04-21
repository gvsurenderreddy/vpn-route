#!/usr/bin/env python

import urllib2
import re
import math


def get_ip():
    data = urllib2.urlopen(
        'http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest'
    ).read()

    cnregex = re.compile(r'^apnic\|cn\|ipv4\|[\d\.]+\|\d+\|\d+\|a\w*$', re.I | re.M)
    cndata = cnregex.findall(data)

    results = []

    for item in cndata:
        ip = item.split('|')
        ip_to = 32 - int(math.log(int(ip[4]), 2))
        results.append((ip[3] + '/' + str(ip_to)))

    return results


def put_ip(ips):
    up_script = """\
#!/bin/sh
export PATH="/bin:/sbin:/usr/sbin:/usr/bin"
OLDGW=`netstat -nr | grep '^default' | grep -v 'ppp' | sed 's/default *\\([0-9\.]*\\) .*/\\1/'`
if [ ! -e /tmp/pptp_oldgw ]; then
    echo "${OLDGW}" > /tmp/pptp_oldgw
fi
dscacheutil -flushcache
"""
    down_script = """\
#!/bin/sh
export PATH="/bin:/sbin:/usr/sbin:/usr/bin"
if [ ! -e /tmp/pptp_oldgw ]; then
    exit 0
fi
OLDGW=`cat /tmp/pptp_oldgw`
"""
    for ip in ips:
        up_script += ip + '\n'
        down_script += ip + '\n'

    open('/etc/ppp/ip-up', 'w').write(up_script)
    open('/etc/ppp/ip-down', 'w').write(down_script)

    print('ok')


def main():
    put_ip(get_ip())

if __name__ == '__main__':
    main()
