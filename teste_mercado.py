import yfinance as yf

# Vamos testar com uma ação ou FII (lembre-se do .SA para ativos brasileiros)
ativo = "IVVB11.SA" 

print(f"Buscando dados de {ativo}...")
dados = yf.Ticker(ativo)
preco_atual = dados.fast_info['last_price']

print(f"O preço atual de {ativo} é: R$ {preco_atual:.2f}")