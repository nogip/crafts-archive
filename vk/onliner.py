import json, time
import vk_api

class Account:

    def __init__(self, **kwargs):
        self.vk = None
        self.api = None

    def auth(self, login, password, **kwargs):
        try:
            self.vk = vk_api.VkApi(login, password, **kwargs)
            self.vk.auth()
            self.api = self.vk.get_api()
            return self
        except vk_api.AuthError as e:
            print(e)

ONLINER_CODE = 110
CONFIG = 'config.txt'
with open(CONFIG, 'r') as cfg:
    config = json.loads(cfg.read())

TIMEOUT = config['timeout'] # seconds

def two_factor():
    code = input('Code? ')
    return code, ONLINER_CODE

acc = Account()
acc.auth(config['login'], config['password'], auth_handler=two_factor)

while True:
    response = acc.api.account.setOnline()
    if response == 1:
        print('[@] Set online at', time.ctime())
        print('Sleep', TIMEOUT, 'sec...')
        time.sleep(TIMEOUT)
    print("[!] Err set online at", time.ctime())
    print('Sleep 1 sec...')
    time.sleep(1)

