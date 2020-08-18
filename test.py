import requests

def main():
    for i in range(100):
        r=requests.get("http://127.0.0.1:5000/add_sud_delo")
        print(r)

if __name__ == '__main__':
    main()