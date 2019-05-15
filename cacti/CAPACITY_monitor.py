import json
import sys
import os
from logging.handlers import TimedRotatingFileHandler
import logging
import os
import datetime

# CONFIG ==============================
# JSON FILE LOCATION
JS_VALUE_FILE = r'/var/www/html/cacti/scripts/CAPACITY_DATA.json'

# LOG FILE LOCATION
LOG_FILE = rf'/tmp/EXIM_{datetime.date.today()}.log'
# =====================================

# LOG =================================
def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    log_file = os.path.join(LOG_FILE)
    timehandler = TimedRotatingFileHandler(
        log_file, when='midnight', backupCount=10)
    formatter = logging.Formatter(
        "[%(levelname)s][ %(asctime)s][%(name)s - %(funcName)s] "
        "- %(lineno)d: %(message)s")
    timehandler.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(timehandler)
    # with this pattern,
    # it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger

logger = get_logger(__name__)

# PROCESS THE VALUE OF JS_FILE ======
def return_capacity_value(js_file, cabinet):
    tmp_list = []
    fin_list = []
    js_data = json.load(open(js_file))
    try:
        for val_dict in js_data:
            for key, val in val_dict.items():
                for tmp in val:
                    pdu_name = str(list(tmp.keys())[0])
                    capacity = f'{(float(list(tmp.values())[0]) / 1000):0.2f}'
                    tmp_list.append([pdu_name, capacity])
                fin_list.append([key, tmp_list[:]])
                tmp_list.clear()
    except Exception as e:
        logger.error(f'Unable to process value from {js_file} - {e}')
        return 'NaN'

    res = ''
    try:
        for i in fin_list:
            if cabinet == i[0]:
                for a in i[1]:
                    # a[0] = PDU NAME
                    # a[1] = CAPACITY VALUE
                    res = res + f'{a[0]}:{a[1]} '
                break
    except Exception as e:
        logger.error(f'Unable to search for value - {e}')
        return 'NaN'
    else:
        if res != '':
            logger.info(f'{cabinet}: {res}')
            return res[:-1]
        else:
            logger.error(f'Unable to search {cabinet} in {js_file}')
            return 'NaN'


if __name__ == "__main__":
    # CALL FUCNTION
    try:
        # Init value
        cabinet = sys.argv[1]
        val = return_capacity_value(JS_VALUE_FILE, cabinet)
    except Exception as e:
        logger.error(f'Missing "cabinet" argument - {e}')
        val = 'Nan'
    finally:
        print(val)
