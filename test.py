import requests


key='29739b00f42ed462a2a850e5c34c03d9e65ae652'
response = requests.get(f'https://api.nomics.com/v1/markets?key={key}')

print(response.text)