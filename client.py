from web3 import Web3

class Client:
    def __init__(
            self,
            web3: Web3,
            private_key: str
    ):
        self.web3 = web3
        self.private_key = private_key
        self.address = self.web3.eth.account.from_key(private_key).address
