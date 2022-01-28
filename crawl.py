import requests
import re
import json
from multiprocessing import Process, Queue, freeze_support
import math

url = 'https://dhlottery.co.kr/gameResult.do?method=byWin'
response = requests.get(url)
body = response.content.decode(response.encoding)

pattern = re.compile('동행복권\s([\d]{1,4})회')
result = re.findall(pattern, body)

latestDrwNo = int(result[0])

def loadLottoData(drwNo):
  res = requests.get(f'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={drwNo}')
  return json.loads(res.content.decode(res.encoding))

def lottoDataRangeLoader(start, end, queueData):
  dataList = []
  for drwNo in range(start, end):
    print(f'#{drwNo} requesting data --->')
    dataList.append(loadLottoData(drwNo=drwNo))
    print(f'#{drwNo} data received <---')
  queueData.put(dataList)

if __name__ == '__main__':
    freeze_support()
    reqNum = 10
    processList = []
    lottoData = Queue()

    for pid in range(math.ceil(latestDrwNo / reqNum)):
        start = pid * reqNum + 1
        if start + reqNum > latestDrwNo:
            end = latestDrwNo + 1
        else:
            end = start + reqNum
        proc = Process(target=lottoDataRangeLoader, args=(start, end, lottoData))
        proc.start()
        processList.append(proc)

    print("wait process...")
    for proc in processList:
        proc.join()
    print("all process done!")

    for idx in range(len(processList)):
        print(lottoData.get())
