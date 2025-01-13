import os, hashlib
import ipdb

full_file_path = "/home/aviuser/AviGeoDb.txt.gz"


def SHA256Checksum(full_file_path):
    buf_size = 65536  # 64KB chunks
    #buf_size = 1048576
    sha256 = hashlib.sha256()
    if not os.path.exists(full_file_path):
        raise FileNotFoundError('File %s not found!' % full_file_path)
    with open(full_file_path, 'rb') as file:
        while True:
            data = file.read(buf_size)
            if not data:
                break
            sha256.update(data)
    sha256_checksum = sha256.hexdigest()   
    return sha256_checksum

def HashFileSha1(full_file_path):
    buf_size = 65536  # 64KB chunks
    #buf_size = 1048576
    sha1 = hashlib.sha1()
    if not os.path.exists(full_file_path):
        raise FileNotFoundError('File %s not found!' % full_file_path)
    with open(full_file_path, 'rb') as file:
        while True:
            data = file.read(buf_size)
            if not data:
                break
            sha1.update(data)
    sha1_checksum = sha1.hexdigest()   
    return sha1_checksum


print(SHA256Checksum(full_file_path))
print(HashFileSha1(full_file_path))
