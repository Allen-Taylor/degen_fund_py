# degen_fund_py

Clone the repo, and add your Public Key (wallet), Private Key and RPC to the Config.py.

### Contact

My services are for **hire**. Contact me if you need help integrating the code into your own project. 

Telegram: Allen_A_Taylor (AL THE BOT FATHER)

### Example

```
from degen_fund import buy

#DEGEN FUND MINT ADDRESS (NOT RAYDIUM)
mint_str = "token_to_buy"

#BUY
buy(mint_str, .1)
```
```
from degen_fund import sell
from utils import get_token_balance

#DEGEN FUND MINT ADDRESS (NOT RAYDIUM)
mint_str = "token_to_sell"

#SELL
token_balance = get_token_balance(mint_str)
sell(mint_str, token_balance)
```
