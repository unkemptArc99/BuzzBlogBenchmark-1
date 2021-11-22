import matplotlib.pyplot as plt
import numpy as np

def plot(plotData, figName, xlabel, ylabel, title):
    combined = {}
    for v in plotData.values():
        combined[str(v['pid']) + " " + v['name']] = v['totalSpin'] // v['count']
    combined = dict(sorted(combined.items(), key=lambda item: item[1]))
    x = list(combined.keys())
    y = list(combined.values())
    plt.plot(x, y)
    plt.xticks(rotation = 90)
    plt.xlabel(xlabel=xlabel)
    plt.ylabel(ylabel=ylabel)
    plt.title(title)
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(figName)
    plt.close()

def inputToMap(inputData):
    mp = {}
    for lines in inputData:
        words = lines.split()
        index = 0
        flag = -1
        while index < len(words):
            if not words[index].isnumeric():
                if not (words[index][-1] == '\'' or words[index][-1] == ']'):
                    flag = index
                    words[index] += " " + words[index+1]
                    words.pop(index+1)
                else:
                    index += 1
            else:
                if index >= 2:
                    break
                index += 1      
        if words[2] in mp:
            old = mp[words[2]]
            mp[words[2]] = {'pid': int(words[2]), 'name': words[1], 'totalSpin': old['totalSpin'] + int(words[-1]), 'count': old['count'] + int(words[-3])}
        else:
            mp[words[2]] = {'pid': int(words[2]), 'name': words[1], 'totalSpin': int(words[-1]), 'count': int(words[-3])}
    return mp

def parseInput():
    with open("out.log") as f:
        lines = f.readlines()
        index = 0
        indexSpin = 0
        indexHold = 0
        while True:
            words = lines[index].split()
            if words:
                if words[0] == "Caller":
                    if indexSpin == 0:
                        indexSpin = index
                    elif indexHold == 0:
                        indexHold = index
                        break
            index += 1
        spinData = lines[indexSpin+1:indexHold-1]
        holdData = lines[indexHold+1:]
        return spinData, holdData

if __name__ == '__main__':
    SPIN_DATA , HOLD_DATA = parseInput()
    SPIN_MAP = inputToMap(SPIN_DATA)
    plot(SPIN_MAP, "spin.png", "Process PID and Name", "Avg. Time wait for locks (in ns)", "Processes that were trying to get locks")
    HOLD_MAP = inputToMap(HOLD_DATA)
    plot(HOLD_MAP, "hold.png", "Process PID and Name", "Avg. Time held locks (in ns)", "Processes that held locks")