import mechanicalsoup as ms
import re, time
import vk_api

## Settings ##
TIMEOUT = 10	# minutes
login, password = 'stankin_login', 'stankin_password'
vk_login, vk_password = 'bot_login', 'bot_password'
me = 'your_domain'
## -------------------

STANKIN_LOGINPAGE = 'http://stankin.ru/for-entrants/info/login.php'
browser = ms.StatefulBrowser()
vk = vk_api.VkApi(vk_login, vk_password)
vk.auth()
api = vk.get_api()

def login_stankin(l=login, p=password):	
	browser.open(STANKIN_LOGINPAGE)
	browser.select_form('form[action="login_handler.php"]')
	browser['username'] = l
	browser['password'] = p
	browser.submit_selected()

def parse_table():
	page = browser.get_current_page().find('div', class_='text justify')
	ways = page.find('table').findAll('tr')
	info = []
	for i in range(len(ways)//3):
		wayname = re.search('\d\d.\d\d.\d\d', ways[0].text).group()
		pos = ways[2].findAll('td')
		info.append({
			wayname: [pos[3].text, pos[4].text, pos[5].text, pos[6].text]
		})
		ways = ways[3:]
	return info

def gen_report(info):
	wayid = list(info)[0]
	data = info.get(wayid)
	report = ''\
	'WayID: {}\n'\
	'- Kvote: {}\n'\
	'- Common list: {}\n'\
	'- By original: {}\n'\
	'- By original and accept: {}\n'\
	.format(wayid, data[0], data[1], data[2], data[3])
	return report

def notify(msg):
	api.messages.send(domain=me, message=msg)

def scan():
	while True:
		finfo = parse_table()
		full_report = "STANKIN\n{}\n{}\n{}"\
		.format(gen_report(finfo[0]), gen_report(finfo[1]), gen_report(finfo[2]))
		notify(full_report)
		time.sleep(TIMEOUT * 60)
		
if __name__ == '__main__':
	login_stankin()
	scan()