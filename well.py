import requests
import time
import asyncio
import random
import itertools
from loguru import logger
from client import Client
from manager_db import DatabaseManager
from better_automation.twitter import TwitterAccount, TwitterClient
from better_automation.utils import set_windows_selector_event_loop_policy
from well_web3 import connect_wallet, claim_daily_insight, claim_rank_insights, save_results, WEB3

set_windows_selector_event_loop_policy()
db_manager = DatabaseManager()
db_manager.connect()

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

def get_keys():
    with open('data/keys.txt', 'r') as file:
        return [line.strip() for line in file.readlines()]

async def login_twitter_with_invite(token, proxy):
    logger.info(f"Начинаю логин в твиттер с инвайтом")
    json = {
        "providerId":"twitter.com",
        "continueUri":"https://well3.com/assets/__/auth/handler",
        "customParameter":{}
    }
    headers_for_login={
        'origin': 'https://well3.com',
        'referer': 'https://well3.com/',
        'x-client-version': 'Chrome/Handler/2.20.2/FirebaseCore-web'
    }
    response_for_google = requests.post("https://www.googleapis.com/identitytoolkit/v3/relyingparty/createAuthUri?key=AIzaSyBPmETcQFfpDrw_eB6s8DCkDpYYBt3e8Wg", json=json, headers=headers_for_login)
    oauth_token = response_for_google.json()['authUri'].split('=')[1]
    session_id = response_for_google.json()['sessionId']
    invite = get_invite()
    try:
        async with TwitterClient(TwitterAccount(token), proxy=proxy, verify=False) as twitter:
            redirect_url, authenticity_token = await twitter.oauth(oauth_token)
            json = {
                "requestUri": redirect_url,
                "sessionId": session_id,
                "returnSecureToken": True,
                "returnIdpCredential": True
            }
            response = requests.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key=AIzaSyBPmETcQFfpDrw_eB6s8DCkDpYYBt3e8Wg", json=json)
            if response.status_code == 200:
                id_token = response.json()['idToken']
                oauth_access_token = response.json()['oauthAccessToken']
                oauth_token_secret = response.json()['oauthTokenSecret']
            else:
                logger.error(f"Ошибка - login_twitter. {response.status_code}. {response.text}")
            headers_for_login = {
                'authorization': id_token,
                'origin': 'https://well3.com',
                'referer': 'https://well3.com/',
            }
            json = {
                "oauth":{
                    "oauthAccessToken": oauth_access_token,
                    "oauthTokenSecret": oauth_token_secret
                }
            }
            response = requests.post("https://api.gm.io/ygpz/link-twitter", headers=headers_for_login, json=json)
            if response.status_code == 200:
                logger.success("Твиттер успешно привязан")
            else:
                logger.error(f"Ошибка при привязке твиттера. {response.status_code}. {response.text}")
            response = requests.post("https://api.gm.io/ygpz/enter-referral-code", headers=headers_for_login, json={"code":invite})
            if response.status_code == 200:
                logger.success(f"Инвайт {invite} успешно привязан")
            else:
                logger.error(f"Ошибка при привязке инвайта. {response.status_code}. {response.text}")
            response = requests.post("https://api.gm.io/ygpz/generate-codes", headers=headers_for_login, json={})
            if response.status_code == 200:
                logger.success(f"Инвайты успешно созданы")
            else:
                logger.error(f"Ошибка при создании инвайтов. {response.status_code}. {response.text}")
            return headers_for_login
    except AttributeError as ae:
        logger.error(f"Токен не валидный. {token}")
        save_errors(f"Токен не валидный. {token}")
        return None
    except Exception as e:
        if "'NoneType' object has no attribute 'get'" in e:
            logger.error(f"Аккаунт заблокирован или поймал капчу. {token}")
            save_errors(f"Аккаунт заблокирован или поймал капчу. {token}")
            return None
        else:
            logger.error(f"Ошибка - login_twitter. {e}")
            save_errors(f"Ошибка - login_twitter. {e}")
            return None
        
