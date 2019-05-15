import os
import datetime
# IP server
IP_SERVER = '192.168.1.2/24'

# IP DEVICE
IP_DEVICE = '192.168.1.100'

# VENDOR ID
VENDOR_ID = '160987'

# TIME INTERVAL IN SECONDS
INTERVAL = 300

# VOLTAGE
U = 220

# FILES LOCATION
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = os.path.join(BASE_DIR, 'logs')

CONFIG_DIR = os.path.join(BASE_DIR, 'config')

# JSON FILE
JS_FILE = os.path.join(CONFIG_DIR, 'object_template.json')

LOG_NAME = os.path.join(LOG_DIR, f'{datetime.date.today()}.log')
JSON_NAME = os.path.join(BASE_DIR, 'CAPACITY_DATA.json')
