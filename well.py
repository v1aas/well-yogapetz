import requests
import time
import asyncio
import random
from loguru import logger
from client import Client
from fake_useragent import UserAgent
from manager_db import DatabaseManager
from better_automation.twitter import TwitterAccount, TwitterClient
from better_automation.utils import set_windows_selector_event_loop_policy
from well_web3 import connect_wallet, claim_daily_insight, claim_rank_insights, save_results, mint_ai_nft, check_balance, WEB3
from utilities import get_invite, save_errors, save_invite, get_keys, get_proxy, get_tokens, get_tokens_change, random_sleep, to_proxy_format

set_windows_selector_event_loop_policy()
db_manager = DatabaseManager()
db_manager.connect()
user_agent = UserAgent()

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
    response_for_google = requests.post("https://www.googleapis.com/identitytoolkit/v3/relyingparty/createAuthUri?key=AIzaSyBPmETcQFfpDrw_eB6s8DCkDpYYBt3e8Wg", json=json, headers=headers_for_login, proxies=to_proxy_format(proxy))
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
            response = requests.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key=AIzaSyBPmETcQFfpDrw_eB6s8DCkDpYYBt3e8Wg", json=json, proxies=to_proxy_format(proxy))
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
                'User-Agent': user_agent.random
            }
            json = {
                "oauth":{
                    "oauthAccessToken": oauth_access_token,
                    "oauthTokenSecret": oauth_token_secret
                }
            }
            response = requests.post("https://api.gm.io/ygpz/link-twitter", headers=headers_for_login, json=json, proxies=to_proxy_format(proxy))
            if response.status_code == 200:
                logger.success("Твиттер успешно привязан")
            else:
                logger.error(f"Ошибка при привязке твиттера. {response.status_code}. {response.text}")
            response = requests.post("https://api.gm.io/ygpz/enter-referral-code", headers=headers_for_login, json={"code":invite}, proxies=to_proxy_format(proxy))
            if response.status_code == 200:
                logger.success(f"Инвайт {invite} успешно привязан")
            else:
                logger.error(f"Ошибка при привязке инвайта. {response.status_code}. {response.text}")
            response = requests.post("https://api.gm.io/ygpz/generate-codes", headers=headers_for_login, json={}, proxies=to_proxy_format(proxy))
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
        response_for_google = requests.post("https://www.googleapis.com/identitytoolkit/v3/relyingparty/createAuthUri?key=AIzaSyBPmETcQFfpDrw_eB6s8DCkDpYYBt3e8Wg", json=json, headers=headers_for_login, proxies=to_proxy_format(proxy))
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
            response = requests.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key=AIzaSyBPmETcQFfpDrw_eB6s8DCkDpYYBt3e8Wg", json=json, proxies=to_proxy_format(proxy))
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
                'User-Agent': user_agent.random
            }
            json = {
                "oauth":{
                    "oauthAccessToken": oauth_access_token,
                    "oauthTokenSecret": oauth_token_secret
                }
            }
            response = requests.post("https://api.gm.io/ygpz/link-twitter", headers=headers_for_login, json=json, proxies=to_proxy_format(proxy))
            if response.status_code == 200:
                logger.success("Твиттер успешно привязан")
            else:
                logger.error(f"Ошибка при привязке твиттера. {response.status_code}. {response.text}")
            return headers_for_login
    except UnboundLocalError as e:
        logger.error(f"Ошибка - login_twitter. {e}")
        save_errors(f"Ошибка - login_twitter. {e}")
        return None
    except AttributeError as e:
        logger.error(f"Аккаунт заблокирован или поймал капчу. {token}")
        save_errors(f"Аккаунт заблокирован или поймал капчу. {token}")
        return None
    except Exception as e:
        logger.error(f"Ошибка - login_twitter. {e}")
        save_errors(f"Ошибка - login_twitter. {e}")
        return None
        
async def update_invites():
    proxys = get_proxy()
    for acc in db_manager.get_accounts():
        proxy = next(proxys)
        headers = await get_headers(acc[0], proxy)
        if headers is None:
            continue
        response = requests.post("https://api.gm.io/ygpz/generate-codes", headers=headers, json={}, proxies=to_proxy_format(proxy))
        if response.status_code == 200:
            logger.success(f"Инвайты успешно созданы")
        else:
            logger.error(f"Ошибка при создании инвайтов. {response.status_code}. {response.text}")
        response = requests.get("https://api.gm.io/ygpz/me", headers=headers, proxies=to_proxy_format(proxy))
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

