import BAC0
from config import config
import sys
import os
import time
import datetime
import subprocess
from logging.handlers import TimedRotatingFileHandler
import json
import re
import logging


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    log_file = os.path.join(config.LOG_DIR, 'bacnet.log')
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


def BACnet_init(ip_server):
    # Init BAC0
    try:
        bacnet = BAC0.lite(ip=ip_server)
    except Exception as e:
        logger.error(f'BACNET: Unable to init connect! - {e}')
        return -1, e
    else:
        return 0, bacnet


def Process_JSON_file(js_file):
    # Init value
    map_list = []
    tmp_list = []

    # Process JSON file
    try:
        js_data = json.load(open(js_file, 'r'))
        for k, v in js_data.items():
            for key, val in v.items():
                pdu_name = val["name"]
                tmp = f'("analogValue", {val["oid"]})'
                tmp_list.append([pdu_name, eval(tmp)])
            map_list.append([k, tmp_list[:]])
            tmp_list.clear()
            print(map_list)
    except Exception as e:
        logger.error(f'BACNET: Unable to load content from {js_file} - {e}')
        return -1, e
    else:
        return 0, map_list


def BACnet_get_value(ip_server, vendor_id, bacnet, myObjList):
    # Init value
    bacnet_list = []
    tmp_list = []
    tmp_obj = []

    # Check BACnet connect
    if bacnet[0] == 0:
        bacnet_connect = bacnet[1]
    else:
        return -1, 'N/A'

    # Check myObjectList
    if myObjList[0] == 0:
        myObj = myObjList[1]
    else:
        return -1, 'N/A'

    # Get value
    try:
        # Process myObjList
        for i in myObj:
            for j in i[1]:
                # Init value
                tmp_obj.append(j[1])

                # Get value
                val = BAC0.device(
                    ip_server, vendor_id, bacnet_connect,
                    poll=0, object_list=tmp_obj)
                data = val.points
                tmp = re.match(r'.*: (.*?) .*', str(data[0]), re.I)
                ampere = float(tmp.group(1))
                tmp_list.append({j[0]: ampere})
                tmp_obj.clear()
            bacnet_list.append({i[0]: tmp_list[:]})
            tmp_list.clear()
    except Exception as e:
        logger.error(f'BACNET: Unable to get value! - {e}')
        return -1, e
    else:
        return 0, bacnet_list


def calculate_value(bacnet_value):
    # Check bacnet_value
    if bacnet_value[0] == 0:
        amperes_list = bacnet_value[1]
    else:
        logger.error(f'BACNET: Input error!')
        return -1, 'N/A'

    # Process value
    for i in amperes_list:
        for key, val in i.items():
            for tmp in val:
                try:
                    key = list(tmp.keys())[0]
                    ampere = list(tmp.values())[0]
                    capacity = f'{(ampere * config.U):0.2f}'
                    # Only change ampare value to capacity value
                    tmp[key] = capacity
                except Exception as e:
                    logger.error(f'BACNET: Unable to get ampare value! - {e}')
                    # IF value error, set it == 0
                    capacity = 0
                    continue
    return 0, amperes_list


def create_log(amperes_list, filename, mode, time_now=None):
    # Check amperes_list
    if amperes_list[0] == 0:
        capacity_val = amperes_list[1]
    else:
        capacity_val = []

    # Make log file
    if mode == "jsn":
        try:
            with open(filename, 'w+') as jsn:
                json.dump(capacity_val[:], jsn, indent=4)
        except Exception as e:
            logger.error(f'JSON FILE: Unable to write JSON file! - {e}')
    elif mode == "lg":
        try:
            with open(filename, 'a+') as lg:
                lg.write('===========================\n')
                lg.write(f'[{time_now}] ')
                json.dump(capacity_val[:], lg)
                lg.write('\n')
        except Exception as e:
            logger.error(f'LOG FILE: Unable to write LOG file! - {e}')


def main():
    # Init connect
    bacnet = BACnet_init(config.IP_SERVER)

    # Make VNDT GREAT AGAIN
    while True:
        # Init value
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Load JSON file
        js_file = Process_JSON_file(config.JS_FILE)

        # Get ampare value
        bacnet_list = BACnet_get_value(
            ip_server=config.IP_DEVICE, vendor_id=config.VENDOR_ID,
            bacnet=bacnet, myObjList=js_file)

        # Calculate capacity value
        cal_val = calculate_value(bacnet_list)

        # Write to log
        # JSON file
        create_log(
            amperes_list=cal_val, filename=config.JSON_NAME,
            mode="jsn")

        # Log file
        create_log(
            amperes_list=cal_val, filename=config.LOG_NAME,
            mode="lg", time_now=time_now)

        # Sleep INTERVAL minutes
        time.sleep(config.INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exit!")
    except Exception as e:
        logger.error(f'Unable to start APP! - {e}')
