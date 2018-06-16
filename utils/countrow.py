import sys, os

DEBUG = 1
if len(sys.argv) > 1:
    PROJECT_DIR = os.path.abspath(sys.argv[1])
else:
    raise RuntimeError('PROJECT_DIR should be determined.')

if not os.path.exists(PROJECT_DIR):
    raise RuntimeError(PROJECT_DIR + ' is not exists.')
    
def logd(*msg):
    if DEBUG: print(*msg)
    
def count_rows_in_file(filepath):
    counted_rows = 0
    source = open(filepath, 'r')
    for row in source.readlines():
        if row.strip(): counted_rows += 1
    logd('{} {:^4} {}'.format('[+]',counted_rows, filepath))
    return counted_rows


def count_rows_in_dir(directory, extension='.py'):
    counted_in_dir = 0
    logd('\nCUR_DIR IS:', directory)
    for item in os.listdir(directory):
        itemfile = os.path.join(directory, item)
        if os.path.isdir(itemfile):
            counted_in_dir += count_rows_in_dir(itemfile)
        elif itemfile.endswith(extension):
            counted_in_dir += count_rows_in_file(itemfile)
    return counted_in_dir

if __name__ == '__main__':
    print('[+] ALL:', count_rows_in_dir(PROJECT_DIR))
