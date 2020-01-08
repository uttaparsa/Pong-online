import sys, pygame
pygame.init()

size = width, height = 1600, 900
speed = [10, 10]
black = 0, 0, 0

screen = pygame.display.set_mode(size)
fpsClock = pygame.time.Clock()
ball = pygame.image.load("mamad.jpg")
ball = pygame.transform.scale(ball, (300, 300))
ballrect = ball.get_rect()
# ballrect = pygame.transform.rotozoom(ballrect, 0, 2)
#IMAGE_BIG = pg.transform.rotozoom(IMAGE, 0, 2)
print(pygame.font)
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()
    fpsClock.tick(90)						#run at 10 fps