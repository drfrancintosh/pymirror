import os

# Set environment variables for framebuffer
os.putenv("SDL_AUDIODRIVER", "dummy")
os.putenv("SDL_FBDEV", "/dev/fb0")
os.putenv("SDL_VIDEODRIVER", "fkms")

import pygame

# Initialize pygame
pygame.init()

# Set up a screen object with the framebuffer
screen = pygame.display.set_mode((1920, 1080))

# Fill the screen with a color
screen.fill((255, 0, 0))  # Red
pygame.display.update()

# Keep the window open for 5 seconds
pygame.time.wait(5000)

# Quit pygame
pygame.quit()
