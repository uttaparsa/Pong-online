import sys
import pygame
import socket
import time
import random
import string
import secrets
from network import ClientNetwork
from constants import LEFT_PADDLE_ID, RIGHT_PADDLE_ID, PADDLE_HEIGHT, PADDLE_WIDTH , FPS, SYMMETRIC, ASYMMETRIC 
import logging
from MyCrypt import *
logging.basicConfig(format='%(asctime)s - CLIENT - %(levelname)s - %(message)s',
                     level=logging.INFO)
pygame.init()


WIDTH, HEIGHT = 1280, 720
WINDOW_HEIGHT = HEIGHT + 200 
SCREEN_SIZE = WIDTH, WINDOW_HEIGHT


FONT = pygame.font.Font(None, 40)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
UP, DOWN = 0, 1

class ScoreBoard():
    global WIDTH
    # global BLACK //TODO : is this gonna work ?! score question
    X = 0
    BOARD_HEIGHT = WINDOW_HEIGHT - HEIGHT
    Y = HEIGHT
    S_WIDTH = WIDTH
    COLOR = BLACK

    def __init__(self,display):
        self.display = display
        self.clientCount = -1
    def draw(self,leftScore, rightScore):
        self.drawBackground()
        self.drawScores(leftScore, rightScore)
        if self.clientCount == 1:
            self.drawInfo()
        logging.info(f'client count  : {self.clientCount}')

    def drawBackground(self):
            pygame.draw.rect(self.display,ScoreBoard.COLOR,(ScoreBoard.X,ScoreBoard.Y,ScoreBoard.S_WIDTH,ScoreBoard.BOARD_HEIGHT))
    def drawScores(self,leftScore, rightScore):
        text = FONT.render("%2s:%2s" % (str(leftScore),
                                str(rightScore)), 1,WHITE)
        textpos = text.get_rect(centerx=WIDTH/2, centery=ScoreBoard.Y+20 )
        self.display.blit(text, textpos)
    def drawInfo(self):
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        text = myfont.render("Waiting for second client", 1,WHITE)
        textpos = text.get_rect(centerx=WIDTH/2, centery=WINDOW_HEIGHT-20 )
        self.display.blit(text, textpos)
        
class Ball:
    SPEED_MAGNITUTE = 6
    def __init__(self):
        global WIDTH
        global HEIGHT
        self.color = BLUE
        self.setRandomDirection()
        self.moveToCenter()
        self.radius = 15
    def get_rect(self):
        return (int(self.x),int(self.y), self.radius*2,  self.radius*2)
    def draw(self,screen):
        pygame.draw.circle(screen, self.color, [
                        self.x, int(self.y)], self.radius)


    def setRandomDirection(self):
        self.speed_x = Ball.SPEED_MAGNITUTE * \
            (-1 if random.choice([True, False]) else 1)
        self.speed_y = Ball.SPEED_MAGNITUTE * \
            (-1 if random.choice([True, False]) else 1)
    def moveToCenter(self):
        self.x = int(0.5 * WIDTH)
        self.y = int(0.5 * HEIGHT)

    def placeInFrontOfLeftPaddle(self,leftPaddle):
        self.x = int(leftPaddle.x+PADDLE_WIDTH/2+1)
        self.y = int(leftPaddle.y+PADDLE_HEIGHT/2)
    def placeInFrontOfRightPaddle(self,rightPaddle):
        self.x = int(rightPaddle.x-(PADDLE_WIDTH/2+1))
        self.y = int(rightPaddle.y+PADDLE_HEIGHT/2)

class DataString:
    @staticmethod
    def update_data(data, ball, myPaddle, opponentPaddle,scoreBoard):

        try:
            logging.info(f"recieved new data : {data}")
            ball.x = int(data.split("|")[0].split(":")[1].split(",")[0])
            ball.y = int(data.split("|")[0].split(":")[1].split(",")[1])
            myPaddle.x = int(data.split("|")[1].split(":")[1].split(",")[0])
            myPaddle.y = int(data.split("|")[1].split(":")[1].split(",")[1])
            opponentPaddle.x = int(data.split(
                "|")[2].split(":")[1].split(",")[0])
            opponentPaddle.y = int(data.split(
                "|")[2].split(":")[1].split(",")[1])
            opponentPaddle.x = int(data.split(
                "|")[2].split(":")[1].split(",")[0])
            opponentPaddle.y = int(data.split(
                "|")[2].split(":")[1].split(",")[1])
            myPaddle.score = int(data.split(
                "|")[3].split(":")[1].split(",")[0])
            opponentPaddle.score = int(data.split(
                "|")[3].split(":")[1].split(",")[1])
            scoreBoard.clientCount = int(data.split(
                "|")[4].split(":")[1])

        except:
            logging.info("exception occurred getting data from server")


