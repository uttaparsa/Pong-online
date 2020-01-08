import time
import socket
import sys
import os
import pygame
import threading
from pongClient import Paddle, Ball, WIDTH, HEIGHT, UP, DOWN
from constants import LEFT_PADDLE_ID, RIGHT_PADDLE_ID, DEFAULT_PORT, PADDLE_HEIGHT, PADDLE_WIDTH, FPS, SYMMETRIC, ASYMMETRIC , SERVER_NAME
import logging
from MyCrypt import *
logging.basicConfig(format='%(asctime)s - SERVER - %(levelname)s - %(message)s',
                    level=logging.INFO)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = SERVER_NAME
port = DEFAULT_PORT

server_ip = socket.gethostbyname(server)
keyf = open('key.key' , 'rb')
key = keyf.read()
cipher = Symmetric(key)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

pygame.init()


class Game:

    def __init__(self):
        self.ball = Ball()
        self.leftPaddle = Paddle(LEFT_PADDLE_ID)
        self.rightPaddle = Paddle(RIGHT_PADDLE_ID)
        self.clock = pygame.time.Clock()
        self.play = False
        self.turn = LEFT_PADDLE_ID
        logging.info('Game initiated')

    def start(self):
        logging.info('Starting game')
        while True:
            if self.play:
                # Update ball position
                self.ball.x += self.ball.speed_x
                self.ball.y += self.ball.speed_y
                # Calculate goals
                if self.ball.x+self.ball.radius > WIDTH:
                    self.ball.speed_y = -self.ball.speed_y
                    self.ball.placeInFrontOfRightPaddle(self.rightPaddle)
                    self.play = False
                    self.turn = RIGHT_PADDLE_ID
                    logging.info('goal for left paddle')
                    self.leftPaddle.score += 1
                elif self.ball.x-self.ball.radius < 0:
                    self.ball.speed_y = -self.ball.speed_y
                    self.ball.placeInFrontOfLeftPaddle(self.leftPaddle)
                    self.play = False
                    self.turn = LEFT_PADDLE_ID
                    logging.info('goal for right paddle')
                    self.rightPaddle.score += 1

                #collision with horizontal walls
                if self.ball.y+self.ball.radius > HEIGHT:
                    self.ball.speed_y = -self.ball.speed_y
                elif self.ball.y-self.ball.radius < 0:
                    self.ball.speed_y = abs(self.ball.speed_y)

                # Bounce ball off paddles
                if self.ball.x-self.ball.radius <= (self.leftPaddle.x + PADDLE_WIDTH) and ((self.leftPaddle.y + PADDLE_HEIGHT) >= self.ball.y >= self.leftPaddle.y):
                    self.ball.x = self.leftPaddle.x + PADDLE_WIDTH + self.ball.radius
                    self.ball.speed_x = abs(self.ball.speed_x)
                    logging.info(f'game:start:bouncing ball off left paddle')
                elif self.ball.x+self.ball.radius >= self.rightPaddle.x and ((self.rightPaddle.y + PADDLE_HEIGHT) >= self.ball.y >= self.rightPaddle.y):
                    self.ball.x = self.rightPaddle.x - self.ball.radius
                    self.ball.speed_x = -self.ball.speed_x
                    logging.info(f'game:start:bouncing ball off right paddle')
            self.clock.tick(FPS)

    def stop(self):
        self.play = False
        logging.info('game stopped successfully?!')


currentId = LEFT_PADDLE_ID


def playGame():
    global game
    game.play = True
    game.start()


game = Game()


def threaded_client(conn, thread_id):
    logging.info(
        'threaded_client: created new thread with id : '+str(thread_id))
    global currentId
    global game
    conn.send(str.encode(str(currentId)))
    if (currentId == RIGHT_PADDLE_ID):
        gameThread = threading.Thread(target=playGame, args=())
        gameThread.start()
    currentId = RIGHT_PADDLE_ID

    reply = ''
    while True:
        try:
            data = conn.recv(2048)
            logging.info(f'Recieved data : {time.time_ns()}')
            if SYMMETRIC:
                reply = cipher.decrypt(data)
                logging.info(f'server:decrypted message : {reply}')
            else:
                reply = data.decode('utf-8')

            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                logging.info("Recieved: " + reply)
                arr = reply.split(":")

                if arr[1] != "NULL":  # might cause problems
                    print("arr[1] : "+arr[1])
                    if game.play == False:
                        if (LEFT_PADDLE_ID == int(arr[0])) and (game.turn == LEFT_PADDLE_ID):
                            game.play = True
                        elif RIGHT_PADDLE_ID == int(arr[0])and (game.turn == RIGHT_PADDLE_ID):
                            game.play = True
                    if int(arr[0]) == LEFT_PADDLE_ID:
                        game.leftPaddle.move(int(arr[1]))
                    elif int(arr[0]) == RIGHT_PADDLE_ID:
                        game.rightPaddle.move(int(arr[1]))

                if int(arr[0]) == LEFT_PADDLE_ID:
                    reply = f"ball:{game.ball.x},{game.ball.y}|paddle left:{game.leftPaddle.x},{game.leftPaddle.y}|paddle right:{game.rightPaddle.x},{game.rightPaddle.y}|score:{game.leftPaddle.score},{game.rightPaddle.score}|count:{threading.activeCount() - 1}"
                elif int(arr[0]) == RIGHT_PADDLE_ID:
                    reply = f"ball:{game.ball.x},{game.ball.y}|paddle right:{game.rightPaddle.x},{game.rightPaddle.y}|paddle left:{game.leftPaddle.x},{game.leftPaddle.y}|score:{game.rightPaddle.score},{game.leftPaddle.score}|count:{threading.activeCount() - 1}"

                logging.info(f"threaded_client {thread_id}: Sending: {reply}")
            if SYMMETRIC:
                reply = cipher.encrypt(reply)
                logging.info(f'server:encypted message : {reply}')
            else :
                reply = str.encode(reply)
            conn.sendall(reply)
            
        except Exception as e:
            print("*************************************\n")
            print("SERVER: Breaker exception happened : "+str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print("\n\n*************************************")
            break

    print("Connection Closed")
    currentId = 0
    game.stop()
    conn.close()


thread_id = 0

while True:
    thread_id = thread_id + 1
    conn, addr = s.accept()
    logging.info(f"Connected to: {addr}")

    t1 = threading.Thread(target=threaded_client, args=(conn, thread_id,))
    t1.start()
