
import subprocess
import shlex
cmd = shlex.split("openssl ciphers -V")
output = subprocess.check_output(cmd).split("\n")

au_list = []
for rec in output:
    ind = [tmp.split("=")[1] for tmp in rec.split(" ") if "Au=" in tmp]
    if ind:
        au_list.append(ind[0])

final_list = list(set(au_list))

print final_list
