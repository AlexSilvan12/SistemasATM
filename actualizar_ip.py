#!/usr/bin/python
import sys
DYNAMIC_DNS_URL = "https://ipv4.cloudns.net/api/dynamicURL/?q=OTkyMDc1ODo2MjAyOTQxNjM6NDFlMzQ3ZDhjOWJjZjkyNjQ1MTcwYmFlMGE5YWE4MjZlMTk1NjFlOGZmZWJkMGY3YTNlYjY0ZGNiNmVkYmU2Zg"
if sys.version_info[0] < 3:
 import urllib
 page = urllib.urlopen(DYNAMIC_DNS_URL);
 page.close();
else:
 import urllib.request
 page = urllib.request.urlopen(DYNAMIC_DNS_URL);
 page.close();