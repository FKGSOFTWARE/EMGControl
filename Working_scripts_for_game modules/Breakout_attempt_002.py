import pygame
import sys
import queue


def run_game(control_queue, threshold_queue):
# def run_game(plotter):

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

    # Additional UI Variables
    font = pygame.font.Font(None, 36)
    extension_threshold = 0.0  # initial value, this should be synced with the actual value from AEMG
    flexion_threshold = 0.0  # initial value, this should be synced with the actual value from AEMG
    threshold_step = 0.005

    # UI Element Positions
    extension_text_pos = (10, screen_height - 40)
    flexion_text_pos = (10, screen_height - 70)
    increase_ext_button = pygame.Rect(250, screen_height - 40, 20, 20)
    decrease_ext_button = pygame.Rect(220, screen_height - 40, 20, 20)
    increase_flex_button = pygame.Rect(250, screen_height - 70, 20, 20)
    decrease_flex_button = pygame.Rect(220, screen_height - 70, 20, 20)

    # Game Variables
    ball_dy = 2
    ball_dx = 2
    paddle_speed = 8
    run_game = True

    # Game loop
    while run_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_game = False
        
        # Draw the threshold values
        extension_label = font.render(f'Extension: {extension_threshold:.3f}', True, (255, 255, 255))
        screen.blit(extension_label, extension_text_pos)

        flexion_label = font.render(f'Flexion: {flexion_threshold:.3f}', True, (255, 255, 255))
        screen.blit(flexion_label, flexion_text_pos)

        # Draw the buttons
        pygame.draw.rect(screen, (255, 0, 0), increase_ext_button)
        pygame.draw.rect(screen, (0, 255, 0), decrease_ext_button)
        pygame.draw.rect(screen, (255, 0, 0), increase_flex_button)
        pygame.draw.rect(screen, (0, 255, 0), decrease_flex_button)

        # Check for button presses
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if increase_ext_button.collidepoint(mouse_pos):
                extension_threshold += threshold_step
                threshold_queue.put({"type": "Extension", "value": extension_threshold})
            elif decrease_ext_button.collidepoint(mouse_pos):
                extension_threshold -= threshold_step
                threshold_queue.put({"type": "Extension", "value": extension_threshold})
            elif increase_flex_button.collidepoint(mouse_pos):
                flexion_threshold += threshold_step
                threshold_queue.put({"type": "Flexion", "value": flexion_threshold})
            elif decrease_flex_button.collidepoint(mouse_pos):
                flexion_threshold -= threshold_step
                threshold_queue.put({"type": "Flexion", "value": flexion_threshold})

            # Paddle movement
        try:
            control = control_queue.get_nowait()
            # control = plotter.get()
            print("in-game control = ", control)

            if control == "Flexion" and paddle.left > 0:
                print("left")   
                # control_queue.clear()
                paddle.move_ip(-paddle_speed, 0)
            elif control == "Extension" and paddle.right < screen_width:
                print("right")
                # control_queue.clear()
                paddle.move_ip(paddle_speed, 0)
        except queue.Empty:
            pass
        

        # Ball movement
        ball.move_ip(ball_dx, ball_dy)

        # Ball and wall collision
        if ball.left < 0 or ball.right > screen_width:
            ball_dx *= -1
        if ball.top < 0:
            ball_dy *= -1
        # if ball.bottom > screen_height:
        #     run_game = False  # Game over when ball hits bottom

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