async def get_headers(token, proxy):
    logger.info(f"Начинаю логин в твиттер")
    json = {
        "providerId":"twitter.com",
        "continueUri":"https://well3.com/assets/__/auth/handler",
        "customParameter":{}
    }
    headers_for_login={
        'origin': 'https://well3.com',
        'referer': 'https://well3.com/',
        'x-client-version': 'Chrome/Handler/2.20.2/FirebaseCore-web'
    }
    try:
        response_for_google = requests.post("https://www.googleapis.com/identitytoolkit/v3/relyingparty/createAuthUri?key=AIzaSyBPmETcQFfpDrw_eB6s8DCkDpYYBt3e8Wg", json=json, headers=headers_for_login)
        oauth_token = response_for_google.json()['authUri'].split('=')[1]
        session_id = response_for_google.json()['sessionId']
        async with TwitterClient(TwitterAccount(token), proxy=proxy, verify=False) as twitter:
            redirect_url, authenticity_token = await twitter.oauth(oauth_token)
            json = {
                "requestUri": redirect_url,
                "sessionId": session_id,
                "returnSecureToken": True,
                "returnIdpCredential": True
            }
            response = requests.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key=AIzaSyBPmETcQFfpDrw_eB6s8DCkDpYYBt3e8Wg", json=json)
            if response.status_code == 200:
                id_token = response.json()['idToken']
                oauth_access_token = response.json()['oauthAccessToken']
                oauth_token_secret = response.json()['oauthTokenSecret']
            else:
                logger.error(f"Ошибка - login_twitter. {response.status_code}. {response.text}")
            headers_for_login = {
                'authorization': id_token,
                'origin': 'https://well3.com',
                'referer': 'https://well3.com/',
            }
            json = {
                "oauth":{
                    "oauthAccessToken": oauth_access_token,
                    "oauthTokenSecret": oauth_token_secret
                }
            }
            response = requests.post("https://api.gm.io/ygpz/link-twitter", headers=headers_for_login, json=json)
            if response.status_code == 200:
                logger.success("Твиттер успешно привязан")
            else:
                logger.error(f"Ошибка при привязке твиттера. {response.status_code}. {response.text}")
            return headers_for_login
    except Exception as e:
        if "'NoneType' object has no attribute 'get'" in e:
            logger.error(f"Аккаунт заблокирован или поймал капчу. {token}")
            save_errors(f"Аккаунт заблокирован или поймал капчу. {token}")
        else:
            logger.error(f"Ошибка - login_twitter. {e}")
            save_errors(f"Аккаунт заблокирован или поймал капчу. {token}")
        
async def update_invites():
    proxys = get_proxy()
    for acc in db_manager.get_accounts():
        headers = await get_headers(acc[0], next(proxys))
        response = requests.post("https://api.gm.io/ygpz/generate-codes", headers=headers, json={})
        if response.status_code == 200:
            logger.success(f"Инвайты успешно созданы")
        else:
            logger.error(f"Ошибка при создании инвайтов. {response.status_code}. {response.text}")
        response = requests.get("https://api.gm.io/ygpz/me", headers=headers)
        if response.status_code == 200:
            invites = response.json()['referralInfo']['myReferralCodes']
            for new_invite in invites:
                if 'usedAt' in new_invite:
                    logger.info("Инвайт использован")
                    continue
                save_invite(new_invite['code'])
        else:
            logger.error(f"Ошибка при сохранении инвайтов. {acc[0]}")
        logger.success("Инвайты успешно сохранены")

def get_num_daily_tweet(headers_for_login):
    response = requests.get("https://api.gm.io/ygpz/me", headers=headers_for_login)
    if response.status_code == 200:
        daily = response.json()['contractInfo']['dailyQuest']['nonce'].split('-')
        return list(daily)[2]
    else:
        logger.error("Ошибка при получении название дейли квеста")

def get_uncomplete_tasks(headers_for_login):
    tasks = []
    response = requests.get("https://api.gm.io/ygpz/me", headers=headers_for_login)
    if response.status_code == 200:
        raw_tasks = response.json()['ygpzQuesting']['rawSpecialProgress']
        if 'follow-gmio' not in raw_tasks:
            tasks.append("follows")
            logger.info("Задание с подписками было не выполнено")
        if 'retweet-CyberKongz-1750535387095691606' not in raw_tasks:
            tasks.append("like_retweet3")
            logger.info("Задание лайк+ретвит#3 был не выполнено")
        if 'retweet-yogapetz-1750523880463340019' not in raw_tasks:
            tasks.append("like_retweet2")
            logger.info("Задание лайк+ретвит#2 было не выполнено")
        if 'retweet-yogapetz-1745127428039847937' not in raw_tasks:
            tasks.append("like_retweet")
            logger.info("Задание лайк+ретвит#1 было не выполнено")
        if 'set-well-twitter-profile-banner' not in raw_tasks:
            tasks.append("set_banner")
            logger.info("Задание с баннером не выполнено")
        return tasks
    else:
        logger.error("Ошибка при проверки заданий")

