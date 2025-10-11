import pygame

from pygame_visor import Visor, VisorMode
from common import App


def main():
    app = App()

    view = Visor(
        VisorMode.RegionLetterbox,
        app.screen.get_rect(),
        region=(0, 0, 400, 300),
        limits=app.extended_limits(10),
    )

    view.move_to(app.player_pos.center)

    font = pygame.Font(pygame.font.get_default_font(), 16)

    for delta in app.loop(60):
        view.move_to(app.player_pos.center)

        bbox = view.get_bounding_box()
        view.render(app.screen, app.get_tiles_for_bbox(app.tiles, bbox))

        # highlight mouse position

        mouse_pos = pygame.mouse.get_pos()
        mw_x, mw_y = view.screen_to_world(mouse_pos)

        col, row = app.get_tile((mw_x, mw_y))
        data = app.tiles.get((col, row))
        if data is not None:
            tx, ty, tile_surf = data
            tmp = tile_surf.copy()
            tmp.fill((0, 128, 255))
            view.render(app.screen, [((tx, ty), tmp)])

            index_surf = font.render(f"({col}, {row})", True, "black")
            # get screen coords, and blit directly into the screen, to prevent scaling of the text
            sx, sy = view.world_to_screen((tx, ty))
            app.screen.blit(index_surf, (sx + 2, sy + 5))

        # render palyer last.
        view.render(app.screen, [(app.player_pos.topleft, app.player_surf)])


if __name__ == "__main__":
    main()
