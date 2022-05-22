import requests

url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
secret_token = 'AQAAAAABk-QnAAYckfT6FI_nFELOsm5CUpYrUSg'
start_time = '1653235876' #'1640995200'

headers = {'Authorization': f'OAuth {secret_token}'}
payload = {'from_date': start_time}

# Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
homework_statuses = requests.get(url, headers=headers, params=payload)

# Печатаем ответ API в формате JSON
print(homework_statuses.text)

# А можно ответ в формате JSON привести к типам данных Python и напечатать и его
#print(homework_statuses.json())






