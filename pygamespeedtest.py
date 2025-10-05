import pygame
import random
pygame.init()
window = pygame.display.set_mode((800, 600))
screen = pygame.Surface((800, 600), pygame.SRCALPHA)  # Enable per-pixel alpha
pygame.display.set_caption("100,000 Transparent Rectangles Speed Test")

rects = [
    pygame.Rect(
        random.randint(0, 799),
        random.randint(0, 599),
        random.randint(1, 5),
        random.randint(1, 5)
    )
    for _ in range(100_000)
]
colors = [
    (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(32, 128)  # Alpha between 32 and 128 for transparency
    )
    for _ in range(100_000)
]

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0, 0))  # Clear with transparent black
    for rect, color in zip(rects, colors):
        pygame.draw.rect(screen, color, rect)
    window.blit(screen, (0, 0))
    pygame.display.flip()
    clock.tick(60)
    pygame.display.set_caption(f"100,000 Transparent Rectangles Speed Test - {int(clock.get_fps())} FPS")

pygame.quit()