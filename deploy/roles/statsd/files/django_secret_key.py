#!/usr/bin/env python
import string, random, argparse

parser = argparse.ArgumentParser()
parser.add_argument('file', type=argparse.FileType('w'), help='Where save secret key')

uni = string.ascii_letters + string.digits + string.punctuation
key = repr(''.join([random.SystemRandom().choice(uni) for i in range(random.randint(45, 50))]))

args = parser.parse_args()

with args.file as a_file:
    a_file.write(key)
