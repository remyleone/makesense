#!/usr/bin/env python3

from ipaddress import IPv6Address
from operator import xor

a = ("::323:4501:1779:343", "01:23:45:01:17:79:03:43")
n = int(a[1].replace(":", ""), 16) ^ (2**57)
print(IPv6Address(n), a[0])
