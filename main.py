import pygame
import random

pygame.init()
WIDTH, HEIGHT = 1200, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Alchemy Game")

# Define areas
MINE_RECT = pygame.Rect(0, 0, 600, 600)
INVENTORY_RECT = pygame.Rect(WIDTH // 2, 0, WIDTH // 2, HEIGHT // 2)
CRAFT_RECT = pygame.Rect(0, 600, WIDTH // 2, HEIGHT - 600)
GARDEN_RECT = pygame.Rect(WIDTH // 2, HEIGHT // 2, WIDTH // 2, HEIGHT // 2)

FONT = pygame.font.SysFont("consolas", 24)
BIG_FONT = pygame.font.SysFont("consolas", 36)

# Mine setup
MINE_SIZE = 16
MINE_CELL_SIZE = 37

TINY = 2 # Tiny. I dont know what this was for, but making it 0 causes the tiles to shift upy and left cusing the bottom and right of the mine ot have a gap and the top and left most tiels to be in the boundary


# Inventory
inventory = {'rock': 5, 'quartzium': 2, 'other': 0}

# Crafting
craft_slots = [None, None]
dragging = None
drag_offset = (0, 0)

# Garden
plants = [{'rect': pygame.Rect(WIDTH//2 + 50 + i*80, HEIGHT//2 + 100, 60, 60), 'type': 'herb'} for i in range(4)]

# Recipes
def arrange(*stuff): return tuple(sorted(stuff))
recipes = {
    arrange('rock', 'quartzium'): 'crystal',
}

# Boom texts
boom_texts = []

def regen_mine():
    global mine_grid, mine_fog
    mine_grid = [[random.choice(['rock', 'quartzium', 'other']) for _ in range(MINE_SIZE)] for _ in range(MINE_SIZE)]
    mine_fog = [[True if y > 0 else False for x in range(MINE_SIZE)] for y in range(MINE_SIZE)]  # Only first row visible

    # topleft has 3 tiles that are unavailable becayse the regen button is in thwe way
    mine_grid[0][0] = 'air'
    mine_grid[0][1] = 'air'
    mine_grid[0][2] = 'air'
regen_mine()



def get_mine_cell(mx, my):
    if not MINE_RECT.collidepoint(mx, my):
        return None, None
    x = (mx - MINE_RECT.x - TINY) // MINE_CELL_SIZE
    y = (my - MINE_RECT.y - TINY) // MINE_CELL_SIZE
    # throw away the top 3 tiles covered by the regen button
    if x == 0 and y in (0,1,2):
        return None, None
    if 0 <= x < MINE_SIZE and 0 <= y < MINE_SIZE:
        return x, y
    return None, None

def load_asset(path, fallback_color, size=(60, 60), text=None, suppress_warning=False):
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        if not suppress_warning:
            print(f"[WARN] Failed to load {path}, using a placeholder.")
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(fallback_color)
        if text:
            label = FONT.render(text, True, (0,0,0))
            surf.blit(label, (5, 5))
        return surf

# Load assets or use placeholders
ASSETS = {
    "rock": load_asset("rock.png", (120,120,120), text="rock"),
    "quartzium": load_asset("quartzium.png", (220,220,220), text="quartz"),
    "other": load_asset("other.png", (150,100,50), text="other"),
    "herb": load_asset("herb.png", (0,200,0), text="herb"),
    "crystal": load_asset("crystal.png", (180,180,255), text="crys"),
    "air": load_asset("air.png", (200,200,255), suppress_warning=True),
    "error": pygame.Surface((60,60)),
}
ASSETS["error"].fill((255, 0, 255))
pygame.draw.rect(ASSETS["error"], (0, 0, 0), (0, 0, 30, 30))
pygame.draw.rect(ASSETS["error"], (0, 0, 0), (30, 30, 30, 30))

def draw_mine():
    for y in range(MINE_SIZE):
        for x in range(MINE_SIZE):
            rect = pygame.Rect(MINE_RECT.x + x*MINE_CELL_SIZE + TINY, MINE_RECT.y + y*MINE_CELL_SIZE + TINY, MINE_CELL_SIZE, MINE_CELL_SIZE)
            if mine_fog[y][x]:
                pygame.draw.rect(screen, (60, 60, 60), rect)
            else:
                mat = mine_grid[y][x]
                screen.blit(pygame.transform.smoothscale(ASSETS.get(mat, ASSETS["error"]), (MINE_CELL_SIZE, MINE_CELL_SIZE)), rect.topleft)
            pygame.draw.rect(screen, (30,30,30), rect, 1)
    # Regen button
    btn_rect = pygame.Rect(MINE_RECT.x+9, MINE_RECT.y+7, 100, 30)
    pygame.draw.rect(screen, (180,180,0), btn_rect)
    screen.blit(FONT.render("Regen", True, (0,0,0)), (btn_rect.x+10, btn_rect.y+5))
    return btn_rect

def draw_inventory():
    x, y = INVENTORY_RECT.x + 20, INVENTORY_RECT.y + 20
    for mat, count in inventory.items():
        if count > 0:
            screen.blit(ASSETS.get(mat, ASSETS["other"]), (x, y))
            screen.blit(FONT.render(str(count), True, (0,0,0)), (x+20, y+40))
            x += 80

def draw_crafting():
    slot_rects = []
    for i in range(2):
        rect = pygame.Rect(CRAFT_RECT.x + 60 + i*120, CRAFT_RECT.y + 60, 100, 100)
        pygame.draw.rect(screen, (220,220,100), rect, 3)
        if craft_slots[i]:
            pygame.draw.rect(screen, (180,180,180), rect.inflate(-10,-10))
            screen.blit(FONT.render(craft_slots[i], True, (0,0,0)), rect.inflate(-10,-10).topleft)
        slot_rects.append(rect)
    # Combine button
    btn_rect = pygame.Rect(CRAFT_RECT.x + 300, CRAFT_RECT.y + 90, 120, 50)
    pygame.draw.rect(screen, (255,255,0), btn_rect)
    screen.blit(FONT.render("Combine", True, (0,0,0)), (btn_rect.x+10, btn_rect.y+10))
    return slot_rects, btn_rect

def draw_garden():
    for plant in plants:
        pygame.draw.ellipse(screen, (0,200,0), plant['rect'])
        screen.blit(FONT.render("Plant", True, (0,0,0)), plant['rect'].move(0,20).topleft)

def draw_booms():
    for boom in boom_texts:
        txt, pos, color = boom['txt'], boom['pos'], boom['color']
        screen.blit(FONT.render(txt, True, color), pos)

def update_booms():
    for boom in boom_texts:
        boom['pos'][0] += boom['vel'][0]
        boom['pos'][1] += boom['vel'][1]
        boom['life'] -= 1
    boom_texts[:] = [b for b in boom_texts if b['life'] > 0]

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Regen mine
            if regen_btn.collidepoint(mx, my):
                regen_mine()
            # Mine tile click
            x, y = get_mine_cell(mx, my)
            if x is not None and y is not None and not mine_fog[y][x]:
                mat = mine_grid[y][x]
                if mat != 'air':  # Only add real materials
                    inventory[mat] = inventory.get(mat, 0) + 1
                mine_grid[y][x] = 'air'
                # Reveal adjacent tiles
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < MINE_SIZE and 0 <= ny < MINE_SIZE:
                        mine_fog[ny][nx] = False
            # Inventory drag
            inv_x, inv_y = INVENTORY_RECT.x + 20, INVENTORY_RECT.y + 20
            for mat, count in inventory.items():
                if count > 0:
                    rect = pygame.Rect(inv_x, inv_y, 60, 60)
                    if rect.collidepoint(mx, my):
                        dragging = mat
                        drag_offset = (mx - rect.x, my - rect.y)
                        inventory[mat] -= 1
                        break
                    inv_x += 80
            
            # Combine
            if combine_btn.collidepoint(mx, my):
                if craft_slots[0] and craft_slots[1]:
                    key = tuple(sorted([craft_slots[0], craft_slots[1]]))
                    if key in recipes:
                        result = recipes[key]
                        inventory[result] = inventory.get(result, 0) + 1
                        craft_slots = [None, None]
                    else:
                        for _ in range(15):
                            boom_texts.append({
                                'txt': "BOOM!",
                                'pos': [combine_btn.x+random.randint(-30,100), combine_btn.y+random.randint(-30,30)],
                                'vel': [random.uniform(-2,2), random.uniform(-2,2)],
                                'color': (random.randint(200,255), random.randint(0,100), 0),
                                'life': random.randint(20,40)
                            })
                        craft_slots = [None, None]
            # Garden
            for plant in plants[:]:
                if plant['rect'].collidepoint(mx, my):
                    inventory['herb'] = inventory.get('herb', 0) + 1
                    plants.remove(plant)
        elif event.type == pygame.MOUSEBUTTONUP:
            # Crafting slots
            for i, rect in enumerate(slot_rects):
                if rect.collidepoint(mx, my) and dragging:
                    if craft_slots[i]:
                        inventory[craft_slots[i]] += 1
                    craft_slots[i] = dragging
                    dragging = None
            if dragging:
                # If not dropped in slot, return to inventory
                inventory[dragging] += 1
                dragging = None


    update_booms()

    screen.fill((40,40,40))
    regen_btn = draw_mine()
    draw_inventory()
    slot_rects, combine_btn = draw_crafting()
    draw_garden()
    draw_booms()
    # Draw thick black boundaries for each sector
    pygame.draw.rect(screen, (0, 0, 0), MINE_RECT, 6)
    pygame.draw.rect(screen, (0, 0, 0), INVENTORY_RECT, 6)
    pygame.draw.rect(screen, (0, 0, 0), CRAFT_RECT, 6)
    pygame.draw.rect(screen, (0, 0, 0), GARDEN_RECT, 6)

    # Draw dragging item
    if dragging:
        mx, my = pygame.mouse.get_pos()
        pygame.draw.rect(screen, (180,180,180), (mx-drag_offset[0], my-drag_offset[1], 60, 60))
        screen.blit(FONT.render(dragging, True, (0,0,0)), (mx-drag_offset[0]+5, my-drag_offset[1]+5))



    pygame.display.flip()
    clock.tick(60)

pygame.quit()