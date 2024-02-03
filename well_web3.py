import time
import requests
import json
import random
from web3 import Web3
from client import Client
from loguru import logger
from manager_db import DatabaseManager
from eth_account.messages import encode_defunct
from web3.middleware import geth_poa_middleware
from utilities import to_proxy_format

with open('data/contract_abi.json', 'r') as file:
    ABI = json.load(file)

WEB3 = Web3(Web3.HTTPProvider("https://opbnb-mainnet-rpc.bnbchain.org"))
WEB3.middleware_onion.inject(geth_poa_middleware, layer=0)
insights_contract = WEB3.eth.contract(address=WEB3.to_checksum_address("0x73a0469348bcd7aaf70d9e34bbfa794def56081f"), abi=ABI)
db_manager = DatabaseManager()
db_manager.connect()

def check_balance(client: Client):
    client = Client(WEB3, client.private_key)
    balance = WEB3.from_wei(WEB3.eth.get_balance(client.address), 'ether')
    if balance == 0:
        return False
    else:
        return True

def get_eip1559_gas(web3):
    latest_block = web3.eth.get_block('latest')
    max_fee_priotiry_gas = web3.eth.max_priority_fee
    max_fee_per_gas = int(latest_block['baseFeePerGas']) + max_fee_priotiry_gas
    return max_fee_priotiry_gas, max_fee_per_gas

def connect_wallet(headers_for_login, client: Client, proxy):
    msg = f"Welcome to Yogapetz\nClick \"Sign\" to continue.\n\nTimestamp:\n{time.time()}"
    message = encode_defunct(text=msg)
    signed_message = client.web3.eth.account.sign_message(message, private_key=client.private_key)
    sign = signed_message.signature.hex()
    
    json = {
        "address": client.address,
        "signature": sign,
        "msg": msg
    }
    
    response = requests.post("https://api.gm.io/ygpz/link-wallet", json=json, headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.success("Кошелек успешно привязан!")
        return True
    else:
        logger.error(f"Ошибка при привязке кошелька. {response.status_code}. {response.text}")
        return False
        
def check_daily_insight(headers_for_login, proxy):
        response = requests.get("https://api.gm.io/ygpz/me", headers=headers_for_login, proxies=to_proxy_format(proxy))
        if response.status_code == 200:
            logger.info("Проверка дейли книжки успешна")
            daily_quest_nonce = response.json()['contractInfo']['dailyQuest']['nonce']
            signature = response.json()['contractInfo']['dailyQuest']['signature']
            used = insights_contract.functions.nonceUsed(daily_quest_nonce).call()
            return used, daily_quest_nonce, signature
        else:
            logger.error("Ошибка при проверке дейли книжки")
            return True, None, None

def claim_daily_insight(headers_for_login, client: Client, proxy):
    if not check_balance(client):
        logger.error("На этом кошельке нет баланса")
        return
    used, daily_quest_nonce, signature = check_daily_insight(headers_for_login, proxy)
    if used and daily_quest_nonce is not None and signature is not None:
        logger.error("Дейли книжка была заминчена или возникла ошибка!")
        return
    else:
        logger.info("Начинаю минтить дейли книжку")
    max_fee_priotiry_gas, max_fee_per_gas = get_eip1559_gas(client.web3)
    try:
        tx = insights_contract.functions.nonceQuest(
            daily_quest_nonce,
            signature
            ).build_transaction(
                {
                    'nonce': client.web3.eth.get_transaction_count(client.address),
                    'gas': 300000,
                    'maxPriorityFeePerGas': max_fee_priotiry_gas,
                    'maxFeePerGas': max_fee_per_gas,
                }
            )
        signed_txn = client.web3.eth.account.sign_transaction(tx, client.private_key)
        txn_hash = client.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f"Транзакция отправлена. Хэш: {txn_hash.hex()}")
        receipt = client.web3.eth.wait_for_transaction_receipt(txn_hash)
        if (receipt['status'] == 1):
            logger.success(f"Транзакция прошла успешно! Клейм дейли книжки успешен! {client.address}")
        else:
            logger.error(f"Ошибка. Статус: {receipt['status']}")
    except Exception as e:
        logger.error(f"Ошибка {e}")

def check_rank_insights(headers_for_login, client: Client, proxy):
    response = requests.get("https://api.gm.io/ygpz/me", headers=headers_for_login, proxies=to_proxy_format(proxy))
    if response.status_code == 200:
        logger.info("Проверка количества книжек успешна")
        current_rank = response.json()['contractInfo']['rankupQuest']['currentRank']
        signature = response.json()['contractInfo']['rankupQuest']['signature']
        quest_amount = insights_contract.functions.getQuests(current_rank, client.address).call()
        return current_rank, quest_amount, signature
    else:
        logger.error("Ошибка при проверке доступных книжек")
        return None, None, None
    
def claim_rank_insights(headers_for_login, client: Client, proxy):
    if not check_balance(client):
        logger.error("На этом кошельке нет баланса")
        return
    current_rank, quest_amount, signature = check_rank_insights(headers_for_login, client, proxy)
    if quest_amount is None or quest_amount == 0:
        logger.info(f"Доступных к минту книжек нет! {quest_amount}")
        return
    else:
        logger.info(f"Начинаю минтить книжки, доступно: {quest_amount}")
    max_fee_priotiry_gas, max_fee_per_gas = get_eip1559_gas(client.web3)
    try:
        tx = insights_contract.functions.rankupQuestAmount(
            current_rank,
            signature,
            quest_amount
            ).build_transaction(
                {
                    'nonce': client.web3.eth.get_transaction_count(client.address),
                    'gas': 300000,
                    'maxPriorityFeePerGas': max_fee_priotiry_gas,
                    'maxFeePerGas': max_fee_per_gas,
                }
            )
        signed_txn = client.web3.eth.account.sign_transaction(tx, client.private_key)
        txn_hash = client.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f"Транзакция отправлена. Хэш: {txn_hash.hex()}")
        receipt = client.web3.eth.wait_for_transaction_receipt(txn_hash)
        if (receipt['status'] == 1):
            logger.success(f"Транзакция прошла успешно! Клейм книжек успешен! {client.address}")
            sec = random.randint(30, 60)
            logger.info(f"Сплю {sec} перед следующим кошельком")
            time.sleep(sec)
        else:
            logger.error(f"Ошибка. Статус: {receipt['status']}")
    except Exception as e:
        logger.error(f"Ошибка {e}")

def save_results(client: Client):
    result = insights_contract.functions.questResults(client.address).call()
    uncommon = result[0]
    rare = result[1]
    legendary = result[2]
    mythical = result[3]
    db_manager.save_books(client.private_key, uncommon, rare, legendary, mythical)
