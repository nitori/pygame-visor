"""
common.py – Shared helper code for pygame-visor examples.

This module provides a minimal application framework and utility functions
used across multiple examples. It handles basic Pygame setup, player movement,
world tile generation, and tile fetching based on a visible region.

Not intended for production use—just a simple, reusable base to keep example
code focused on demonstrating viewport/camera functionality.
"""

from collections.abc import Generator
import random
import sys
import os
import inspect

import pygame
from pygame._sdl2.video import Window, Renderer, Texture


from pygame_visor.types import WorldPos, Limits

SEED = 123

type TileIndex = tuple[int, int]  # index as (column, row) pair
type TileTuple[T] = tuple[float, float, T]
type Tiles[T] = dict[TileIndex, TileTuple[T]]


class App[TileT]:
    use_sdl2: bool
    tiles: Tiles[TileT]

    # use_sdl2 == False
    screen: pygame.Surface
    player_surf: TileT
    player2_surf: TileT | None

    # use_sdl2 == True
    window: Window
    renderer: Renderer

    def __init__(
        self,
        size: tuple[int, int] = (800, 600),
        *,
        resizable=False,
        second_player=False,
        use_sdl2=False,
    ):
        pygame.init()

        flags = 0
        if resizable:
            flags = pygame.RESIZABLE

        filename = "<unknown>"
        if sys.argv and sys.argv[0]:
            filename = os.path.basename(sys.argv[0])
        if not filename:
            stack = inspect.stack()
            if len(stack) >= 2:
                calling_file = stack[1].filename
                filename = os.path.basename(calling_file)

        caption = f"pygame-visor example {filename} - Python {sys.version}"

        self.use_sdl2 = use_sdl2
        if use_sdl2:
            print("init window")
            self.window = Window(caption, size=size, resizable=resizable)
            print("init renderer")
            self.renderer = Renderer(self.window, accelerated=1, vsync=True)
            print("done")
        else:
            self.screen = pygame.display.set_mode(size, flags)
            pygame.display.set_caption(caption)

        self.clock = pygame.Clock()

        self.rows = 150
        self.columns = 150
        self.tile_size = 32

        self.offset = (
            -(self.rows * self.tile_size) / 2,
            -(self.columns * self.tile_size) / 2,
        )

        self.tiles = self.generate_world_tiles()

        self.limits = (
            self.offset[0],
            self.offset[1],
            self.offset[0] + self.columns * self.tile_size,
            self.offset[1] + self.rows * self.tile_size,
        )

        self.speed = 200

        # world size
        self.player_surf = pygame.Surface((10, 10))
        self.player_surf.fill("red")
        if self.use_sdl2:
            self.player_surf = Texture.from_surface(self.renderer, self.player_surf)

        # world pos
        self.player_pos = self.player_surf.get_rect(center=(0, 0))

        self.second_player = second_player
        self.player2_surf = None
        self.player2_tex = None
        self.player2_pos = None
        if second_player:
            self.player2_surf = pygame.Surface((10, 10))
            self.player2_surf.fill("blue")
            self.player2_pos = self.player2_surf.get_rect(center=(20, 0))
            if self.use_sdl2:
                self.player2_surf = Texture.from_surface(
                    self.renderer, self.player2_surf
                )

    def generate_world_tiles(self) -> Tiles[TileT]:
        """
        size in number of (rows, columns)
        offset in (x,y) world coordinates.
        tile_size integer of size in world coordinates.

        returns list of tile-tuples: (world_x, world_y, tile_surf)
        """

        random.seed(SEED)

        off_x, off_y = self.offset

        tiles = {}
        for row in range(self.rows):
            for column in range(self.columns):
                tone = random.randint(64, 240)
                tile = pygame.Surface((self.tile_size, self.tile_size))
                tile.fill((tone, 255, tone))
                if self.use_sdl2:
                    tile = Texture.from_surface(self.renderer, tile)
                tiles[(column, row)] = (
                    off_x + column * self.tile_size,
                    off_y + row * self.tile_size,
                    tile,
                )
        return tiles

    def get_tiles_for_bbox(
        self, tiles: Tiles[TileT], bbox: pygame.FRect
    ) -> Generator[tuple[tuple[float, float], TileT]]:
        """
        This yields all the tiles visible.
        Big regions possibly take a long time to render, so in any proper application,
        you'd likely "chunk" the world into larger areas.
        This is just a simple demo.
        """
        left_column, top_row = self.get_tile(bbox.topleft)
        right_column, bottom_row = self.get_tile(bbox.bottomright)

        # Some debugging left here
        # size_x = right_column - left_column + 1
        # size_y = bottom_row - top_row + 1
        # print(f'Requesting {size_x * size_y} tiles.')

        for row in range(top_row, bottom_row + 1):
            for column in range(left_column, right_column + 1):
                if data := tiles.get((column, row)):
                    x, y, surf_or_tex = data
                    yield (x, y), surf_or_tex

    def get_tile(self, pos: WorldPos) -> TileIndex:
        x, y = map(int, pos)
        column = int(x - self.offset[0]) // self.tile_size
        row = int(y - self.offset[1]) // self.tile_size
        return column, row

    def extended_limits(self, value) -> Limits:
        return (
            self.limits[0] - value,
            self.limits[1] - value,
            self.limits[2] + value,
            self.limits[3] + value,
        )

    @staticmethod
    def get_input_vector(wasd: tuple[int, int, int, int]) -> pygame.Vector2:
        up, left, down, right = wasd
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(keys[right] - keys[left], keys[down] - keys[up])
        if direction.length_squared() > 1:
            direction.normalize_ip()
        return direction

    def loop(self, fps: int, callback=None):
        frames = 0
        acc_deltas = 0
        font = pygame.Font(pygame.font.get_default_font())
        fps_surf = font.render(f"FPS: {frames}", True, "white", "black")

        if self.use_sdl2:
            self.renderer.draw_color = 0, 0, 0, 255
            fps_surf = Texture.from_surface(self.renderer, fps_surf)

        while True:
            frames += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if callback:
                    callback(event)

            delta = self.clock.tick(fps) / 1000

            direction = self.get_input_vector(
                (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d)
            )
            if direction:
                self.player_pos.center += direction * self.speed * delta

            if self.second_player:
                direction2 = self.get_input_vector(
                    (pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT)
                )
                if direction2:
                    self.player2_pos.center += direction2 * self.speed * delta

            if self.use_sdl2:
                self.renderer.clear()
            else:
                self.screen.fill("black")

            yield delta

            acc_deltas += delta
            if acc_deltas > 1.0:
                acc_deltas -= 1.0
                fps_surf = font.render(f"FPS: {frames}", True, "white", "black")
                if self.use_sdl2:
                    fps_surf = Texture.from_surface(self.renderer, fps_surf)
                frames = 0

            if self.use_sdl2:
                fps_surf.draw(dstrect=(10, 50))
                self.renderer.present()
            else:
                self.screen.blit(fps_surf, (10, 50))
                pygame.display.flip()
