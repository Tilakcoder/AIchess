import chess
import chess.engine
import serial
import time

port = "COM6"

board_size = 260
biasx = 0
biasy = 0


def is_square_empty(board, square):
    piece = board.piece_at(chess.parse_square(square))
    return piece is None


def get_ai_move(board, engine, time_limit=2.0):
    result = engine.play(board, chess.engine.Limit(time=time_limit))
    return result.move.uci()


def getBox(row, column):
    return int(row), abs(8-(ord(column) - 97))



def runGcode(ser, move='e2e4'):
    start = move[:2]
    end = move[2:]
    sx, sy = getBox(start[1], start[0])
    ex, ey = getBox(end[1], end[0])
    rb = board_size / 8
    ehalf = rb / 2
    # ehalf = 0
    sx = (sx * rb) + ehalf + biasx
    sy = (sy * rb) + ehalf + biasy
    ex = (ex * rb) + ehalf + biasx
    ey = (ey * rb) + ehalf + biasy

    code = "G00 X" + str(-1 * sx) + " Y" + str(-1 * sy) + ";"
    send_move_to_arduino(ser, code, ser)

    code = "G00 Z1;"
    send_move_to_arduino(ser, code, ser)

    code = "G00 X" + str(-1 * ex) + " Y" + str(-1 * ey) + ";"
    send_move_to_arduino(ser, code, ser)

    code = "G00 Z0;"
    send_move_to_arduino(ser, code, ser)


def send_move_to_arduino(serial_port, move, ser=''):
    serial_port.write(move.encode())
    # serial_port.write(";")
    while True and ser!='':
        response = receive_move_from_arduino(ser)
        if len(response) > 1:
            print(response)
            break


def receive_move_from_arduino(serial_port):
    return serial_port.readline().decode().strip()


def main():
    board = chess.Board()

    # Replace "path/to/stockfish" with the actual path to your Stockfish executable
    with chess.engine.SimpleEngine.popen_uci(r"./stockfish/stockfish-windows-x86-64-modern.exe") as engine:
        with serial.Serial(port, 9600, timeout=1) as ser:
            time.sleep(2)
            while not board.is_game_over():
                print(board)

                # Get user move in UCI format
                user_move_uci = input("Enter your move (UCI format): ")

                # Make user move on the board
                board.push_uci(user_move_uci)

                # Send user move to arudino

                send_move_to_arduino(ser, user_move_uci)

                # Check if the game is over after the user move
                if board.is_game_over():
                    break

                # Get AI move in UCI format
                ai_move_uci = get_ai_move(board, engine)

                # Make AI move on the board
                board.push_uci(ai_move_uci)
                # print(ai_move_uci)
                runGcode(ser, ai_move_uci)
                # send_move_to_arduino(ser, ai_move_uci + ";");
                # time.sleep(1)

                # while (True):
                #     response = receive_move_from_arduino(ser)
                #     if len(response) > 1:
                #         print(response)
                #         break

                print(f"AI's move: {ai_move_uci}")

            print("Game Over")
            print("Result: ", board.result())
