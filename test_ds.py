from descubrimiento import DS_connection
from generales import *


obj = DS_connection(server_url, server_port)
obj.connect_to_server()

# data = obj.list_users()
# data = obj.query('mam')
data = obj.register('mam', '127.0.0.1', 9999, 'password', 'V0')
# data = obj.quit()

print(data)
