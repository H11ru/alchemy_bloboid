import pygame
import random
import betterfont
import math

pygame.init()
WIDTH, HEIGHT = 1200, 900
window = pygame.display.set_mode((WIDTH, HEIGHT))
screen = pygame.Surface((WIDTH, HEIGHT)).convert() # convert will turn it into a format that is faster to blit
pygame.display.set_caption("i dont know yet")

# Define areas
MINE_RECT = pygame.Rect(0, 0, 600, 600)
INVENTORY_RECT = pygame.Rect(WIDTH // 2, 0, WIDTH // 2, HEIGHT // 2)
CRAFT_RECT = pygame.Rect(0, 600, WIDTH // 2, HEIGHT - 600)
GARDEN_RECT = pygame.Rect(WIDTH // 2, HEIGHT // 2, WIDTH // 2, HEIGHT // 2)

FONT = betterfont.Font(font="./pXld.ttf", font_size=18, color=(255,255,255), border_color=(0,0,0), border_thickness=3)
BOOM_FONT = betterfont.Font(font="./pXld.ttf", font_size=36, color=(255,255,255), border_color=(0,0,0), border_thickness=3)
BIG_FONT = betterfont.Font(font="./pXld.ttf", font_size=26, color=(255,255,255), border_color=(0,0,0), border_thickness=3)
REGEN_BUTTON_FONT = betterfont.Font(font="./pXld.ttf", font_size=15, color=(0,0,0), border_color=(255,255,255), border_thickness=3)

# Mine setup
MINE_SIZE = 16
MINE_CELL_SIZE = 37

TINY = 2 # Tiny. I dont know what this was for, but making it 0 causes the tiles to shift upy and left cusing the bottom and right of the mine ot have a gap and the top and left most tiels to be in the boundary


# Inventory
inventory = {}

# Crafting
craft_slots = [None, None]
dragging = None
drag_offset = (0, 0)

# Garden
plants = []
plant_growth_timer = 15
plant_max = 12
plant_types = ['coilgrass', 'nightbloom']

# Recipes
def arrange(*stuff): return tuple(sorted(stuff))
recipes = {
    arrange('rock', 'quartzium'): 'crystal',
}

# Boom texts
boom_texts = []

def regen_mine():
    global mine_grid, mine_fog
    # Adjust weights: [rock, quartzium, dirt]
    resources = ['rock', 'quartzium', 'dirt']
    weights = [0.5, 0.1, 0.4] # 40% dirt, 50% rock, 10% quartzium
    mine_grid = [
        [random.choices(resources, weights)[0] for _ in range(MINE_SIZE)]
        for _ in range(MINE_SIZE)
    ]
    mine_fog = [[True if y > 0 else False for x in range(MINE_SIZE)] for y in range(MINE_SIZE)]  # Only first row visible

    # topleft has 3 tiles that are unavailable because the regen button is in the way
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
    if y == 0 and x in (0,1,2):
        return None, None
    if 0 <= x < MINE_SIZE and 0 <= y < MINE_SIZE:
        return x, y
    return None, None

def load_asset(path, fallback_color, size=(60, 60), text=None, suppress_warning=False):
    try:
        img = pygame.image.load(path).convert_alpha()
        # the images are 64x64 pixelart
        img = pygame.transform.scale(img, size) # Scale the image to the desired size without smoothing since it's pixel art
        return img
    except Exception:
        if not suppress_warning:
            print(f"[WARN] Failed to load {path}, using a placeholder.")
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(fallback_color)
        if text:
            label = FONT.render(text)
            surf.blit(label, (5, 5))
        return surf

# Load assets or use placeholders
ASSETS = {
    "rock": load_asset("rock.png", (120,120,120), text="rock"),
    "quartzium": load_asset("quartzite_item.png", (220,220,220), text="quartz"),
    "dirt": load_asset("dirt.png", (150,100,50), text="dirt"),
    "coilgrass": load_asset("coilgrass.png", (0,200,0), text="CG"),
    "crystal": load_asset("crystal.png", (180,180,255), text="crys"),
    "nightbloom": load_asset("nightbloom.png", (100,0,150), text="NB"),
    "error": pygame.Surface((60,60)),
}
ASSETS_MINE = {
    "rock": load_asset("rock.png", (120,120,120), text="rock"),
    "quartzium": load_asset("quartzite.png", (220,220,220), text="quartz"),
    "dirt": load_asset("dirt.png", (150,100,50), text="dirt"),
    "air": load_asset("air.png", (200,200,255), suppress_warning=True),
    "error": pygame.Surface((60,60)),
}
ASSETS["error"].fill((255, 0, 255))
pygame.draw.rect(ASSETS["error"], (0, 0, 0), (0, 0, 30, 30))
pygame.draw.rect(ASSETS["error"], (0, 0, 0), (30, 30, 30, 30))
frame = 0

def foggy(y, x, frame):
    # fun shader. oscillates between (90,90,90) and (120, 120, 120) based on position and framea nd sine wave
    base = 115 + 15 * math.sin((frame + x*5 + y*10) * 0.1)
    return (base, base, base)
magicfilm = pygame.Surface((MINE_RECT.width, MINE_RECT.height), pygame.SRCALPHA)
def draw_mine():
    global frame
    for y in range(MINE_SIZE):
        for x in range(MINE_SIZE):
            rect = pygame.Rect(MINE_RECT.x + x*MINE_CELL_SIZE + TINY, MINE_RECT.y + y*MINE_CELL_SIZE + TINY, MINE_CELL_SIZE, MINE_CELL_SIZE)
            if not mine_fog[y][x]:
                mat = mine_grid[y][x]
                screen.blit(pygame.transform.smoothscale(ASSETS_MINE.get(mat, ASSETS_MINE["error"]), (MINE_CELL_SIZE, MINE_CELL_SIZE)), rect.topleft)
    # magic film
    global magicfilm
    magicfilm.fill((0, 0, 0, 90))
    if pickswing > 0:
        screen.blit(magicfilm, MINE_RECT.topleft)

    for y in range(MINE_SIZE):
        for x in range(MINE_SIZE):
            rect = pygame.Rect(MINE_RECT.x + x*MINE_CELL_SIZE + TINY, MINE_RECT.y + y*MINE_CELL_SIZE + TINY, MINE_CELL_SIZE, MINE_CELL_SIZE)
            if mine_fog[y][x]:
                pygame.draw.rect(screen, foggy(y, x, frame), rect)
            pygame.draw.rect(screen, (30,30,30), rect, 1)


    # Regen button
    btn_rect = pygame.Rect(MINE_RECT.x+9, MINE_RECT.y+7, 100, 30)
    pygame.draw.rect(screen, (180,180,0), btn_rect)
    screen.blit(REGEN_BUTTON_FONT.render("Regen"), (btn_rect.x+10, btn_rect.y+5))
    return btn_rect

numberwriter = betterfont.Font(surf=None, font="./pXld.ttf", font_size=20, color=(255,255,255), border_color=(0,0,0), border_thickness=4)

def draw_inventory():
    x, y = INVENTORY_RECT.x + 20, INVENTORY_RECT.y + 20
    for mat, count in inventory.items():
        if count > 0:
            screen.blit(ASSETS.get(mat, ASSETS["error"]), (x, y))
            im = numberwriter.render(str(count))
            screen.blit(im, (x+20, y+40))
            x += 80

def fire():
    hue = random.randint(0, 60)
    # hsv
    retval = pygame.Color(0)
    retval.hsva = (hue, 100, 100)
    return retval

def draw_crafting():
    slot_rects = []
    for i in range(2):
        rect = pygame.Rect(CRAFT_RECT.x + 60 + i*120, CRAFT_RECT.y + 60, 100, 100)
        pygame.draw.rect(screen, (220,220,100), rect, 3)
        if craft_slots[i]:
            # center a 60x60 image in the 100x100 slot: add +20
            centered = (rect.x + 20, rect.y + 20)
            screen.blit(ASSETS.get(craft_slots[i], ASSETS["error"]), centered)
        slot_rects.append(rect)
    # Combine button
    btn_rect = pygame.Rect(CRAFT_RECT.x + 300, CRAFT_RECT.y + 90, 120, 50)
    pygame.draw.rect(screen, (255,255,0), btn_rect)
    screen.blit(FONT.render("Combine"), (btn_rect.x+10, btn_rect.y+10))
    return slot_rects, btn_rect

def draw_garden():
    for plant in plants:
        # use the plant type texture
        screen.blit(ASSETS.get(plant['type'], ASSETS["error"]), plant['rect'].topleft)
        #pygame.draw.rect(screen, (0,150,0), plant['rect'], 2)

def draw_booms():
    for boom in boom_texts:
        txt, pos, color = boom['txt'], boom['pos'], boom['color']
        BOOM_FONT.color = color
        screen.blit(BOOM_FONT.render(txt), pos)

def update_booms():
    for boom in boom_texts:
        boom['pos'][0] += boom['vel'][0]
        boom['pos'][1] += boom['vel'][1]
        boom['vel'][1] += 0.1  # Gravity
        boom['life'] -= 1
    boom_texts[:] = [b for b in boom_texts if b['life'] > 0]

pickswing = 0
strength = {
    'rock': 15,
    'quartzium': 40,
    'dirt': 5,
}

clock = pygame.time.Clock()
running = True
pickswing = 0
mouse_still_for = 0
while running:
    dt = clock.tick(60)
    frame += 1
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
            if x is not None and y is not None and not mine_fog[y][x] and pickswing <= 0:
                mat = mine_grid[y][x]
                if mat != 'air':  # Only add real materials
                    inventory[mat] = inventory.get(mat, 0) + 1
                    pickswing = strength[mat]
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
                        for _ in range(15):
                            boom_texts.append({
                                'txt': "Yay!",
                                'pos': [combine_btn.x+random.randint(-30,100), combine_btn.y+random.randint(-30,30)],
                                'vel': [random.uniform(-3,3), random.uniform(-5,1)],
                                'color': (137, 235, 255), # light blue
                                'life': 120
                            })
                    else:
                        for _ in range(45):
                            boom_texts.append({
                                'txt': "BOOM!",
                                'pos': [combine_btn.x+random.randint(-30,100), combine_btn.y+random.randint(-30,30)],
                                'vel': [random.uniform(-16,16), random.uniform(-18,9)],
                                'color': fire(),
                                'life': 60
                            })
                        craft_slots = [None, None]
            # Garden
            for plant in plants[:]:
                if plant['rect'].collidepoint(mx, my):
                    inventory[plant['type']] = inventory.get(plant['type'], 0) + 1
                    plants.remove(plant)
            # Crafting slots
            if event.button == 3:  # Right click to remove from slot
                for i, rect in enumerate(slot_rects):
                    if rect.collidepoint(mx, my) and craft_slots[i]:
                        inventory[craft_slots[i]] += 1
                        craft_slots[i] = None
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
        elif event.type == pygame.MOUSEMOTION:
            mouse_still_for = 0

    mouse_still_for += 1

    plant_growth_timer -= 0.15
    if plant_growth_timer <= 0 and len(plants) < plant_max:
        px = random.randint(GARDEN_RECT.x + 20, GARDEN_RECT.x + GARDEN_RECT.width - 80)
        py = random.randint(
            GARDEN_RECT.y + GARDEN_RECT.height // 2 + 20,
            GARDEN_RECT.y + GARDEN_RECT.height - 80
        )
        plants.append({'rect': pygame.Rect(px, py, 60, 60), 'type': random.choice(plant_types)})
        plant_growth_timer = random.randint(30, 180)

    if pickswing > 0:
        pickswing -= 1

    update_booms()

    screen.fill((40,40,40))
    regen_btn = draw_mine()
    draw_inventory()
    slot_rects, combine_btn = draw_crafting()
    pygame.draw.rect(screen, (171, 205, 239), (GARDEN_RECT.x, GARDEN_RECT.y, GARDEN_RECT.width, GARDEN_RECT.height))
    pygame.draw.rect(screen, (71, 205, 91), (GARDEN_RECT.x, GARDEN_RECT.y + GARDEN_RECT.height // 2, GARDEN_RECT.width, GARDEN_RECT.height // 2))
    pygame.draw.line(screen, (0,0,0), (GARDEN_RECT.x, GARDEN_RECT.y + GARDEN_RECT.height // 2), (GARDEN_RECT.x + GARDEN_RECT.width, GARDEN_RECT.y + GARDEN_RECT.height // 2), 3)
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
        screen.blit(ASSETS.get(dragging, ASSETS["error"]), (mx - drag_offset[0], my - drag_offset[1]))
    else:
        # hover logic
        if mouse_still_for > 30:
            # are we on inventory?
            mx, my = pygame.mouse.get_pos()
            if INVENTORY_RECT.collidepoint(mx, my):
                inv_x, inv_y = INVENTORY_RECT.x + 20, INVENTORY_RECT.y + 20
                tooltip_left = mx + 20
                tooltip_top = my + 20
                for mat, count in inventory.items():
                    if count > 0:
                        rect = pygame.Rect(inv_x, inv_y, 60, 60)
                        if rect.collidepoint(mx, my):
                            info_lines = [
                                f"Name={mat.replace("_", " ").title()}",
                                f"Amount={count}",
                            ]
                            if mat in strength:
                                info_lines.append(f"Mining Strength={strength[mat]}")
                            #pygame.draw.rect(screen, (0,0,0), (tooltip_left, tooltip_top, 200, 30 + 30*len(info_lines)), border_radius=5)
                            # calculate bounds
                            box_top = tooltip_top
                            box_left = tooltip_left
                            box_width = max([FONT.font.size(line)[0] for line in info_lines]) + 20
                            box_height = 20 + 30*len(info_lines)
                            # check collision with right edge of screen
                            go_left = 0
                            if box_left + box_width > WIDTH:
                                # shift box left instead
                                box_left = mx - 20 - box_width
                                go_left = -20 - box_width - 15
                            transparancybox = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
                            transparancybox.fill((0,0,0,0))
                            #pygame.draw.rect(screen, (0,0,0), (box_left, box_top, box_width, box_height), border_radius=5)
                            pygame.draw.rect(transparancybox, (0,0,0,200), (0, 0, box_width, box_height), border_radius=5)
                            screen.blit(transparancybox, (box_left, box_top))
                            for i, line in enumerate(info_lines):
                                screen.blit(FONT.render(line), (tooltip_left + 10 + go_left, tooltip_top + i*30 + 10))
                            break
                        inv_x += 80

    window.blit(screen, (0,0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()