def complete_breath_session(headers_for_login):
    response = requests.post("https://api.gm.io/ygpz/complete-breath-session", json={}, headers=headers_for_login)
    if response.status_code == 200:
        logger.success("Клейм за ежедневную метидацию успешен!")
    else:
        logger.error(f"Ошибка при клейме ежедневной метидации. {response.status_code}. {response.text}")

async def post_daily_tweet(token, headers_for_login, proxy):
    num = get_num_daily_tweet(headers_for_login)
    response = requests.post(f"https://api.gm.io/ygpz/claim-exp/{num}-post-daily-yoga-photo", json={}, headers=headers_for_login)
    if response.status_code == 400:
        return
    try:
        async with TwitterClient(TwitterAccount(token), proxy=proxy, verify=False) as twitter:
            tweet = get_random_daily_tweet()
            tweet_id = await twitter.tweet(tweet)
            logger.info(f"Дейли пост твитнут, твит id: {tweet_id}")
        if response.status_code == 200:
            logger.success("Клейм за ежедневый твит успешен!")
        else:
            logger.error(f"Ошибка при клейме ежедневый твит. {response.status_code}. {response.text}")
    except Exception as e:
        logger.error(f"Ошибка - post_daily_tweet|{e}|{token}")
        save_errors(f"Ошибка - post_daily_tweet|{e}|{token}")
    
def set_banner(headers_for_login):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/set-well-twitter-profile-banner", json={}, headers=headers_for_login)
    if response.status_code == 200:
        logger.success("Клейм за баннер успешен!")
    else:
        logger.error(f"Ошибка при за баннер. {response.status_code}. {response.text}")
    
def like_retweet(headers_for_login):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/retweet-yogapetz-1745127428039847937", json={}, headers=headers_for_login)
    if response.status_code == 200:
        logger.success("Клейм за лайк+ретвит #1 успешен!")
    else:
        logger.error(f"Ошибка при за лайк+ретвит #1. {response.status_code}. {response.text}")
    
def like_retweet2(headers_for_login):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/retweet-yogapetz-1750523880463340019", json={}, headers=headers_for_login)
    if response.status_code == 200:
        logger.success("Клейм за лайк+ретвит #2 успешен!")
    else:
        logger.error(f"Ошибка при за лайк+ретвит #2. {response.status_code}. {response.text}")
    
def like_retweet3(headers_for_login):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/retweet-CyberKongz-1750535387095691606", json={}, headers=headers_for_login)
    if response.status_code == 200:
        logger.success("Клейм за лайк+ретвит #3 успешен!")
    else:
        logger.error(f"Ошибка при за лайк+ретвит #3. {response.status_code}. {response.text}")
    
def follows(headers_for_login):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/follow-yogapetz", json={}, headers=headers_for_login)
    if response.status_code == 200:
        logger.success("Клейм за подписку #1 успешен!")
    else:
        logger.error(f"Ошибка при за подписку #1. {response.status_code}. {response.text}")
    time.sleep(random.randrange(3,5))
    response = requests.post("https://api.gm.io/ygpz/claim-exp/follow-keung", json={}, headers=headers_for_login)
    if response.status_code == 200:
        logger.success("Клейм за подписку #2 успешен!")
    else:
        logger.error(f"Ошибка при за подписку #2. {response.status_code}. {response.text}")
    time.sleep(random.randrange(3,5))
    response = requests.post("https://api.gm.io/ygpz/claim-exp/follow-gmio", json={}, headers=headers_for_login)
    if response.status_code == 200:
        logger.success("Клейм за подписку #3 успешен!")
    else:
        logger.error(f"Ошибка при за подписку #2. {response.status_code}. {response.text}")
    
