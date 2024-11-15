import random
from time import sleep
import json
import random

from web3 import Web3

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def read_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


def write_line(file_path, line):
    with open(file_path, 'a') as file:
        file.write(line)


def transfer_balance(from_address, to_address, from_key):
    # http_provider = 'https://rpc.ankr.com/celo'   #celo节点
    http_provider = 'https://bsc.publicnode.com'   #bsc节点
    web3 = Web3(Web3.HTTPProvider(http_provider))
    to_address = web3.to_checksum_address(to_address)

    # 获取当前钱包地址的 nonce 值
    nonce = web3.eth.get_transaction_count(from_address)

    '''以下数据要修改'''



    # 获取当前 gas price

    # gas_price = web3.eth.gas_price    #动态获取当前gas_price_
    # gas_price = web3.to_wei(0.001, 'ether')  # 固定gas_price,单位为bnb，例0.001bnb
    gas_price = web3.to_wei('1.02', 'gwei')    #BSC建议参数
    # gas_price = web3.to_wei('0.00101', 'gwei')   #opbnb建议参数


    gas = 21000  # 设置每次转账要多少份gas
    # 获取发送者地址的余额
    balance_wei = web3.eth.get_balance(from_address)    #单位为gwei,例5000000gwei
    balance_eth = web3.from_wei(balance_wei, 'ether')   # 单位转为非gwei，例500000000gwei转为0.05bnb

    # 计算要转账的金额
    amount_to_transfer = balance_wei - gas * gas_price   #归集所有余额
    #amount_to_transfer = int(0.002 * 10 ** 18)          #归集固定金额

    '''以上数据要修改'''
    # 构建转账交易
    tx = {
        'nonce': nonce,
        'to': to_address,
        'value': amount_to_transfer,
        # 'gas': 21000 + random.randint(1, 10000),  # 设置 gas 限额
        'gas': gas,  # 设置 gas 限额
        'gasPrice': gas_price,  # 使用动态获取的 gas price
        'chainId': web3.eth.chain_id,  # 自动获取chain_id
    }

    # 对交易进行签名
    signed_tx = web3.eth.account.sign_transaction(tx, from_key)
    logging.info(f"signed_tx: {signed_tx.rawTransaction.hex()}")

    # 发送已签名的交易
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    logging.info(f"tx_hash: {tx_hash.hex()}")

    # 等待交易被确认
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    logging.info(f"tx_receipt: {tx_receipt.status}")
    # 获取交易的状态
    if tx_receipt.status == 1:
        logging.info(f"转账成功，转账金额为{web3.from_wei(amount_to_transfer, 'ether') },剩余金额为{web3.from_wei(web3.eth.get_balance(from_address),'ether')}")
        return True,web3.from_wei(amount_to_transfer, 'ether')
    else:
        logging.info("转账失败")
        return False,0


def handle(from_wallet, to_address, fail_wallet):
    # 读取钱包文件和新账户文件的内容
    from_accounts = read_lines(from_wallet)

    total_from = len(from_accounts)
    sum = 0
    balance = 0
    # 遍历 new_accounts 中的每个账户
    for from_account in from_accounts:
        logging.info(f"第{sum}/{total_from}个地址")
        # to_address, to_key = from_account.strip().split(',')

        # 按顺序选择一个发送账户
        from_address, from_key = from_account.strip().split(',')
        # 假设有一个名为 transfer_balance 的方法可以进行转账，返回转账是否成功的布尔值
        try:
            transfer_success,num = transfer_balance(from_address, to_address, from_key)
            # 如果转账成功，则将新账户信息写入 t.txt 文件
            if transfer_success:
                balance += num

            else:
                write_line(fail_wallet,from_account)

        except Exception as e:
            logging.info(e)
        logging.info(f'归集总金额为{balance}')


        sum += 1
    # 如果所有的新账户都被转账完毕，则可以在这里处理
    logging.info("所有新账户转账完成")


# 示例调用
from_wallet = "from_wallet.txt"
to_address = ""    #归集地址
fail_wallet = 'fail_wallet.txt'
handle(from_wallet, to_address, fail_wallet)
