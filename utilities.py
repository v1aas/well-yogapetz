import itertools
import random
import time
from loguru import logger

def save_errors(error):
    with open('errors.txt', 'a', encoding='utf-8') as file:
        file.write(f"\n{error}")

def get_invite():
    with open("data/invites.txt", 'r+', encoding='utf-8') as file:
        invites = file.readlines()
        if invites:
            invite = invites.pop(0)
            file.seek(0)
            file.truncate()
            file.writelines(invites)
            return invite.strip()
        else:
            raise FileNotFoundError("Файл с инвайтами пустой!")       

def save_invite(new_invite):
    with open("data/invites.txt", 'a', encoding='utf-8') as file:
        file.write(f"{new_invite}\n")

def get_random_daily_tweet():
    with open ("data/daily_tweets.txt", 'r', encoding='utf-8') as file:
        return random.choice(file.readlines())

def random_sleep():
    sec = random.randint(3,5)
    logger.info(f"Жду {sec} до выполнения следующего задания")
    time.sleep(sec)

def get_proxy():
    with open('data/proxy.txt', 'r') as file:
        return itertools.cycle([line.strip() for line in file.readlines()])

def get_tokens():
    with open('data/tokens.txt', 'r') as file:
        return [line.strip() for line in file.readlines()]

def get_tokens_change():
    with open('data/tokens_change.txt', 'r') as file:
        return [line.strip() for line in file.readlines()]

def get_keys():
    with open('data/keys.txt', 'r') as file:
        return [line.strip() for line in file.readlines()]

def to_proxy_format(proxy):
    return {
            'http': proxy,
            'https': proxy
    }