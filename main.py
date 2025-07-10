import pygame, sys, random

pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Chef")
clock = pygame.time.Clock()

# High score handling
def load_high_score():
    try:
        with open("scoreboard.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(new_score):
    with open("scoreboard.txt", "w") as f:
        f.write(str(new_score))

# Sounds
sizzle = pygame.mixer.Sound("assets/sounds/sizzle.wav")
game_over_fx = pygame.mixer.Sound("assets/sounds/game_over.wav")

# Load sprite helper
def load_sprite(name, size=None):
    img = pygame.image.load(f"assets/sprites/{name}")
    return pygame.transform.scale(img, size) if size else img

# Load images
bg_img = load_sprite("kitchen_bg.png")
pan_img = load_sprite("pan.png", (100, 100))
splash_img = load_sprite("splash.png", (60, 60))
ingredients = {
    "Egg": load_sprite("egg.png", (60, 60)),
    "Toast": load_sprite("toast.png", (60, 60)),
    "Bacon": load_sprite("bacon.png", (60, 60)),
    "Pancake": load_sprite("pancake.png", (60, 60)),
    "Pepper": load_sprite("pepper.png", (60, 60))
}

# Fonts
title_font = pygame.font.Font("assets/fonts/title_font.ttf", 64)
prompt_font = pygame.font.Font("assets/fonts/title_font.ttf", 32)
game_font = pygame.font.Font("assets/fonts/game_font.ttf", 48)

# Render text with border
def render_text_with_border(text, font, color, border, pos):
    for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
        shadow = font.render(text, True, border)
        screen.blit(shadow, (pos[0]+dx, pos[1]+dy))
    label = font.render(text, True, color)
    screen.blit(label, pos)

# Intro screen
def show_intro():
    pygame.mixer.music.load("assets/sounds/title_theme.wav")
    pygame.mixer.music.play(-1)
    blink = True
    blink_timer = 0
    while True:
        screen.blit(bg_img, (0, 0))
        screen.blit(pan_img, (350, 400))
        render_text_with_border("NEON CHEF", title_font, (255, 100, 0), (0, 0, 0), (WIDTH//2 - 180, 100))
        if blink:
            render_text_with_border("Press SPACE to Start", prompt_font, (0, 255, 255), (0, 0, 0), (WIDTH//2 - 200, 300))
        blink_timer += 1
        if blink_timer >= 30:
            blink = not blink
            blink_timer = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.mixer.music.stop()
                return
        pygame.display.flip()
        clock.tick(60)

# Game Over screen
def show_game_over(final_score):
    high_score = load_high_score()
    if final_score > high_score:
        save_high_score(final_score)
        high_score = final_score
    game_over_fx.play()
    blink = True
    blink_timer = 0
    while True:
        screen.fill((10, 10, 10))
        render_text_with_border("GAME OVER", title_font, (255, 0, 0), (0, 0, 0), (WIDTH//2 - 150, 100))
        render_text_with_border(f"Your Score: {final_score}", game_font, (255, 255, 255), (0, 0, 0), (WIDTH//2 - 160, 180))
        render_text_with_border(f"High Score: {high_score}", game_font, (255, 215, 0), (0, 0, 0), (WIDTH//2 - 160, 240))
        if blink:
            render_text_with_border("Press R to Restart", prompt_font, (0, 255, 255), (0, 0, 0), (WIDTH//2 - 160, 320))
        blink_timer += 1
        if blink_timer >= 30:
            blink = not blink
            blink_timer = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return
        pygame.display.flip()
        clock.tick(60)

# Game loop
def run_game():
    pan_x, pan_y = 350, 500
    pan_speed = 7
    score, combo, timer = 0, 0, 60
    falling, splashes = [], []
    spawn_rate = 1000
    last_spawn = pygame.time.get_ticks()
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    running = True
    while running:
        screen.blit(bg_img, (0, 0))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: pan_x -= pan_speed
        if keys[pygame.K_RIGHT]: pan_x += pan_speed
        pan_x = max(0, min(pan_x, WIDTH - 100))
        screen.blit(pan_img, (pan_x, pan_y))

        if pygame.time.get_ticks() - last_spawn > spawn_rate:
            name = random.choice(list(ingredients.keys()))
            x = random.randint(0, WIDTH - 60)
            y = -60
            speed = random.randint(4, 7)
            falling.append({"name": name, "x": x, "y": y, "speed": speed})
            last_spawn = pygame.time.get_ticks()

        for item in falling[:]:
            item["y"] += item["speed"]
            screen.blit(ingredients[item["name"]], (item["x"], item["y"]))
            item_rect = pygame.Rect(item["x"], item["y"], 60, 60)
            pan_rect = pygame.Rect(pan_x, pan_y, 100, 100)
            if item_rect.colliderect(pan_rect):
                sizzle.play()
                splashes.append({"x": item["x"], "y": item["y"], "timer": 10})
                if item["name"] == "Pepper":
                    score += 5
                    combo += 2
                else:
                    score += 1 + combo
                    combo += 1
                falling.remove(item)
            elif item["y"] > HEIGHT:
                combo = 0
                falling.remove(item)

        for splash in splashes[:]:
            screen.blit(splash_img, (splash["x"], splash["y"]))
            splash["timer"] -= 1
            if splash["timer"] <= 0:
                splashes.remove(splash)

        render_text_with_border(f"Time: {timer}s", game_font, (255, 255, 0), (0, 0, 0), (30, 30))
        render_text_with_border(f"Combo: {combo}", game_font, (0, 255, 255), (0, 0, 0), (30, 80))
        render_text_with_border(f"Score: {score}", game_font, (255, 0, 0), (0, 0, 0), (30, 130))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.USEREVENT:
                timer -= 1
                if timer <= 0:
                    running = False

        pygame.display.flip()
        clock.tick(60)

    show_game_over(score)

# 🚀 Launch everything
while True:
    show_intro()
    run_game()