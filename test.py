#去重
accounts = open('from_wallet.txt','r').readlines()
file = open('去重.txt','a')
accounts = list(set(accounts))
for account in accounts:
    file.write(account)