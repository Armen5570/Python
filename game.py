
import random
import pygame

CELL = 24
COLS = 25
ROWS = 20
HUD = 60
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + HUD
FPS = 12

BG = (18, 25, 40)
GRID = (28, 38, 56)
GREEN = (42, 175, 120)
HEAD = (76, 220, 150)
RED = (255, 95, 110)
WHITE = (240, 245, 255)
MUTED = (160, 175, 200)

DIRECTIONS = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_w: (0, -1),
    pygame.K_s: (0, 1),
    pygame.K_a: (-1, 0),
    pygame.K_d: (1, 0),
}


def random_food(snake):
    empty = [
        (x, y)
        for x in range(COLS)
        for y in range(ROWS)
        if (x, y) not in snake
    ]
    return random.choice(empty) if empty else None


def new_game():
    x, y = COLS // 2, ROWS // 2
    snake = [(x, y), (x - 1, y), (x - 2, y)]
    return {
        "snake": snake,
        "direction": (1, 0),
        "next_direction": (1, 0),
        "food": random_food(snake),
        "score": 0,
        "game_over": False,
        "won": False,
        "paused": False,
    }


def draw_cell(screen, cell, color, inset=2):
    x, y = cell
    rect = pygame.Rect(
        x * CELL + inset,
        HUD + y * CELL + inset,
        CELL - inset * 2,
        CELL - inset * 2,
    )
    pygame.draw.rect(screen, color, rect, border_radius=6)


def draw_overlay(screen, fonts, title, subtitle):
    overlay = pygame.Surface(
        (WIDTH, HEIGHT - HUD), pygame.SRCALPHA
    )
    overlay.fill((4, 8, 18, 190))
    screen.blit(overlay, (0, HUD))

    center_x = WIDTH // 2
    center_y = HUD + (HEIGHT - HUD) // 2

    title_img = fonts["title"].render(title, True, WHITE)
    subtitle_img = fonts["small"].render(subtitle, True, MUTED)

    screen.blit(
        title_img,
        title_img.get_rect(center=(center_x, center_y - 22)),
    )
    screen.blit(
        subtitle_img,
        subtitle_img.get_rect(center=(center_x, center_y + 20)),
    )


def draw_game(screen, fonts, game, best_score):
    screen.fill(BG)

    for x in range(COLS + 1):
        pygame.draw.line(
            screen, GRID,
            (x * CELL, HUD), (x * CELL, HEIGHT)
        )

    for y in range(ROWS + 1):
        pygame.draw.line(
            screen, GRID,
            (0, HUD + y * CELL),
            (WIDTH, HUD + y * CELL),
        )

    pygame.draw.rect(screen, (12, 18, 31), (0, 0, WIDTH, HUD))

    score = fonts["hud"].render(
        f"SCORE  {game['score']}", True, WHITE
    )
    best = fonts["small"].render(
        f"BEST  {best_score}", True, MUTED
    )
    screen.blit(score, (16, 9))
    screen.blit(best, (16, 35))

    food = game["food"]
    if food is not None:
        draw_cell(screen, food, RED, 3)
        fx, fy = food
        pygame.draw.circle(
            screen, (255, 200, 205),
            (fx * CELL + CELL // 2,
             HUD + fy * CELL + CELL // 2),
            3,
        )

    for i, segment in enumerate(game["snake"]):
        draw_cell(screen, segment, HEAD if i == 0 else GREEN)

    if game["paused"] and not game["game_over"]:
        draw_overlay(screen, fonts, "PAUSED", "Press P to continue")
    elif game["game_over"]:
        title = "YOU WIN!" if game["won"] else "GAME OVER"
        subtitle = (
            f"Score: {game['score']}  |  "
            "Press SPACE to play again"
        )
        draw_overlay(screen, fonts, title, subtitle)

    pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption("Snake - Python Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    fonts = {
        "hud": pygame.font.Font(None, 28),
        "small": pygame.font.Font(None, 21),
        "title": pygame.font.Font(None, 48),
    }

    game = new_game()
    best_score = 0

    move_event = pygame.USEREVENT + 1
    pygame.time.set_timer(move_event, int(1000 / FPS))
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    if game["game_over"]:
                        game = new_game()

                elif event.key == pygame.K_p:
                    if not game["game_over"]:
                        game["paused"] = not game["paused"]

                elif event.key in DIRECTIONS:
                    if not game["game_over"] and not game["paused"]:
                        requested = DIRECTIONS[event.key]
                        current = game["direction"]

                        
                        if requested != (-current[0], -current[1]):
                            game["next_direction"] = requested

            elif event.type == move_event:
                if game["game_over"] or game["paused"]:
                    continue

                game["direction"] = game["next_direction"]
                dx, dy = game["direction"]
                hx, hy = game["snake"][0]
                new_head = (hx + dx, hy + dy)

               
                if not (
                    0 <= new_head[0] < COLS
                    and 0 <= new_head[1] < ROWS
                ):
                    game["game_over"] = True
                    continue

                eating = new_head == game["food"]

                
                body = (
                    game["snake"]
                    if eating
                    else game["snake"][:-1]
                )

                if new_head in body:
                    game["game_over"] = True
                    continue

                game["snake"].insert(0, new_head)

                if eating:
                    game["score"] += 1
                    best_score = max(best_score, game["score"])
                    game["food"] = random_food(game["snake"])

                    if game["food"] is None:
                        game["game_over"] = True
                        game["won"] = True
                else:
                    game["snake"].pop()

        draw_game(screen, fonts, game, best_score)
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