async def complete_task_twitter(token, proxy, tasks = None):
    async def set_banner(twitter):
        logger.info("Ставлю баннер")
        image = open("data/1500x500.jpg", "rb").read()
        media_id = await twitter.upload_image(image)
        banner_image_url = await twitter.update_profile_banner(media_id)
        if banner_image_url is not None:
            logger.success("Баннер успешно поставлен")
        else: 
            logger.error("Ошибка. Баннер не поставлен")
    
    async def like_retweet(twitter):
        logger.info("Лайк+ретвит #1")
        logger.info(f"Твит 1 лайкнут: {await twitter.like('1745127428039847937')}")
        time.sleep(random.randint(2,4))
        logger.info(f"Твит 1 ретвитнут: {await twitter.repost('1745127428039847937')}")
    
    async def like_retweet2(twitter):
        logger.info("Лайк+ретвит #2")
        logger.info(f"Твит 2 лайкнут: {await twitter.like('1750523880463340019')}")
        time.sleep(random.randint(2,4))
        logger.info(f"Твит 2 ретвитнут: {await twitter.repost('1750523880463340019')}")
    
    async def like_retweet3(twitter):
        logger.info("Лайк+ретвит #3")
        logger.info(f"Твит 3 лайкнут: {await twitter.like('1750535387095691606')}")
        time.sleep(random.randint(2,4))
        logger.info(f"Твит 3 ретвитнут: {await twitter.repost('1750535387095691606')}")
        
    functions = []
    if tasks is None:
        functions = [set_banner, like_retweet, like_retweet2, like_retweet3]
    else:
        for task in tasks:
            if task is "follows":
                continue
            elif task is "set_banner":
                functions.append(set_banner)
            elif task is "like_retweet":
                functions.append(like_retweet)
            elif task is "like_retweet2":
                functions.append(like_retweet2)
            elif task is "like_retweet3":
                functions.append(like_retweet3)
    try:
        async with TwitterClient(TwitterAccount(token), proxy=proxy, verify=False) as twitter:
            for func in functions:
                await func(twitter)            
                sec = random.randint(5,10)
                logger.info(f"Сплю {sec} перед следующим действием")
                time.sleep(sec)
    except Exception as e:
        logger.error(f"Ошибка - complete_task_twitter. {e}")
        save_errors(f"Ошибка - complete_task_twitter. {e}")
        
async def complete_tasks_well():
    try:
        proxys = get_proxy()
        tokens = get_tokens()
        keys = get_keys()
        if len(tokens) != len(keys):
            logger.error("Токены и ключи не равны в количестве!")
            return
        for index, (token, key) in enumerate(zip(tokens, keys), start=1):
            proxy = next(proxys)
            logger.info(f"ТОКЕН: {index}/{len(tokens)} {token}")
            client = Client(WEB3, key)
            headers_for_login = await login_twitter_with_invite(token, proxy)
            if headers_for_login is None:
                continue
            is_connect = connect_wallet(headers_for_login, client)
            if is_connect:
                db_manager.save_account(token, client.private_key)
            else:
                save_errors(f"Ошибка при привязке кошелька: {token};{client.address}")
            TASKS = [
                (complete_task_twitter, [token, proxy]),
                (complete_breath_session, [headers_for_login]),
                (post_daily_tweet, [token, headers_for_login, proxy]),
                (set_banner, [headers_for_login]),
                (like_retweet, [headers_for_login]),
                (like_retweet2, [headers_for_login]),
                (like_retweet3, [headers_for_login]),
                (follows, [headers_for_login]),
            ]
            logger.info("Начинаю выполнять задания")
            time.sleep(0.5)
            for task, args in TASKS:
                if asyncio.iscoroutinefunction(task):
                    await task(*args)
                else:
                    task(*args)
                random_sleep()
            logger.success(f"Все задания выполнены. {token}")
    except Exception as e:
        if "'NoneType' object has no attribute 'get'" in e:
            logger.error(f"Аккаунт заблокирован или поймал капчу. {token}")
            save_errors(f"Аккаунт заблокирован или поймал капчу. {token}")
        else:
            logger.error(f"Ошибка - login_twitter. {e}")
            save_errors(f"Аккаунт заблокирован или поймал капчу. {token}")      

