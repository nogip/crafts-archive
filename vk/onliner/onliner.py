import json, time
import vk_api

CONFIG = 'config.txt'
with open(CONFIG, 'r') as cfg:
    config = json.loads(cfg.read())

TIMEOUT = config['timeout'] # seconds

session = vk_api.VkApi(config['login'], config['password'])
session.http.headers.update({
    'User-agent': config['phone_user_agent']
})
session.auth()
api = session.get_api()

while True:
    response = api.account.setOnline()
    if response == 1:
        print('[@] Set online at', time.ctime())
        print('Sleep', TIMEOUT, 'sec...')
        time.sleep(TIMEOUT)
        continue
    print("[!] Err set online at", time.ctime())
    print('Sleep 1 sec...')
    time.sleep(1)