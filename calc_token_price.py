def calc_token_price(token_reserves, sol_price=117.20):
    a = 2.17e-22
    b = -4.04e-13
    c = 0.0002283
    
    token_price_in_sol = a * token_reserves**2 + b * token_reserves + c
    token_price_in_usd = token_price_in_sol * sol_price
    
    return token_price_in_usd
