
import json
import random

import requests
from web3 import Web3
from eth_account import Account, messages
import logging
from faker import Faker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def read_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


def write_line(file_path, line):
    with open(file_path, 'a') as file:
        file.write(line)



def block(address,key):
    http_provider = 'https://rpc.ankr.com/celo'
    web3 = Web3(Web3.HTTPProvider(http_provider))
    address = web3.to_checksum_address(address)
    nonce = web3.eth.get_transaction_count(address)
    print(f'{address}-----{key}')


    '''以下数据要改'''
    to = '0x12781d368A416aC970F6c6b125d6Ac47dF64002a'  # 合约交互地址，视具体项目而定
    # 交互data
    data = f'0x84bb1e42000000000000000000000000{address[2:]}0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    gas_price = web3.to_wei(0.000000008971106059, 'ether')  # 每份汽油的价格
    gas = 150000  # 需要多少分汽油，最终fee = gas * gas_price
    chainId = 42220
    '''以上数据要改'''
    transaction = {
        'to': to,
        'from': address,
        'data': data,
        'gasPrice': gas_price,
        'gas': gas,
        'nonce': nonce,
        'chainId': chainId,
    }

    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key=key)
    # 发送交易
    try:

        transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

        logging.info(f"tx_hash: {transaction_hash.hex()}")
        # 等待交易被确认
        tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
        logging.info(f"tx_receipt: {tx_receipt.status}")
        # 获取交易的状态
        if tx_receipt.status == 1:
            logging.info("转账成功")
            return True
        else:
            logging.info("转账失败")
            return False

    except Exception as e:
        logging.info(e)


def handle(file,success_contract_wallet):
    accounts = read_lines(file)

    total = len(accounts)
    sum = 1
    for i in range(0,total):
        logging.info(f"第{sum}/{total}个地址")
        address, key = accounts[i].strip().split(',')
        flag = block(address, key)
        if flag:
            write_line(success_contract_wallet,accounts[i])
        sum += 1

file_name = 'celo.txt'
success_contract_wallet = 'success_contract_wallet.txt'
handle(file_name,success_contract_wallet)