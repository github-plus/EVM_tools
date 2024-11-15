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
    http_provider = 'https://rpc.ankr.com/celo'
    web3 = Web3(Web3.HTTPProvider(http_provider))

    # 获取发送者地址的余额
    balance_wei = web3.eth.get_balance(from_address)
    balance_eth = web3.from_wei(balance_wei, 'ether')

    # 获取当前钱包地址的 nonce 值
    nonce = web3.eth.get_transaction_count(from_address)

    '''以下数据要修改'''
    # 计算要转账的金额
    # amount_to_transfer = balance_wei / 1000
    amount_to_transfer = int(0.002 * 10 ** 18)
    # 获取当前 gas price
    # gas_price = web3.eth.gas_price    #动态获取当前gas_price_
    gas_price = web3.to_wei(0.000000008971106059, 'ether')    #固定gas_price
    gas = 150000          #设置每次转账要多少份gas

    '''以上数据要修改'''
    # 构建转账交易
    tx = {
        'nonce': nonce,
        'to': to_address,
        'value': int(amount_to_transfer),
        # 'gas': 21000 + random.randint(1, 10000),  # 设置 gas 限额
        'gas': gas,  # 设置 gas 限额
        'gasPrice': gas_price,  # 使用动态获取的 gas price
        'chainId': web3.eth.chain_id,   #自动获取chain_id
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
        logging.info("转账成功")
        return True
    else:
        logging.info("转账失败")
        return False

def handle(from_wallet, to_wallet, success_wallet):

    # 读取钱包文件和新账户文件的内容
    from_accounts = read_lines(from_wallet)
    to_accounts = read_lines(to_wallet)

    # 如果新账户列表为空，直接返回
    if not to_accounts:
        return

    total_to = len(to_accounts)
    total_from = len(from_accounts)
    sum = 0
    # 遍历 new_accounts 中的每个账户
    for to_account in to_accounts:
        logging.info(f"第{sum}/{total_to}个地址")
        to_address, to_key = to_account.strip().split(',')

        flag = True
        while flag:

            # 按顺序选择一个发送账户
            from_address, from_key = from_accounts[sum%total_from].strip().split(',')
            # 假设有一个名为 transfer_balance 的方法可以进行转账，返回转账是否成功的布尔值
            try:
                transfer_success = transfer_balance(from_address, to_address, from_key)
                # 如果转账成功，则将新账户信息写入 t.txt 文件
                if transfer_success:
                    write_line(success_wallet, f"{to_account}")
                flag = False
            except Exception as e:
                logging.info(e)
                logging.info(f'第{sum}地址转账失败,失败地址为{to_address},正在重新转账')

        sleep(2)

        sum += 1
    # 如果所有的新账户都被转账完毕，则可以在这里处理
    logging.info("所有新账户转账完成")



# 示例调用
from_wallet = "from_wallet.txt"
to_wallet = "to_wallet.txt"
success_wallet = "success_wallet.txt"
fail_wallet = 'fail_wallet.txt'
handle(from_wallet, to_wallet, success_wallet)
