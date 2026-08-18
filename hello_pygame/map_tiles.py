import pygame

pygame.init()

TILE_SIZE = 32
TILE_SPACING = 1
TILE_WIDTH, TILE_HEIGHT = 20, 10
 
WIDTH, HEIGHT = TILE_WIDTH * TILE_SIZE, TILE_HEIGHT * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# tileset.png is a grid of 32x32 tiles
tileset = pygame.image.load("simple_spacing_4_rows.png").convert_alpha()

# Tile IDs in our map
# 0 = grass, 1 = water, 2 = dirt
tile_map = [
    ['c-se', 'horz', 'horz', 'c-sw'],
    ['vert', 'none', 'none', 'vert'],
    ['vert', 'none', 'none', 'vert'],
    ['vert', 'none', 'none', 'vert'],
    ['vert', 'none', 'none', 'vert'],
    ['c-ne', 'horz', 'horz', 'c-nw'],
]

# Where each tile ID is located in the tileset.
# (column, row)
tiles = {
    'cross': (0, 0),
    'c-nw': (1, 0),
    'c-ne': (2, 0),  
    'horz': (3, 0),  
    'T-n': (0, 1),
    'c-se': (1, 1),
    'c-sw': (2, 1),  
    'vert': (3, 1),  
    'T-e': (0, 2),
    'T-s': (1, 2),
    'T-w': (2, 2),
    'none': (3, 2),
}

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("white")

    # Draw the map
    for y, row in enumerate(tile_map):
        for x, tile_id in enumerate(row):

            tx, ty = tiles[tile_id]

            # Account for the 1-pixel spacing between tiles
            source_x = tx * (TILE_SIZE + TILE_SPACING) + TILE_SPACING
            source_y = ty * (TILE_SIZE + TILE_SPACING) + TILE_SPACING

            source_rect = pygame.Rect(
                source_x,
                source_y,
                TILE_SIZE,
                TILE_SIZE,
            )

            # Position on the map
            destination = (
                x * TILE_SIZE,
                y * TILE_SIZE,
            )

            screen.blit(tileset, destination, source_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

