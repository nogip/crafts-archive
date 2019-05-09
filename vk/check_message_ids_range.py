import vk_api
import time
import datetime


def find_lost_msg(api, identifyers=range(10**7), only_private=True, user_id=None, sleep=5, size=100, step=1, write=None):
    # Хотел проверить насколько далеко можно заглянуть в прошлое переписок
    query = []
    count_in_iters = []
    epoch_counter = 0
    error_lock = False
    print('[+] Starts.')
    if write:
        f = open(write, 'w')
    else:
        f = None

    while identifyers:
        if error_lock:
            print('[+] Alive.'.format(sleep))
            error_lock = False
        part = identifyers[:size:step]
        identifyers = identifyers[size:]
        row = ','.join(list(map(str, part)))
        try:
            response = api.messages.getById(message_ids=row)
            count_in_iters.append(response.get('count'))
            items = response.get('items')
            if items:
                if only_private:
                    for msg in items:
                        if not len(str(msg.get('peer_id'))) == 10 and msg.get('peer_id') == user_id:
                            print('-'*80)
                            print('Found message. id:[{}], date:[{}]'
                                  .format(msg.get('id'), datetime.datetime.fromtimestamp(msg.get('date'))))
                            query.append(msg)
                else:
                    print('-'*80)
                    print('Found {} messages'.format(len(items)))
                    print('({}) --> ({})'.format(items[0].get('id'), items[-1].get('id')))
                    for msg in items:
                        query.append(msg)
                if f:
                    f.writelines((str(query) + '\n').strip())
                print('-'*10)

            epoch_counter += 1
            if epoch_counter % 20 == 0:
                print('[!] Current epoch: [({}) --> ({})]'.format(part[0], part[-1]))
        except Exception as err:
            print(err)
            print('[?] Sleep for {} sec...'.format(sleep))
            error_lock = True
            time.sleep(sleep)

    return query
