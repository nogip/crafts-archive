import vk_api
import mechanicalsoup
import argparse
import urllib

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--login')
parser.add_argument('-p', '--password')
parser.add_argument('-td', '--target-domain')

args = vars(parser.parse_args())
__fields__ = ['login', 'password', 'target_domain']
for field in __fields__:
    if args.get(field) is None:
        args.update({field: input('{} >> '.format(field))})

browser = mechanicalsoup.StatefulBrowser()
login = args.get('login')
password = args.get('pass')

# Authentication
browser = mechanicalsoup.StatefulBrowser()
browser.open('https://vk.com')
browser.select_form()
browser['email'] = login
browser['pass'] = password
browser.submit_selected()


def parse_count(count):
    count = str(count)
    multiplyer = 1
    if count.endswith('K'):
        multiplyer = 1000
    count = count[:-1]
    count = int(float(count) * multiplyer)
    return count


def grab_users_ids(container, html_users):
    for user in html_users:
        container.append(str(user.attrs.get('href')).lstrip('/'))


def collect_likes(post):
    link = 'https://vk.com/wall{0}'.format(post)
    browser.open(link)
    page = browser.get_current_page()

    count = page.find('b', class_='v_like').text
    like_link = page.find('a', class_='item_like _i')
    browser.follow_link(like_link)

    domains = []
    offset = 0
    print(browser.get_url())
    while offset < parse_count(count):
        link = "https://m.vk.com/like?act=members&object=wall{}&offset={}".format(post_id, offset)
        browser.open(link)
        like_page = browser.get_current_page()
        users = like_page.findAll('a', class_='inline_item')
        grab_users_ids(domains, users)
        offset += 50
    return domains


def get_wall(domain, count=100, offset=0, ver='5.52'):
    method = 'https://api.vk.com/method/wall.get?domain={dom}$count={count}&offset={offset}&v={ver}'\
        .format(ver=ver, dom=domain, count=count, offset=offset)
    response = urllib.urlopen(method)

    print(response)


def check_target(target_domain, data):
    if target_domain in data:
        print('{} liked this post ({})\n'.format(target_domain, post_id))
    else:
        print('{} did not like this post ({})\n'.format(target_domain, post_id))


if __name__ == '__main__':
    friend_domain = args.get('target_domain')
    try:
        post = args.get('post_id').strip('\\"{}'.format("'"))
    except AttributeError:
        while True:
            post_id = input('next post_id >> ')
            check_target(friend_domain, collect_likes(post_id))
