import pygame
import sys
import queue

def run_game(control_queue, threshold_queue):
    # Initialize pygame
    pygame.init()
    clock = pygame.time.Clock()

    # Window setup
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    
    # Game Rectangles
    paddle = pygame.Rect(screen_width // 2 - 50, screen_height - 20, 100, 10)
    ball = pygame.Rect(screen_width // 2 - 15 // 2, screen_height // 2 - 15 // 2, 15, 15)
    ball_dy = 2
    ball_dx = 2
    paddle_speed = 8
    run_game = True
    
    # Blocks
    block_width = 60
    block_height = 30
    blocks = [pygame.Rect(50 + 70 * i, 50 + 50 * j, block_width, block_height) for i in range(10) for j in range(4)]
    
    # Score
    score = 0
    score_font = pygame.font.Font(None, 36)

    # Game state
    NOT_STARTED, COUNTDOWN, PLAYING = 0, 1, 2
    game_state = NOT_STARTED
    countdown_start_time = 0

    # Buttons
    reset_button = pygame.Rect(20, screen_height - 40, 100, 30)
    start_button = pygame.Rect(screen_width // 2 - 50, screen_height // 2 - 15, 100, 30)
    
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

    # Main game loop
    while run_game:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if reset_button.collidepoint(event.pos):
                    # Reset the game
                    paddle = pygame.Rect(screen_width // 2 - 50, screen_height - 20, 100, 10)
                    ball = pygame.Rect(screen_width // 2 - 15 // 2, screen_height // 2 - 15 // 2, 15, 15)
                    blocks = [pygame.Rect(50 + 70 * i, 50 + 50 * j, block_width, block_height) for i in range(10) for j in range(4)]
                    score = 0
                    game_state = NOT_STARTED

                if start_button.collidepoint(event.pos) and game_state == NOT_STARTED:
                    game_state = COUNTDOWN
                    countdown_start_time = pygame.time.get_ticks()

        if game_state == PLAYING:
            # Paddle movement
            try:
                control = control_queue.get_nowait()
                if control == 'Flexion':
                    paddle.move_ip(-paddle_speed, 0)
                elif control == 'Extension':
                    paddle.move_ip(paddle_speed, 0)
            except queue.Empty:
                pass

            # Ball movement and collisions
            ball.move_ip(ball_dx, ball_dy)
            if ball.colliderect(paddle):
                ball_dy = -ball_dy
            if ball.left <= 0 or ball.right >= screen_width:
                ball_dx = -ball_dx
            if ball.top <= 0:
                ball_dy = -ball_dy
            if ball.bottom >= screen_height:
                paddle = pygame.Rect(screen_width // 2 - 50, screen_height - 20, 100, 10)
                ball = pygame.Rect(screen_width // 2 - 15 // 2, screen_height // 2 - 15 // 2, 15, 15)
                blocks = [pygame.Rect(50 + 70 * i, 50 + 50 * j, block_width, block_height) for i in range(10) for j in range(4)]
                score = 0
                game_state = NOT_STARTED
            for block in blocks:
                if ball.colliderect(block):
                    blocks.remove(block)
                    ball_dy = -ball_dy
                    score += 1
                    break

        # Draw game objects
        pygame.draw.rect(screen, GREEN, paddle)
        pygame.draw.ellipse(screen, RED, ball)
        pygame.draw.aaline(screen, GREEN, (ball.centerx, ball.centery), (paddle.centerx, paddle.centery))
        for block in blocks:
            pygame.draw.rect(screen, BLACK, block)

        # Draw score
        score_surface = score_font.render('Score: {}'.format(score), True, BLACK)
        screen.blit(score_surface, (screen_width - 150, 10))

        # Draw reset button
        pygame.draw.rect(screen, BLACK, reset_button)
        reset_label = score_font.render('RESET', True, WHITE)
        screen.blit(reset_label, (reset_button.x + 20, reset_button.y + 5))

        # Draw start button and countdown
        if game_state == NOT_STARTED:
            pygame.draw.rect(screen, BLACK, start_button)
            start_label = score_font.render('START', True, WHITE)
            screen.blit(start_label, (start_button.x + 20, start_button.y + 5))
        elif game_state == COUNTDOWN:
            elapsed_time = (pygame.time.get_ticks() - countdown_start_time) // 1000
            if elapsed_time < 3:
                count_label = score_font.render(str(3 - elapsed_time), True, BLACK)
                screen.blit(count_label, (screen_width // 2 - 10, screen_height // 2 - 20))
            elif elapsed_time == 3:
                go_label = score_font.render('GO!', True, BLACK)
                screen.blit(go_label, (screen_width // 2 - 30, screen_height // 2 - 20))
                game_state = PLAYING

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

        pygame.display.flip()
        clock.tick(60)
