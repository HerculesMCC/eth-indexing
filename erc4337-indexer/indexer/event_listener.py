from web3 import Web3
from web3.middleware import geth_poa_middleware
from config import Config
from .models import Session, UserOperation
import time

class EventListener:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(Config.INFURA_URL))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Vérification du réseau
        network_id = self.w3.eth.chain_id
        print(f"Connected to network ID: {network_id}")  # 1 pour Mainnet
        
        # Vérification du bloc actuel
        current_block = self.w3.eth.block_number
        print(f"Current block number: {current_block}")
        
        # Convertir l'adresse en format checksum
        checksum_address = Web3.to_checksum_address(Config.ENTRYPOINT_ADDRESS)
        print(f"Checking contract at address: {checksum_address}")
        
        # Vérifier si le contrat existe
        code = self.w3.eth.get_code(checksum_address)
        print(f"Contract code exists: {len(code) > 0}")
        print(f"Contract code length: {len(code)}")
        
        # ABI minimal pour l'événement UserOperationEvent
        self.abi = [{
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "internalType": "bytes32",
                    "name": "userOpHash",
                    "type": "bytes32"
                },
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "sender",
                    "type": "address"
                },
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "paymaster",
                    "type": "address"
                },
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "nonce",
                    "type": "uint256"
                },
                {
                    "indexed": False,
                    "internalType": "bool",
                    "name": "success",
                    "type": "bool"
                },
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "actualGasCost",
                    "type": "uint256"
                },
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "actualGasUsed",
                    "type": "uint256"
                }
            ],
            "name": "UserOperationEvent",
            "type": "event"
        }]

        self.contract = self.w3.eth.contract(
            address=checksum_address,
            abi=self.abi
        )

    def listen_to_events(self, from_block=None):
        if from_block is None:
            current_block = self.w3.eth.block_number
            from_block = current_block - 1000
            print(f"Current block: {current_block}")
            print(f"Starting from block: {from_block}")

        print(f"Using EntryPoint address: {self.contract.address}")
        
        # Ajout de "0x" au début du topic
        event_signature_hash = "0x" + self.w3.keccak(
            text="UserOperationEvent(bytes32,address,address,uint256,bool,uint256,uint256)"
        ).hex()
        print(f"Event signature hash: {event_signature_hash}")

        while True:
            try:
                current_block = self.w3.eth.block_number
                print(f"\nChecking blocks from {from_block} to {current_block}")
                
                logs = self.w3.eth.get_logs({
                    'fromBlock': from_block,
                    'toBlock': current_block,
                    'address': self.contract.address,
                    'topics': [event_signature_hash]
                })
                
                print(f"Number of logs found: {len(logs)}")
                
                if logs:
                    print("Log details:")
                    for log in logs:
                        print(f"\nLog block: {log['blockNumber']}")
                        decoded_log = self.contract.events.UserOperationEvent().process_log(log)
                        print(f"Decoded event: {decoded_log}")
                        self.process_event(decoded_log)
                
                from_block = current_block + 1
                time.sleep(Config.POLLING_INTERVAL)
                
            except Exception as e:
                print(f"Error in event listener: {e}")
                time.sleep(5)

    def process_event(self, event):
        session = Session()
        try:
            args = event['args']
            user_op = UserOperation(
                user_op_hash=args['userOpHash'].hex(),
                sender=args['sender'],
                paymaster=args['paymaster'],
                nonce=str(args['nonce']),
                success=args['success'],
                actual_gas_cost=args['actualGasCost'],
                actual_gas_used=args['actualGasUsed'],
                block_number=event['blockNumber'],
                timestamp=self.w3.eth.get_block(event['blockNumber'])['timestamp']
            )
            session.add(user_op)
            session.commit()
            print(f"Saved UserOperation: {user_op.user_op_hash}")
        except Exception as e:
            print(f"Error processing event: {e}")
            session.rollback()
        finally:
            session.close()