import pygame
import random
import sys
import os

pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Cube Runner")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)

# Initialize mixer for sound
pygame.mixer.init()

# Try loading sounds (add your .wav/.mp3 files in same folder)
try:
    hit_sound = pygame.mixer.Sound("hit.wav")
    collect_sound = pygame.mixer.Sound("powerup.wav")
    bg_music = pygame.mixer.Sound("bg_music.mp3")
    bg_music.play(-1)  # loop forever
except Exception as e:
    print("Sound loading failed:", e)
    hit_sound = collect_sound = bg_music = None

# Colors
WHITE = (255,255,255)
RED = (255,0,0)
BLUE = (0,255,255)
GREEN = (0,255,0)
BLACK = (0,0,0)
YELLOW = (255,255,0)

# Game objects
player_size = 50
player = pygame.Rect(WIDTH//2 - player_size//2, HEIGHT - 100, player_size, player_size)
speed = 6
score, lives = 0, 3
blocks, powerups = [], []
invincible, inv_timer = False, 0
game_over = False
paused = False

# High score file
high_score_file = "high_score.txt"
if not os.path.exists(high_score_file):
    with open(high_score_file, "w") as f:
        f.write("0")
with open(high_score_file, "r") as f:
    high_score = int(f.read())

# Draw hearts for lives
heart_img = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.polygon(heart_img, RED, [(15, 5), (30, 15), (15, 30), (0, 15)])

def draw_hearts():
    for i in range(lives):
        screen.blit(heart_img, (WIDTH - (i+1)*40, 10))

def spawn_block():
    x = random.randint(0, WIDTH - player_size)
    blocks.append(pygame.Rect(x, -player_size, player_size, player_size))

def spawn_powerup():
    x = random.randint(0, WIDTH - player_size)
    powerups.append(pygame.Rect(x, -player_size, player_size, player_size))

def reset_game():
    global blocks, powerups, score, lives, invincible, inv_timer, game_over
    blocks.clear()
    powerups.clear()
    score = 0
    lives = 3
    invincible = False
    inv_timer = 0
    player.x = WIDTH//2 - player_size//2
    game_over = False

def draw_ui():
    s = font.render(f"Score: {score}", True, WHITE)
    hs = font.render(f"High Score: {high_score}", True, BLUE)
    screen.blit(s, (10, 10))
    screen.blit(hs, (10, 50))
    draw_hearts()

def end_game():
    global game_over, high_score
    game_over = True
    if score > high_score:
        high_score = score
        with open(high_score_file, "w") as f:
            f.write(str(score))

def background_color(tick):
    phase = (tick // 10) % 255
    return (phase, 100, 255 - phase)

# Main game loop
while True:
    dt = clock.tick(60)
    screen.fill(background_color(pygame.time.get_ticks() // 50))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()
            if event.key == pygame.K_p:
                paused = not paused

    if not game_over and not paused:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= 7
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += 7

        score += 1

        if random.random() < 0.03:
            spawn_block()
        if random.random() < 0.005:
            spawn_powerup()

        for b in blocks[:]:
            b.y += speed
            if b.colliderect(player):
                if not invincible:
                    if hit_sound: hit_sound.play()
                    lives -= 1
                    if lives <= 0:
                        end_game()
                blocks.remove(b)
            elif b.top > HEIGHT:
                blocks.remove(b)

        for pu in powerups[:]:
            pu.y += speed
            if pu.colliderect(player):
                if collect_sound: collect_sound.play()
                invincible = True
                inv_timer = pygame.time.get_ticks()
                powerups.remove(pu)
            elif pu.top > HEIGHT:
                powerups.remove(pu)

        if invincible and pygame.time.get_ticks() - inv_timer > 5000:
            invincible = False

        color = YELLOW if invincible else GREEN
        pygame.draw.rect(screen, color, player)
        for b in blocks:
            pygame.draw.rect(screen, RED, b)
        for pu in powerups:
            pygame.draw.rect(screen, BLUE, pu)

        draw_ui()

    elif game_over:
        msg = font.render("Game Over! Press [R] to Restart", True, WHITE)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 30))

    if paused and not game_over:
        pause_msg = font.render("Paused - Press [P] to Resume", True, WHITE)
        screen.blit(pause_msg, (WIDTH//2 - pause_msg.get_width()//2, HEIGHT//2))

    pygame.display.flip()
