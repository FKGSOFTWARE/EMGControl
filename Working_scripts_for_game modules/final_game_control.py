
import pygame
import sys
import queue
import logging

logging.basicConfig(level=logging.INFO)

class BreakoutGame:
    def __init__(self, control_queue):
        pygame.init()
        self.control_queue = control_queue
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.paddle = pygame.Rect(self.screen_width // 2 - 50, self.screen_height - 20, 100, 10)
        self.ball = pygame.Rect(self.screen_width // 2 - 15 // 2, self.screen_height // 2 - 15 // 2, 15, 15)
        self.block_width = 60
        self.block_height = 30
        self.blocks = [pygame.Rect(50 + 70 * i, 50 + 50 * j, self.block_width, self.block_height) for i in range(10) for j in range(4)]
        self.ball_dy = 2
        self.ball_dx = 2
        self.paddle_speed = 8
        self.run_game = True

    def start_game(self):
        while self.run_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run_game = False

            try:
                control = self.control_queue.get_nowait()
                logging.info(f"In-game control = {control}")

                if control == "Flexion" and self.paddle.left > 0:
                    self.paddle.move_ip(-self.paddle_speed, 0)
                elif control == "Extension" and self.paddle.right < self.screen_width:
                    self.paddle.move_ip(self.paddle_speed, 0)
            except queue.Empty:
                pass

            # Ball movement
            self.ball.move_ip(self.ball_dx, self.ball_dy)

            # Ball and wall collision
            if self.ball.left < 0 or self.ball.right > self.screen_width:
                self.ball_dx *= -1
            if self.ball.top < 0:
                self.ball_dy *= -1

            # Ball and paddle collision
            if self.ball.colliderect(self.paddle):
                self.ball_dy *= -1

            # Ball and block collision
            block_hit_index = self.ball.collidelist(self.blocks)
            if block_hit_index >= 0:
                hit_rect = self.blocks.pop(block_hit_index)
                self.ball_dy *= -1

            self.screen.fill((255, 255, 255))
            pygame.draw.rect(self.screen, (0, 255, 0), self.paddle)
            pygame.draw.ellipse(self.screen, (255, 0, 0), self.ball)
            for block in self.blocks:
                pygame.draw.rect(self.screen, (0, 0, 255), block)

            pygame.display.flip()

        pygame.quit()

