import pygame
import sys

# General setup
pygame.init()
clock = pygame.time.Clock()

# Setting up the main window
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Game Rectangles
paddle = pygame.Rect(screen_width // 2 - 50, screen_height - 20, 100, 10)
ball = pygame.Rect(screen_width // 2 - 15 // 2, screen_height // 2 - 15 // 2, 15, 15)

# Blocks
block_width = 60
block_height = 30
blocks = [pygame.Rect(50 + 70 * i, 50 + 50 * j, block_width, block_height) for i in range(10) for j in range(4)]

# Game Variables
ball_dy = 3
ball_dx = 3
paddle_speed = 4
run_game = True

# Game loop
while run_game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_game = False
            
    # # Paddle movement
    # keys = pygame.key.get_pressed()
    # if keys[pygame.K_LEFT] and paddle.left > 0:
    #     paddle.move_ip(-paddle_speed, 0)
    # if keys[pygame.K_RIGHT] and paddle.right < screen_width:
    #     paddle.move_ip(paddle_speed, 0)
        
    # Ball movement
    ball.move_ip(ball_dx, ball_dy)
    
    # Ball and wall collision
    if ball.left < 0 or ball.right > screen_width:
        ball_dx *= -1
    if ball.top < 0:
        ball_dy *= -1
    if ball.bottom > screen_height:
        run_game = False  # Game over when ball hits bottom
    import pygame
import sys

def run_game():
    # General setup
    pygame.init()
    clock = pygame.time.Clock()

    # Setting up the main window
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))

    # Game Rectangles
    paddle = pygame.Rect(screen_width // 2 - 50, screen_height - 20, 100, 10)
    ball = pygame.Rect(screen_width // 2 - 15 // 2, screen_height // 2 - 15 // 2, 15, 15)

    # Blocks
    block_width = 60
    block_height = 30
    blocks = [pygame.Rect(50 + 70 * i, 50 + 50 * j, block_width, block_height) for i in range(10) for j in range(4)]

    # Game Variables
    ball_dy = 3
    ball_dx = 3
    paddle_speed = 2
    run_game = True

    # Game loop
    while run_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_game = False

        # Paddle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.move_ip(-paddle_speed, 0)
        if keys[pygame.K_RIGHT] and paddle.right < screen_width:
            paddle.move_ip(paddle_speed, 0)

        # Ball movement
        ball.move_ip(ball_dx, ball_dy)

        # Ball and wall collision
        if ball.left < 0 or ball.right > screen_width:
            ball_dx *= -1
        if ball.top < 0:
            ball_dy *= -1
        if ball.bottom > screen_height:
            run_game = False  # Game over when ball hits bottom

        # Ball and paddle collision
        if ball.colliderect(paddle):
            ball_dy *= -1

        # Ball and block collision
        hit_index = ball.collidelist(blocks)
        if hit_index != -1:
            hit_rect = blocks.pop(hit_index)
            if ball_dx > 0:
                ball.right = hit_rect.left
            else:
                ball.left = hit_rect.right
            ball_dy *= -1

        # Drawing everything
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, pygame.Color('white'), paddle)
        pygame.draw.rect(screen, pygame.Color('white'), ball)
        for block in blocks:
            pygame.draw.rect(screen, pygame.Color('white'), block)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

    # Ball and paddle collision
    if ball.colliderect(paddle):
        ball_dy *= -1
        
    # Ball and block collision
    hit_index = ball.collidelist(blocks)
    if hit_index != -1:
        hit_rect = blocks.pop(hit_index)
        if ball_dx > 0:
            ball.right = hit_rect.left
        else:
            ball.left = hit_rect.right
        ball_dy *= -1
    
    # Drawing everything
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, pygame.Color('white'), paddle)
    pygame.draw.rect(screen, pygame.Color('white'), ball)
    for block in blocks:
        pygame.draw.rect(screen, pygame.Color('white'), block)
    
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
sys.exit()
