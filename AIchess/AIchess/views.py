from django.shortcuts import render, HttpResponse
from . import playerBlack as pb
import json


def chessBoard(r):
    # print(pb.checkMove("e2e4"));
    return render(r, "chess.html")


def checkThis(r, move):
    valid = pb.checkMove(move)
    if not pb.online['done']:
        valid = False
    if valid:
        pb.online['move'] = move
        pb.online['done'] = False
    return HttpResponse(str(valid).lower())


def getAImove(r):
    print(pb.online)
    if pb.online['done'] and pb.online['AImove'] != '':
        amove = pb.online['AImove']
        pb.online['AImove'] = ''
        return HttpResponse(json.dumps({'move': amove}))
    return HttpResponse(json.dumps({'move': ''}))
