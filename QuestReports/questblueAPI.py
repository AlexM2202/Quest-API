"""
This library is intended to make curl request to the QuestBlue Api.
Created at HDTec Solutions by Alex Marquardt on 17 May, 2023

Intended for in house use. For questions contact Alex.
"""

import csv
import datetime
import logging
import os
import threading
import time
from datetime import date
from multiprocessing import Queue
from pathlib import Path

import requests

import QuestReports.__main__ as main
import QuestReports.config as config


#Init sets global variables like username, password, and api key.
#Call this function first before anything else
def init(username: str, password: str, key:str):
    
    global user
    global secret
    global api_key
    global csvFirstTime

    csvFirstTime = True

    user = username
    secret = password
    api_key = key

def startLog():
    global log
    global logFile
    logFP = os.getcwd()
    logFile = str(f"{logFP}\\logs\\questLog.log")
    log = open(os.path.join(logFP, logFile), "w")
    logging.basicConfig(filename=os.path.join(logFP,logFile), level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%H:%M:%S", filemode='a')

def startCSV(mode: str, name=None):
    global sheet
    global sheetFile
    global sheetFileOpened
    
    if name == None:
        fname = date.today()
    else:
        fname = name
    
    if mode == 'endMon':
        sheetFP = os.getcwd()
        sheetFile = f"{sheetFP}\\outputs\\endMon\\{fname}-outputSheet.csv"
        sheetFileOpened = open(os.path.join(sheetFP, sheetFile), "w")
        sheet = csv.writer(sheetFileOpened)
        # sheet.writerow(['Trunk', 'Inbound Calls', 'Inbound Min', 'Outbound Calls', 'Outbound Min', 'Inbound TF Calls', 'Inbound TF Min', 'Outbound TF Calls', 'Outbound TF Min'])
        sheet.writerow(['Trunk', 'Inbound Calls', 'Inbound Min', 'Outbound Calls', 'Outbound Min', 'Inbound TF Calls', 'Inbound TF Min', 'Outbound TF Calls', 'Outbound TF Min'])
        
    if mode == 'tollFree':
        sheetFP = os.getcwd()
        sheetFile = f"{sheetFP}\\outputs\\tollFree\\{fname}-outputSheet.csv"
        sheetFileOpened = open(os.path.join(sheetFP, sheetFile), "w")
        sheet = csv.writer(sheetFileOpened)
        sheet.writerow(['Did', 'Inbound Min', 'Inbound Cost', 'Outbound Min', 'Outbound Cost'])
    
#Next section is the library of pull request functions

def __requestDids(page=int(1)):
    headers = {
        'Content-type': 'application/json',
        'Security-Key': api_key,
    }

    json_data = {
        'per_page': config.default_dids_per_page,
        'page': page,
    }

    global response
    response = requests.get(
        'https://api2.questblue.com/did',
        headers=headers,
        json=json_data,
        auth=(user, secret),
    )
    return response

def __requestDids_area_code(num=int(), page=int(1)):
    headers = {
        'Content-type': 'application/json',
        'Security-Key': api_key,
    }

    json_data = {
        'did': str(num)+'*',
        'per_page': config.default_dids_per_page,
        'page': page,
    }

    global response
    response = requests.get(
        'https://api2.questblue.com/did',
        headers=headers,
        json=json_data,
        auth=(user, secret),
    ).json()
    return response

def __internal_requestReports_num(num=int(), unix=int(time.time()), page=int(1), tryNum = 1):
    now = unix
    start = now - 86400

    headers = {
        'Content-type': 'application/json',
        'Security-Key': api_key,
    }

    json_data = {
        'period': [start, now],
        'did': num,
        'per_page': config.default_request_per_page,
        'page': page,
    }
    try:
        # print(json_data)
        logging.info(f"Attempting to pull call history for {start} - {now}. Attempt {tryNum}")
        response = requests.get(
            'https://api2.questblue.com/callhistory',
            headers=headers,
            json=json_data,
            auth=(user, secret),
        ).json()
    except Exception as err:
        if tryNum > 5:
            logging.info(f"FATAL ERROR! PROGRAM EXCEEDED 5 CONNECTION ATTEMPTS")
            quit()
        else:    
            tryNum += 1
            logging.error(err)
            logging.info(f"ERROR TIMED OUT :: ON RETRY {tryNum}")
            response = __internal_requestReports_num(num, unix, page, tryNum)
    return response

def __internal_requestReports_trunk(trunk: str, unix :int ,page=1, tryNum=1):
    now = unix
    start = now - 86400
    headers = {
        'Content-type': 'application/json',
        'Security-Key': api_key,
    }

    json_data = {
        'trunk': trunk,
        'period': [start, now],
        'per_page': config.default_request_per_page,
        'page': page,
    }
    try:
        response = requests.get(
            'https://api2.questblue.com/callhistory',
            headers=headers,
            json=json_data,
            auth=(user, secret),
        ).json()
    except Exception as err:
        if tryNum > 5:
            logging.info(f"FATAL ERROR! PROGRAM EXCEEDED 5 CONNECTION ATTEMPTS")
            quit()
        else:    
            tryNum += 1
            logging.error(err)
            logging.info(f"ERROR TIMED OUT :: ON RETRY {tryNum}")
            response = __internal_requestReports_trunk(trunk, unix, page, tryNum)
    return response

def __requestTrunks(page=int(1)):
    headers = {
        'Content-type': 'application/json',
        'Security-Key': api_key,
    }

    json_data = {
        'per_page': config.default_trunks_per_page,
        'page': page,
    }

    response = requests.get(
        'https://api2.questblue.com/siptrunk',
        headers=headers,
        json=json_data,
        auth=(user, secret),
    ).json()
    return response

### Public Functions ###

def tollFreeMonth(areaCode=int(), start_day=datetime.datetime.now(), end_day=datetime.datetime.now()):
    currDay = start_day
    endDay = end_day
    
    response = __requestDids_area_code(areaCode)
    nums = getNumbers(response)
    billed_min = {
        'Inbound': float(0),
        'Outbound': float(0),
    }
    billed = {
        'Inbound': float(0),
        'Outbound': float(0),
    }
    logging.info(f"{nums}")
    for num in nums:
        logging.info(f"Starting - {num}")
        currDay = start_day
        billed_min['Inbound'] = 0
        billed_min['Outbound'] = 0
        while currDay < endDay:
            # print(currDay)
            tempDay = currDay + datetime.timedelta(days=1)
            currTime = time.mktime(tempDay.timetuple())
            response = __internal_getCosts(currTime, num)
            # print(response)
            billed_min['Inbound'] += response['Inbound']
            billed_min['Outbound'] += response['Outbound']
            logging.info(f"Day Finished - {num} - {currDay} - {billed_min}")
            currDay = currDay + datetime.timedelta(days=1)
        billed['Inbound'] = billed_min['Inbound'] * config.inboud_charge_rate
        billed['Outbound'] = billed_min['Outbound'] * config.outbound_charge_rate
        logging.info(f"Month Finished for {num} - {billed_min} - {billed}")
        sheet.writerow([num, billed_min['Inbound'], round(billed['Inbound'], 2), billed_min['Outbound'], round(billed['Outbound'], 2)]) # type: ignore
        # print(f"Did {num} - {billed_min} - {billed}")
    logging.info(f"Finished area code {areaCode}")
    return

def __internal_getCosts(time: datetime.time, num: int):
    answer = {
        'Inbound': float(0),
        'Outbound': float(0),
    }
    page = 1
    response = __internal_requestReports_num(num, time ,page)
    # log.write(str(response))
    if "total_pages" in response:
        while page <= int(response['total_pages']):
            
            # logging.info(f"\n{response}")
            tags = []
            if 'data' in response:
                for tag in response['data']:
                    tags.append(tag)

                for i in range(len(tags)):
                    
                    if response['data'][i]['billed_min'] == 'unknown':
                        logging.info(f"Unknown Call Found!! {response['data'][i]}")
                    elif response['data'][i]['call_type'] == 'Outbound TF Call':
                        logging.info(f"Outbound Call - {response['data'][i]['billed_min']} added")
                        answer['Outbound'] += float(response['data'][i]['billed_min'])
                    elif response['data'][i]['call_type'] == 'Inbound Toll Free Call':
                        # logging.info(f"Inbound Call - {response['data'][i]['billed_min']} added")
                        answer['Inbound'] += float(response['data'][i]['billed_min'])
                # logging.info(f"Current Total - {cost}")
            page += 1
            if page <= int(response['total_pages']):
                response = __internal_requestReports_num(num,time, page)
    logging.info(f"Returning - {answer}")
    return answer


def getDids_all_by_num(num):

    print("got page 1")
    main = __requestDids_area_code(num, 1)

    pages = 2
    if "total_pages" in main:
        while pages <= int(main['total_pages']):
            print(f"got page {pages}")
            
            main['data'] += response['data']
            pages += 1
            if pages <= int(response['total_pages']):
                response = __requestDids_area_code(num, pages)
    
    return main

def getNumbers(response):
    tags = []
    answer = []
    for tag in response['data']:
        tags.append(tag)

    for i in range(len(tags)):
        answer.append(response['data'][i]['did'])

    return answer

def getMonthReport_Trunk(name=str(), start_day=datetime.datetime.now(), end_day=datetime.datetime.now()):
    logging.info(f"Starting {name}")
    # print(f"Started {name}")
    answer = {}
    answer = __addToDict(name, 'Trunk', answer)
    currDay = start_day
    endDay = end_day
    delta = endDay - currDay
    loopDay = 1
    # df = pd.DataFrame({"Did": [np.nan], "Inbound Total": [np.nan], "Outbound Total": [np.nan], "Inbound TF Total": [np.nan], "Outbound TF Total": [np.nan]})
    # print(df)
    for loopDay in range(int(delta.days)):

        tempDay = currDay + datetime.timedelta(days=1)
        currTime = time.mktime(tempDay.timetuple())
        response= __getMinByTrunk(name, currTime)
        for data in response:
            answer = __addToDict(response[data], data, answer)
        logging.info(f"Finished {name} {currDay}")
        currDay = currDay + datetime.timedelta(days=1)
        # df = pd.concat([df,df2])

        loopDay += 1
    # print(answer)
    # print(df)
    logging.info(f"Month Finished returning {name}")
    # print(f"Finished {name}")
    sheet.writerow([answer['Trunk'], answer['inbound_calls_total'], round(answer['inbound_min_total'], 2), answer['outbound_calls_total'], round(answer['outbound_min_total'], 2),
                    answer['Inbound_TF_total'], round(answer['Inbound_TF_min'], 2), answer['Outbound_TF_total'], round(answer['Outbound_TF_min'], 2)])

    return answer

def __getMinByTrunk(name, unix=float()):
    answer = {
        'inbound_calls_total': 0,
        'inbound_min_total': round(float(0), 2),
        'outbound_calls_total': 0,
        'outbound_min_total': round(float(0), 2),

        'Inbound_TF_total': 0,
        'Inbound_TF_min': round(float(0), 2),
        'Outbound_TF_total': 0,
        'Outbound_TF_min': round(float(0), 2),
    }

    page = 1
    response = __internal_requestReports_trunk(name, unix, page)
    # print(response)
    # df = pd.DataFrame({"Did": [np.nan], "Inbound Total": [np.nan], "Outbound Total": [np.nan], "Inbound TF Total": [np.nan], "Outbound TF Total": [np.nan]})
     
    if "total_pages" in response:
        while page <= int(response['total_pages']):
            # print(page)
            tags = []
            if 'data' in response:
                for tag in response['data']:
                    tags.append(tag)
                for i in range(len(tags)):
                    # try:
                    # print(response['data'][i])
                    
                    if response['data'][i]['billed_min'] == 'unknown':
                        logging.warning(f"Unknown Call Found!! {response['data'][i]}")
                    elif response['data'][i]['call_status'] == 'ok':
                        if response['data'][i]['call_type'] == 'Inbound Call':
                            answer['inbound_calls_total'] += 1
                            answer['inbound_min_total'] += round(float(response['data'][i]['call_duration_min']), 2)
                        elif response['data'][i]['call_type'] == 'Inbound Toll Free Call':
                            answer["Inbound_TF_total"] += 1
                            answer['Inbound_TF_min'] += round(float(response['data'][i]['call_duration_min']), 2)
                        elif response['data'][i]['call_type'] == 'Outbound Call':
                            answer['outbound_calls_total'] += 1
                            answer['outbound_min_total'] += round(float(response['data'][i]['call_duration_min']), 2)
                        elif response['data'][i]['call_type'] == 'Outbound TF Call':
                            answer['Outbound_TF_total'] += 1
                            answer['Outbound_TF_min'] += round(float(response['data'][i]['call_duration_min']), 2)
                # except KeyError:
                #     print(response['data'][i])
                #     input("Press any key to continue...")
            page += 1
            if page <= int(response['total_pages']):
                response = __internal_requestReports_trunk(name, unix, page)
    return answer

def getTrunkNames():
    tags = []
    answer = []

    response = __requestTrunks()

    for tag in response['data']:
        tags.append(tag)

    for i in range(len(tags)):
        if response['data'][i]['trunk'] in answer:
            continue
        else:
            answer.append(response['data'][i]['trunk'])

    return answer

def __getTrunkDids(Trunk: str):
    tags = []
    response = __requestTrunks()
    for tag in response['data']:
        tags.append(tag)
    
    for i in range(len(tags)):
        try:
            if response['data'][i]['trunk'] == Trunk:
                return response['data'][i]['routed_dids']
            else:
                continue
        except:
            logging.info(f"No dids on trunk - {response['data'][i]['trunk']}")

#internal helper methods
def check_creds():
    response = __requestDids()
    return response

def month_len(today=datetime.datetime.now()):
    days = (datetime.date(today.year,today.month+1,1) - datetime.date(today.year, today.month, 1)).days
    return days

def logInfo(info):
    logging.info(info)

def closeLog():
    # print(f"Log File - {logFile}")
    log.close()

def closeCSV():
    sheetFileOpened.close()
    # print(f"Your output file is at - {sheetFile}")
    return sheetFile

def __addToDict(value, key=str(), dict={}):
    if key not in dict.keys():
        dict[key] = value
    else:
        dict[key] += value
    return dict


#TODO
#[] Thread Dids
"""
I still need to thread Dids. Write what args need passed and how to do spread sheets
"""
def InDepthThread(did: int, start_Date: datetime.date, end_Date: datetime.date):
    global trunkTotal
    currDay = start_Date
    endDay = end_Date
    delta = endDay - currDay
    loopDay = 1
    
    logging.info(f"Starting - {did}")
    currDay = start_Date
    # trunkTotal ={}
    didWrite = {
        'did': did,
    }
    for loopDay in range(int(delta.days)):
        tempDay = currDay + datetime.timedelta(days=1)
        currTime = time.mktime(tempDay.timetuple())
        response = __getDidHistory_Trunk(did, currTime)
        for data in response:
            
            didWrite = __addToDict(response[data], data, didWrite)
            trunkTotal = __addToDict(response[data], data, trunkTotal)
        # print(trunkTotal)
        currDay = currDay + datetime.timedelta(days=1)
        loopDay += 1
    didSheet.writerow([didWrite['did'], didWrite['inbound_calls_total'], didWrite['Inbound_TF_total'], didWrite['outbound_calls_total'], didWrite['Outbound_TF_total']])
    # print(didWrite)
    # didSheetFileOpened.close()
    # sheet.writerow([trunkTotal['trunk'], trunkTotal['inbound_calls_total'], round(trunkTotal['inbound_min_total'], 2), trunkTotal['outbound_calls_total'], round(trunkTotal['outbound_min_total'], 2),
    #                 trunkTotal['Inbound_TF_total'], round(trunkTotal['Inbound_TF_min'], 2), trunkTotal['Outbound_TF_total'], round(trunkTotal['Outbound_TF_min'], 2)])
    return

def __getDidHistory_Trunk(num: int, time: datetime.time):
    answer = {
        'inbound_calls_total': 0,
        'inbound_min_total': round(float(0), 2),
        'outbound_calls_total': 0,
        'outbound_min_total': round(float(0), 2),

        'Inbound_TF_total': 0,
        'Inbound_TF_min': round(float(0), 2),
        'Outbound_TF_total': 0,
        'Outbound_TF_min': round(float(0), 2),
    }
    page = 1
    response = __internal_requestReports_num(num, time, page)
    if "total_pages" in response:
        while page <= int(response['total_pages']):
            # print(response)
            tags = []
            if 'data' in response:
                for tag in response['data']:
                    tags.append(tag)
                
                for i in range(len(tags)):
                    if response['data'][i]['billed_min'] == 'unknown':
                        logging.warning(f"Unknown Call Found!! {response['data'][i]}")
                    elif response['data'][i]['call_status'] == 'ok':
                        if response['data'][i]['call_type'] == 'Inbound Call':
                            answer['inbound_calls_total'] += 1
                            answer['inbound_min_total'] += round(float(response['data'][i]['call_duration_min']), 2)
                        elif response['data'][i]['call_type'] == 'Inbound Toll Free Call':
                            answer["Inbound_TF_total"] += 1
                            answer['Inbound_TF_min'] += round(float(response['data'][i]['call_duration_min']), 2)
                        elif response['data'][i]['call_type'] == 'Outbound Call':
                            answer['outbound_calls_total'] += 1
                            answer['outbound_min_total'] += round(float(response['data'][i]['call_duration_min']), 2)
                        elif response['data'][i]['call_type'] == 'Outbound TF Call':
                            answer['Outbound_TF_total'] += 1
                            answer['Outbound_TF_min'] += round(float(response['data'][i]['call_duration_min']), 2)
            page += 1
            if page <= int(response['total_pages']):
                response = __internal_requestReports_num(num, time, page)
    return answer

def runDid(trunk, start_date, end_date):
    global did_start_date
    global did_end_date
    global q_did
    global didSheet
    global didSheetFileOpened
    global trunkTotal
    global did_done
    did_done = 0
    trunkTotal = {
        'trunk': trunk,
    }
    
    
    did_start_date = start_date
    did_end_date = end_date
    
    didSheetFP = os.getcwd()
    if trunk == 'HDTArnoldInsura':
        return
    # didSheetFile = f"{didSheetFP}\\outputs\\endMon\\dids\\{trunk}-outputSheet.csv"
    # didSheetFileOpened = open(os.path.join(didSheetFP, didSheetFile), "w")
    # didSheet = csv.writer(didSheetFileOpened)
    # didSheet.writerow(['Did', 'Inbound Calls', 'Inbound TF Calls', 'Outbound Calls', 'Outbound TF Calls'])
    
    
    q_did = Queue()
    nums = __getTrunkDids(trunk)
    for num in nums:
        q_did.put(num)
    
    __thread_did(start_date, end_date)
    sheet.writerow(['Trunk', 'Inbound Calls', 'Inbound Min', 'Outbound Calls', 'Outbound Min', 'Inbound TF Calls', 'Inbound TF Min', 'Outbound TF Calls', 'Outbound TF Min'])
    sheet.writerow([trunkTotal['trunk'], trunkTotal['inbound_calls_total'], round(trunkTotal['inbound_min_total'], 2), trunkTotal['outbound_calls_total'], round(trunkTotal['outbound_min_total'], 2),
                    trunkTotal['Inbound_TF_total'], round(trunkTotal['Inbound_TF_min'], 2), trunkTotal['Outbound_TF_total'], round(trunkTotal['Outbound_TF_min'], 2)])
    print("returning to GUI")
    # didSheetFileOpened.close()
    return


def __did_wroker(start_date, end_date):
    while not q_did.empty():
        if q_did.qsize() == 0:
            return
        else:
            did = q_did.get()
            InDepthThread(did, start_date, end_date)
    
    return

def __thread_did(start_date, end_date):
    thread_list = []
    global did_done
    size = round(q_did.qsize()/2)
    for t in range(round(q_did.qsize()/2)):
        thread = threading.Thread(target=__did_wroker, args=(start_date, end_date))
        thread_list.append(thread)
    for thread in thread_list:
        print(f"Starting Did Thread {thread}")
        thread.start()
    
    for thread in thread_list:
        thread.join()
        did_done += 1
        main.progressBar_endMon.set(float(did_done/size))
        print(f"Closing thread {thread}")
    print("all did threads closed")
    
def InDepthThread(did: int, start_Date: datetime.date, end_Date: datetime.date):
    global trunkTotal
    currDay = start_Date
    endDay = end_Date
    delta = endDay - currDay
    loopDay = 1
    
    logging.info(f"Starting - {did}")
    currDay = start_Date
    # trunkTotal ={}
    didWrite = {
        'did': did,
    }
    for loopDay in range(int(delta.days)):
        tempDay = currDay + datetime.timedelta(days=1)
        currTime = time.mktime(tempDay.timetuple())
        response = __getDidHistory_Trunk(did, currTime)
        for data in response:
            
            didWrite = __addToDict(response[data], data, didWrite)
            trunkTotal = __addToDict(response[data], data, trunkTotal)
        # print(trunkTotal)
        currDay = currDay + datetime.timedelta(days=1)
        loopDay += 1
    sheet.writerow([didWrite['did'], didWrite['inbound_calls_total'], didWrite['Inbound_TF_total'], didWrite['outbound_calls_total'], didWrite['Outbound_TF_total']])
    # print(didWrite)
    # didSheetFileOpened.close()
    # sheet.writerow([trunkTotal['trunk'], trunkTotal['inbound_calls_total'], round(trunkTotal['inbound_min_total'], 2), trunkTotal['outbound_calls_total'], round(trunkTotal['outbound_min_total'], 2),
    #                 trunkTotal['Inbound_TF_total'], round(trunkTotal['Inbound_TF_min'], 2), trunkTotal['Outbound_TF_total'], round(trunkTotal['Outbound_TF_min'], 2)])
    return

def trunkHistory(trunk, start_date, end_date):
    if trunk == 'HDTArnoldInsura':
        return
    
    global did_start_date
    global did_end_date
    global q_did
    global didSheet
    global didSheetFileOpened
    global trunkTotal
    
    trunkTotal = {
        'trunk': trunk,
    }
    
    did_start_date = start_date
    did_end_date = end_date
    
    didSheetFP = os.getcwd()
    
    didSheetFile = f"{didSheetFP}\\outputs\\endMon\\dids\\{trunk}-outputSheet.csv"
    didSheetFileOpened = open(os.path.join(didSheetFP, didSheetFile), "w")
    didSheet = csv.writer(didSheetFileOpened)
    didSheet.writerow(['Did', 'Inbound Calls', 'Inbound TF Calls', 'Outbound Calls', 'Outbound TF Calls'])
    
    currDay = start_date
    endDay = end_date
    delta = endDay - currDay
    loopDay = 1
    
    # logging.info(f"Starting - {did}")
    currDay = start_date
    # trunkTotal ={}
    # didWrite = {
    #     'did': did,
    # }
    
    
    # q_did = Queue()
    nums = __getTrunkDids(trunk)
    for num in nums:
        didWrite = {
            'did': num,
        }
        for loopDay in range(int(delta.days)):
            tempDay = currDay + datetime.timedelta(days=1)
            currTime = time.mktime(tempDay.timetuple())
            response = __getDidHistory_Trunk(num, currTime)
            for data in response:
                
                didWrite = __addToDict(response[data], data, didWrite)
                # trunkTotal = __addToDict(response[data], data, trunkTotal)
            # print(trunkTotal)
            currDay = currDay + datetime.timedelta(days=1)
            loopDay += 1
        print(didWrite)
        didSheet.writerow([didWrite['did'], didWrite['inbound_calls_total'], didWrite['Inbound_TF_total'], didWrite['outbound_calls_total'], didWrite['Outbound_TF_total']])
        # q_did.put(num)
    
    # __thread_did(start_date, end_date)
    # sheet.writerow([trunkTotal['trunk'], trunkTotal['inbound_calls_total'], round(trunkTotal['inbound_min_total'], 2), trunkTotal['outbound_calls_total'], round(trunkTotal['outbound_min_total'], 2),
                    # trunkTotal['Inbound_TF_total'], round(trunkTotal['Inbound_TF_min'], 2), trunkTotal['Outbound_TF_total'], round(trunkTotal['Outbound_TF_min'], 2)])
    print("returning to GUI")
    return