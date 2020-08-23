import requests
import zlib,hashlib,uuid 
import json
def main():
	# print(zlib.crc32('Казаков Дмитрий Вячеславович'.encode()))
	# print(hashlib.sha224('Казаков Дмитрий Вячеславович'.encode()))
    for i in range(100):
        r=requests.get("http://127.0.0.1:5000/admin/add_user")
        print(r)
    # password=zlib.crc32('stolbunov.yaroslav@gmail.com'.encode())
    # print(password)
    #qqq@qqq.qqq -  
    # stolbunov.yaroslav@gmail.com- 2127642222
    # yaroher2442@gmail.com - 2124346601
    # def hash_password(password):
    #     salt = uuid.uuid4()
    #     return salt,hashlib.sha256(salt.hex.encode() + password.encode()).hexdigest() + ':' + salt.hex
    # print(hash_password(str(password)))
if __name__ == '__main__':
    main()