def get_num_daily_tweet(headers_for_login, proxy):
    response = requests.get("https://api.gm.io/ygpz/me", headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        daily = response.json()['contractInfo']['dailyQuest']['nonce'].split('-')
        return list(daily)[2]
    else:
        logger.error("Ошибка при получении номера дейли квеста")

def is_mint_daily_ai_nft(headers_for_login, proxy):
    response = requests.get("https://api.gm.io/ygpz/me", headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        daily = response.json()['contractInfo']['dailyQuest']['nonce'].split('-')
        num = list(daily)[2]
        raw_daily = response.json()['ygpzQuesting']['rawDailyProgress']
        if f'{num}-mint-daily-well3nft' in raw_daily:
            logger.success("AI нфт уже заминчена!")
            return True, 0
        else:
            return False, num
    else:
        logger.error("Ошибка при проверке минта AI нфт")
        return True, 0
   
def get_uncomplete_tasks(headers_for_login, proxy):
    tasks = []
    response = requests.get("https://api.gm.io/ygpz/me", headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        raw_tasks = response.json()['ygpzQuesting']['rawSpecialProgress']
        if 'retweet-yogapetz-1756009723122643349' not in raw_tasks:
            tasks.append(like_retweet3)
            logger.info("Задание лайк+ретвит#3 был не выполнено")
        if 'retweet-yogapetz-1750523880463340019' not in raw_tasks:
            tasks.append(like_retweet2)
            logger.info("Задание лайк+ретвит#2 было не выполнено")
        if 'retweet-yogapetz-1745127428039847937' not in raw_tasks:
            tasks.append(like_retweet)
            logger.info("Задание лайк+ретвит#1 было не выполнено")
        if 'set-well-twitter-profile-banner' not in raw_tasks:
            tasks.append(set_banner)
            logger.info("Задание с баннером не выполнено")
        if 'retweet-yogapetz-1752693511433093285' not in raw_tasks:
            tasks.append(like_retweet4)
            logger.info("Задание лайк+ретвит#4 было не выполнено")
        if 'retweet-yogapetz-1755646539610157102' not in raw_tasks:
            tasks.append(like_retweet5)
            logger.info("Задание лайк+ретвит#5 было не выполнено")
        return tasks
    else:
        logger.error("Ошибка при проверки заданий")

def complete_breath_session(headers_for_login, proxy):
    response = requests.post("https://api.gm.io/ygpz/complete-breath-session", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.success("Клейм за ежедневную метидацию успешен!")
    elif response.status_code == 400:
        return
    else:
        logger.error(f"Ошибка при клейме ежедневной метидации. {response.status_code}. {response.text}")

async def post_daily_tweet(token, headers_for_login, proxy):
    try:
        num = get_num_daily_tweet(headers_for_login, proxy)
        response = requests.post(f"https://api.gm.io/ygpz/claim-exp/{num}-post-daily-yoga-photo", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
        if response.status_code == 400:
            return
        if response.status_code == 200:
            logger.success("Клейм за ежедневый твит успешен!")
        else:
            logger.error(f"Ошибка при клейме ежедневый твит. {response.status_code}. {response.text}")
    except Exception as e:
        logger.error(f"Ошибка - post_daily_tweet|{e}|{token}")
        save_errors(f"Ошибка - post_daily_tweet|{e}|{token}")
    
def set_banner(headers_for_login, proxy):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/set-well-twitter-profile-banner", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.success("Клейм за баннер успешен!")
    else:
        logger.error(f"Ошибка при за баннер. {response.status_code}. {response.text}")
    
def like_retweet(headers_for_login, proxy):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/retweet-yogapetz-1745127428039847937", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.success("Клейм за лайк+ретвит #1 успешен!")
    else:
        logger.error(f"Ошибка при за лайк+ретвит #1. {response.status_code}. {response.text}")
    
def like_retweet2(headers_for_login, proxy):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/retweet-yogapetz-1750523880463340019", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.success("Клейм за лайк+ретвит #2 успешен!")
    else:
        logger.error(f"Ошибка при за лайк+ретвит #2. {response.status_code}. {response.text}")
    
def like_retweet3(headers_for_login, proxy):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/retweet-yogapetz-1756009723122643349", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.success("Клейм за лайк+ретвит #3 успешен!")
    else:
        logger.error(f"Ошибка при за лайк+ретвит #3. {response.status_code}. {response.text}")
    
def like_retweet4(headers_for_login, proxy):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/retweet-yogapetz-1752693511433093285", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.success("Клейм за лайк+ретвит #4 успешен!")
    else:
        logger.error(f"Ошибка при за лайк+ретвит #4. {response.status_code}. {response.text}")
    
def like_retweet5(headers_for_login, proxy):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/retweet-yogapetz-1755646539610157102", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.success("Клейм за лайк+ретвит #4 успешен!")
    else:
        logger.error(f"Клейм за лайк+ретвит #5 успешен!. {response.status_code}. {response.text}")
    
def follows(headers_for_login, proxy):
    response = requests.post("https://api.gm.io/ygpz/claim-exp/follow-yogapetz", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.success("Клейм за подписку #1 успешен!")
    else:
        logger.error(f"Ошибка при за подписку #1. {response.status_code}. {response.text}")
    time.sleep(random.randrange(3,5))
    response = requests.post("https://api.gm.io/ygpz/claim-exp/follow-keung", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.success("Клейм за подписку #2 успешен!")
    else:
        logger.error(f"Ошибка при за подписку #2. {response.status_code}. {response.text}")
    time.sleep(random.randrange(3,5))
    response = requests.post("https://api.gm.io/ygpz/claim-exp/follow-gmio", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.success("Клейм за подписку #3 успешен!")
    else:
        logger.error(f"Ошибка при за подписку #2. {response.status_code}. {response.text}")

def claim_daily_nft(headers_for_login, proxy, client):
    if not check_balance(client):
        logger.error("На этом кошельке нет баланса")
        return
    is_mint, num = is_mint_daily_ai_nft(headers_for_login, proxy)
    if not is_mint:
        mint_ai_nft(client)
        response = requests.post(f"https://api.gm.io/ygpz/claim-exp/{num}-mint-daily-well3nft", json={}, headers=headers_for_login, proxies=to_proxy_format(proxy))
        if response.status_code == 200:
            logger.success("Клейм за AI нфт успешен!")
        else:
            logger.error(f"Ошибка при клейме AI нфт. {response.status_code}. {response.text}")

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
            is_connect = connect_wallet(headers_for_login, client, proxy)
            if is_connect:
                db_manager.save_account(token, client.private_key)
            else:
                save_errors(f"Ошибка при привязке кошелька: {token};{client.address}")
            TASKS = [
                (complete_breath_session, [headers_for_login, proxy]),
                (post_daily_tweet, [token, headers_for_login, proxy]),
                (set_banner, [headers_for_login, proxy]),
                (like_retweet, [headers_for_login, proxy]),
                (like_retweet2, [headers_for_login, proxy]),
                (like_retweet3, [headers_for_login, proxy]),
                (like_retweet4, [headers_for_login, proxy]),
                (like_retweet5, [headers_for_login, proxy]),
                (follows, [headers_for_login, proxy])
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
    except AttributeError as e:
        logger.error(f"Аккаунт заблокирован или поймал капчу. {token}")
        save_errors(f"Аккаунт заблокирован или поймал капчу. {token}")
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

async def complete_daily_tasks():
    try:
        proxys = get_proxy()
        accounts = db_manager.get_accounts()
        for index, acc in enumerate(accounts, start=1):
            proxy = next(proxys)
            token = acc[0]
            key = acc[1]
            logger.info(f"Начинаю выполнять дневные задания. {index}/{len(accounts)} {token}")
            headers_for_login = await get_headers(token, proxy)
            if headers_for_login is None:
                continue
            TASKS = [
                (complete_breath_session, [headers_for_login, proxy]),
                (post_daily_tweet, [token, headers_for_login, proxy])
            ]
            for task, args in TASKS:
                if asyncio.iscoroutinefunction(task):
                    await task(*args)
                else:
                    task(*args)
                random_sleep()
            logger.success(f"Все задания выполнены. {token}")
            claim_daily_insight(headers_for_login, Client(WEB3, key), proxy)
            claim_daily_nft(headers_for_login, proxy, Client(WEB3, key))
    except AttributeError as e:
        logger.error(f"Аккаунт заблокирован или поймал капчу. {token}")
        save_errors(f"Аккаунт заблокирован или поймал капчу. {token}")
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

async def check_and_complete_tasks():
    try:
        proxys = get_proxy()
        accounts = db_manager.get_accounts()
        for index, acc in enumerate(accounts, start=1):
            proxy = next(proxys)
            token = acc[0]
            logger.info(f"Начинаю проверку выполненных заданий. {index}/{len(accounts)} {token}")
            headers_for_login = await get_headers(token, proxy)
            if headers_for_login is None:
                continue
            uncomplete_tasks = get_uncomplete_tasks(headers_for_login, proxy)
            if len(uncomplete_tasks) == 0:
                logger.success(f"Все задания выполнены. {token}")
                continue
            else:
                for task in uncomplete_tasks:
                    if asyncio.iscoroutinefunction(task):
                        await task(headers_for_login, proxy)
                    else:
                        task(headers_for_login, proxy)
                    random_sleep()
            logger.success(f"Все задания выполнены. {token}")
    except AttributeError as e:
        logger.error(f"Аккаунт заблокирован или поймал капчу. {token}")
        save_errors(f"Аккаунт заблокирован или поймал капчу. {token}")
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
    for acc in db_manager.get_accounts():
        proxy = next(proxys)
        token = acc[0]
        key = acc[1]
        headers_for_login = await get_headers(token, proxy)
        if headers_for_login is None:
            continue
        logger.info(f"Начинаю выполнять клеймить книжки. {token}")
        claim_rank_insights(headers_for_login, Client(WEB3, key), proxy)

def update_token():
    old_token = input("Введите старый токен: ")
    print("")
    new_token = input("Введите новый токен: ")
    db_manager.update_token(old_token, new_token)

def update_batch_token():
    change_tokens = get_tokens_change()
    for tokens in change_tokens:
        token = tokens.split(';')
        db_manager.update_token(token[0], token[1])

def delete_accout():
    old_token = input("Введите старый токен: ")
    db_manager.delete_accout(old_token)
    