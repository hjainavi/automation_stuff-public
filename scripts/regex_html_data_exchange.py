import re

with open("/home/harsh/patch_optimistic_lock_tests.html","r") as f:
    patch_html = f.read()

pattern = re.compile('Plotly\.plot\(gd, \{\n.*(data.*\}\],)\n.*layout: \{"title": \{"text": "(.*Lock = \w{4,5})')
res = re.findall(pattern, patch_html)

print (res[0][1])
import ipdb;ipdb.set_trace()
abc = re.search(res[0][1],patch_html)
