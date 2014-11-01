#! /usr/bin/python
# -*- coding: utf-8 -*-
from tarea_1_fork import Utils
from Classification import Clasificator
import csv


def doMetrics(Display=False, WS=False, Ver=2):
    utils = Utils(Display=Display, WS=WS, Ver=Ver)
    c = Clasificator(Ver=Ver)
    if Ver == 2:
        base_save = "./res/statistics/Metrics"
    else:
        base_save = "./res/statistics2/Metrics"

    (posWords, negWords, posI, negI, tokenizedComm) = utils.process()
    matrix = {}
    for i in range(0, 30):
        train_path = "./resources/statistic/train" + str(i) + ".txt"
        test_path = "./resources/statistic/test" + str(i) + ".txt"
        (Metrics, num) = c.process(posWords, negWords, posI, negI,
            tokenizedComm, train_path, test_path)
        c.saveMetrics(Metrics, base_save + str(i) + ".txt")
        matrix[i] = num
    return matrix


def generateFile(metrics, outfile):
    column = [i for i in range(1, 31)]
    column.append("AVG")
    matrix = [metrics[j] for j in range(0, 30)]
    avgRow = []
    for i in range(0, 5):
        l = [matrix[e][i] for e in range(0, 30)]
        avg = sum(l) / float(len(l))
        avgRow.append(avg)
    #add avg
    avgRow.insert(0, "AVG")
    matrix.append(avgRow)
    #add first column
    for i in range(0, 30):
        matrix[i].insert(0, i + 1)

    with open(outfile, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(matrix)

if __name__ == "__main__":
    metrics = doMetrics(Ver=2)
    metrics2 = doMetrics(Ver=1)
    generateFile(metrics, "tabla1.csv")
    generateFile(metrics2, "tabla2.csv")