async def complete_daily_tasks():
    try:
        proxys = get_proxy()
        proxy = next(proxys)
        accounts = db_manager.get_accounts()
        for index, acc in enumerate(accounts, start=1):
            token = acc[0]
            key = acc[1]
            logger.info(f"Начинаю выполнять дневные задания. {index}/{len(accounts)} {token}")
            headers_for_login = await get_headers(token, proxy)

            TASKS = [
                (complete_breath_session, [headers_for_login]),
                (post_daily_tweet, [token, headers_for_login, proxy])
            ]
            
            for task, args in TASKS:
                if asyncio.iscoroutinefunction(task):
                    await task(*args)
                else:
                    task(*args)
                random_sleep()
                
            logger.success(f"Все задания выполнены. {token}")
            claim_daily_insight(headers_for_login, Client(WEB3, key))
    except Exception as e:
        if "'NoneType' object has no attribute 'get'" in e:
            logger.error(f"Аккаунт заблокирован или поймал капчу. {token}")
            save_errors(f"Аккаунт заблокирован или поймал капчу. {token}")
        else:
            logger.error(f"Ошибка - login_twitter. {e}")
            save_errors(f"Ошибка - login_twitter. {token}")

async def check_and_complete_tasks():
    try:
        proxys = get_proxy()
        proxy = next(proxys)
        accounts = db_manager.get_accounts()
        for index, acc in enumerate(accounts, start=1):
            token = acc[0]
            logger.info(f"Начинаю проверку выполненных заданий. {index}/{len(accounts)} {token}")
            headers_for_login = await get_headers(token, proxy)
            uncomplete_tasks = get_uncomplete_tasks(headers_for_login)
            TASKS = []
            if len(uncomplete_tasks) == 0:
                logger.success(f"Все задания выполнены. {token}")
                continue
            else:
                for task in uncomplete_tasks:
                    if task is "set_banner":
                        TASKS.append((set_banner, [headers_for_login]))
                    elif task is "like_retweet":
                        TASKS.append((like_retweet, [headers_for_login]))
                    elif task is "like_retweet2":
                        TASKS.append((like_retweet2, [headers_for_login]))
                    elif task is "like_retweet3":
                        TASKS.append((like_retweet3, [headers_for_login]))
                    elif task is "follows":
                        TASKS.append((follows, [headers_for_login]))
            await complete_task_twitter(token=token, proxy=proxy, tasks=uncomplete_tasks)
            for task, args in TASKS:
                if asyncio.iscoroutinefunction(task):
                    await task(*args)
                else:
                    task(*args)
                random_sleep()
            logger.success(f"Все задания выполнены. {token}")
    except Exception as e:
        if "'NoneType' object has no attribute 'get'" in e:
            logger.error(f"Аккаунт заблокирован или поймал капчу. {token}")
            save_errors(f"Аккаунт заблокирован или поймал капчу. {token}")
        else:
            logger.error(f"Ошибка - check_and_complete_tasks. {e}")
            save_errors(f"Ошибка - check_and_complete_tasks. {token}")

def refresh_info_for_books():
    logger.info("Обновляю количество книг")
    for acc in db_manager.get_accounts():
        save_results(Client(WEB3, acc[1]))

def get_all_stats_book():
    refresh_info_for_books()
    for acc in db_manager.get_stats_of_all_accounts():
        client = Client(WEB3, acc[1])
        logger.info(f"Аккаунт {acc[0]};{client.address} имеет: un {acc[2]} ra {acc[3]} le {acc[4]} my {acc[5]}")
    all_stats = db_manager.get_all_stats_book()[0]
    logger.info((f"Общее количество:\nuncommon: {all_stats[0]}\nrare: {all_stats[1]}\nlegendary: {all_stats[2]}\nmythical: {all_stats[3]}"))
        
async def claim_books():
    proxys = get_proxy()
    proxy = next(proxys)
    for acc in db_manager.get_accounts():
        token = acc[0]
        key = acc[1]
        headers_for_login = await get_headers(token, proxy)
        logger.info(f"Начинаю выполнять клеймить книжки. {token}")
        claim_rank_insights(headers_for_login, Client(WEB3, key))

def update_token():
    old_token = input("Введите старый токен: ")
    print("")
    new_token = input("Введите новый токен: ")
    db_manager.update_token(old_token, new_token)

def intro():
    business_card = """
    ╔════════════════════════════════════════╗
    ║        Createad by v1aas               ║
    ║                                        ║
    ║        https://t.me/v1aas              ║
    ║        https://github.com/v1aas        ║
    ║                                        ║
    ╚════════════════════════════════════════╝
    """
    print(business_card)
    