import struct
from config import payer_keypair, client
from constants import *
from solana.rpc.types import TokenAccountOpts, TxOpts
from solana.transaction import AccountMeta
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price  # type: ignore
from solders.instruction import Instruction  # type: ignore
from solders.message import MessageV0  # type: ignore
from solders.pubkey import Pubkey  # type: ignore
from solders.transaction import VersionedTransaction  # type: ignore
from spl.token.instructions import create_associated_token_account, get_associated_token_address
from utils import confirm_txn, get_token_balance, get_bonding_curve_accounts

def buy(mint_str, sol_in=0.1):
    # Function to execute a buy transaction using a bonding curve
    
    # Fetch bonding curve accounts
    print("Fetching bonding curve accounts info...")
    bonding_curve_accounts = get_bonding_curve_accounts(mint_str)
    if not bonding_curve_accounts:
        # Exit if accounts cannot be fetched
        print("Failed to fetch bonding curve accounts...")
        return
    
    # Unpack the bonding curve accounts
    curve_state, curve_mint_ata = bonding_curve_accounts
    user = payer_keypair.pubkey()
    mint = Pubkey.from_string(mint_str)
    user_mint_ata, token_account_instructions = None, None

    try:
        # Try to get user's token account associated with the mint
        account_data = client.get_token_accounts_by_owner(user, TokenAccountOpts(mint))
        user_mint_ata = account_data.value[0].pubkey
        token_account_instructions = None
    except:
        # Create associated token account if it doesn't exist
        user_mint_ata = get_associated_token_address(user, mint)
        token_account_instructions = create_associated_token_account(user, user, mint)

    # Calculate the exact amount of SOL in lamports
    exact_sol_in = int(sol_in * LAMPORTS_PER_SOL)

    # Build the list of accounts involved in the transaction
    keys = [
        AccountMeta(pubkey=user, is_signer=True, is_writable=True),
        AccountMeta(pubkey=main_state, is_signer=False, is_writable=True),
        AccountMeta(pubkey=curve_state, is_signer=False, is_writable=True),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=user_mint_ata, is_signer=False, is_writable=True),
        AccountMeta(pubkey=curve_mint_ata, is_signer=False, is_writable=True),
        AccountMeta(pubkey=treasury, is_signer=False, is_writable=True),
        AccountMeta(pubkey=referrer, is_signer=False, is_writable=True),
        AccountMeta(pubkey=system_program, is_signer=False, is_writable=False),
        AccountMeta(pubkey=token_program, is_signer=False, is_writable=False),
        AccountMeta(pubkey=associated_token_program, is_signer=False, is_writable=False),
        AccountMeta(pubkey=event_authority, is_signer=False, is_writable=False),
        AccountMeta(pubkey=program, is_signer=False, is_writable=False)
    ]

    # Define integer values for the instruction data
    instruction_code = 9427741683329488989
    integers = [
        instruction_code,
        exact_sol_in,
        0
    ]
    
    # Pack the integers into binary segments for the instruction data
    binary_segments = [struct.pack('<Q', integer) for integer in integers]
    data = b''.join(binary_segments)  
    swap_instruction = Instruction(program, data, keys)

    # Create the list of transaction instructions
    instructions = []
    instructions.append(set_compute_unit_price(UNIT_PRICE))
    instructions.append(set_compute_unit_limit(UNIT_BUDGET))
    if token_account_instructions:
        instructions.append(token_account_instructions)
    instructions.append(swap_instruction)

    # Compile the message for the transaction
    compiled_message = MessageV0.try_compile(
        payer_keypair.pubkey(),
        instructions,
        [],  
        client.get_latest_blockhash().value.blockhash,
    )

    # Create and send the transaction
    transaction = VersionedTransaction(compiled_message, [payer_keypair])
    txn_sig = client.send_transaction(transaction, opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed")).value
    print(txn_sig)
    
    # Confirm the transaction and print the result
    confirm = confirm_txn(txn_sig)
    print(confirm)

def sell(mint_str, token_balance=None):
    # Function to execute a sell transaction using a bonding curve

    # Fetch bonding curve accounts
    print("Fetching bonding curve accounts...")
    bonding_curve_accounts = get_bonding_curve_accounts(mint_str)
    if not bonding_curve_accounts:
        # Exit if accounts cannot be fetched
        print("Failed to fetch bonding curve accounts...")
        return
    
    # Unpack the bonding curve accounts
    curve_state, curve_mint_ata = bonding_curve_accounts
    
    user = payer_keypair.pubkey()
    mint = Pubkey.from_string(mint_str)

    # Calculate the user's associated token account address
    user_mint_ata = get_associated_token_address(user, mint)

    # Calculate token balance and minimum SOL output
    if token_balance is None:
        token_balance = get_token_balance(mint_str)
    
    print("Token Balance:", token_balance)    
    
    if token_balance == 0:
        # Exit if token balance is zero
        print("Zero tokens.")
        return
    
    # Convert token balance to the appropriate unit
    amount_in = int(token_balance * 10**6)
    
    # Build the list of accounts involved in the transaction
    keys = [
        AccountMeta(pubkey=user, is_signer=True, is_writable=True),
        AccountMeta(pubkey=main_state, is_signer=False, is_writable=True),
        AccountMeta(pubkey=curve_state, is_signer=False, is_writable=True),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=user_mint_ata, is_signer=False, is_writable=True),
        AccountMeta(pubkey=curve_mint_ata, is_signer=False, is_writable=True),
        AccountMeta(pubkey=treasury, is_signer=False, is_writable=True),
        AccountMeta(pubkey=referrer, is_signer=False, is_writable=True),
        AccountMeta(pubkey=system_program, is_signer=False, is_writable=False),
        AccountMeta(pubkey=token_program, is_signer=False, is_writable=False),
        AccountMeta(pubkey=associated_token_program, is_signer=False, is_writable=False),
        AccountMeta(pubkey=event_authority, is_signer=False, is_writable=False),
        AccountMeta(pubkey=program, is_signer=False, is_writable=False)
    ]
    
    # Define integer values for the instruction data
    sell = 11439165946368031069
    integers = [
        sell,
        amount_in,
        0
    ]

    # Pack the integers into binary segments for the instruction data
    binary_segments = [struct.pack('<Q', integer) for integer in integers]
    data = b''.join(binary_segments)  
    swap_instruction = Instruction(program, data, keys)

    # Create the list of transaction instructions
    instructions = []
    instructions.append(set_compute_unit_price(UNIT_PRICE))
    instructions.append(set_compute_unit_limit(UNIT_BUDGET))
    instructions.append(swap_instruction)

    # Compile the message for the transaction
    compiled_message = MessageV0.try_compile(
        payer_keypair.pubkey(),
        instructions,
        [],
        client.get_latest_blockhash().value.blockhash,
    )

    # Create and send the transaction
    transaction = VersionedTransaction(compiled_message, [payer_keypair])
    txn_sig = client.send_transaction(transaction, opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed")).value
    print(txn_sig)
    
    # Confirm the transaction and print the result
    confirm = confirm_txn(txn_sig)
    print(confirm)
