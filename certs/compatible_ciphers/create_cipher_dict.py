import os

ciphers = {
   "SSL_VERSION_TLS1":{
      "SSL_KEY_ALGORITHM_RSA":[],
      "SSL_KEY_ALGORITHM_EC":[]
   },
   "SSL_VERSION_TLS1_1":{
      "SSL_KEY_ALGORITHM_RSA":[],
      "SSL_KEY_ALGORITHM_EC":[]
   },
   "SSL_VERSION_TLS1_2":{
      "SSL_KEY_ALGORITHM_RSA":[],
      "SSL_KEY_ALGORITHM_EC":[]
   }
}
for f in os.listdir("./"):
    if ".txt" in f:
        with open(f,"r") as ff:
            for line in ff.readlines():
                val = line.strip().split(",")
                param1 = ""
                param2 = ""
                param3 = ""
                if "tls1_0" in f:
                    param1 = "SSL_VERSION_TLS1"
                elif "tls1_1" in f:
                    param1 = "SSL_VERSION_TLS1_1"
                elif "tls1_2" in f:
                    param1 = "SSL_VERSION_TLS1_2"
                if "rsa" in f:
                    param2 = "SSL_KEY_ALGORITHM_RSA"
                else:
                    param2 = "SSL_KEY_ALGORITHM_EC"
                #if "without" in f:
                #    param3 = "no_dh"
                #else:
                #    param3 = "dh"
                #ciphers[param1][param2][param3].append(val)
                ciphers[param1][param2].extend(val)
import json
print json.dumps(ciphers)