class Paddle:
    global HEIGHT
    SPEED = 9

    def __init__(self, input):
        self.score = 0
        self.y = int(0.5 * HEIGHT - 0.5 * PADDLE_HEIGHT)
        if type(input) is int:  # Create from server
            self.id = input
            self.color = RED if self.id == LEFT_PADDLE_ID else GREEN
            self.x = PADDLE_WIDTH + 5 if self.id == LEFT_PADDLE_ID else WIDTH - \
                (PADDLE_WIDTH + PADDLE_WIDTH + 2)
        else:  # Create from client
            self.net = input
            self.color = RED if self.net.id == LEFT_PADDLE_ID else GREEN
            self.x = PADDLE_WIDTH + 5 if self.net.id == LEFT_PADDLE_ID else WIDTH - \
                (PADDLE_WIDTH + PADDLE_WIDTH + 2)

    def draw(self,screen):
        self.rect = self.get_rect()
        pygame.draw.rect(screen, self.color,self.rect)
    def get_rect(self):
        return (int(self.x),int(self.y), PADDLE_WIDTH, PADDLE_HEIGHT)
        
    def move(self, direction):
        try:
            if direction == UP:
                self.y = self.y - Paddle.SPEED
                if self.y < 0:
                    self.y = 0
            elif direction == DOWN:
                self.y = self.y + Paddle.SPEED
                if self.y > (HEIGHT - PADDLE_HEIGHT):
                    self.y = HEIGHT - PADDLE_HEIGHT
        except Exception as e:
            print("CLIENT:MOVE: something went wrong"+str(e))




    def send_data(self, data):
        """
        Send pressedkey to server
        :returns server reply: 
        """
        before = time.time_ns()
        data = str(self.net.id) + ":" + str(data)
        reply = self.net.send(data)
        after = time.time_ns()
        logging.critical(f'message trip time : {after - before}')
        return reply


MAX_SCORE = 3 # TODO : USE THIS VARIABLE!


def main():
    screen = pygame.display.set_mode(SCREEN_SIZE)
    play = True
    myPaddle = Paddle(ClientNetwork())
    pygame.display.set_caption('Pong')
    if myPaddle.net.id == LEFT_PADDLE_ID:
        opponentPaddle = Paddle(RIGHT_PADDLE_ID)
    else:
        opponentPaddle = Paddle(LEFT_PADDLE_ID)
    scoreBoard = ScoreBoard(screen)

    ball = Ball()
    clock = pygame.time.Clock()
    while play:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False

            if event.type == pygame.K_ESCAPE:
                play = False

        pressedKeys = pygame.key.get_pressed()
        if pressedKeys[pygame.K_q]:
            play = False
        if pressedKeys[pygame.K_UP]:
            DataString.update_data(myPaddle.send_data(
                UP), ball, myPaddle, opponentPaddle,scoreBoard)
        elif pressedKeys[pygame.K_DOWN]:
            DataString.update_data(myPaddle.send_data(
                DOWN), ball, myPaddle, opponentPaddle,scoreBoard)
        else:
            DataString.update_data(myPaddle.send_data(
                "NULL"), ball, myPaddle, opponentPaddle,scoreBoard)
        # Draw Screen
        screen.fill(WHITE)

        # Draw Paddles
        myPaddle.draw(screen)
        opponentPaddle.draw(screen)

        # Draw ball
        ball.draw(screen)

        leftScore = myPaddle.score if int(myPaddle.net.id) == LEFT_PADDLE_ID else opponentPaddle.score
        rightScore = myPaddle.score if int(myPaddle.net.id) == RIGHT_PADDLE_ID else opponentPaddle.score
        scoreBoard.draw(leftScore, rightScore)
        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
