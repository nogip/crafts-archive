'''
This programm has to count the sectors for comfortable disk partitioning.
'''
import argparse
def sector(part, first):
    return int(first) + (int(part.size) * 1024**3) / int(part.block)

def count_blocks(args):
    count = int(args.count)
    if count == 1:
        print('%d - %d' % (args.first_block, sector(args, args.first_block)))
    if count > 1:
        first = int(args.first_block)
        for part in range(count):
            size = int(input('Size of %d partition (GB): ' % part))
            args.size = size
            last = sector(args, first)
            print('Part %d: ' % part,'%d - %d' % (first, last))
            first = last + 1

    
def initial():
    parser = argparse.ArgumentParser('Sector counter',
        description='This program counts sectors for each partition which you entered.')
    parser.add_argument('-s', '--size', default=0, help='Size of partition (GB)')
    parser.add_argument('-b', '--block', default=512, help='Size of one block (512b by default)')
    parser.add_argument('-c', '--count', default=1, help='Num of partitions for smart count')
    parser.add_argument('-f', '--first-block', default=2048, help='The first block (2048 by default')
    return parser.parse_args()

if __name__ == "__main__":
    count_blocks(initial())
