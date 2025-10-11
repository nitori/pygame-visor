import pygame

from pygame_visor import Visor, VisorMode, WorldPos
from common import App


def main():
    app = App()

    view = Visor(
        VisorMode.RegionLetterbox,
        app.screen.get_rect(),
        region=(0, 0, 400, 300),
    )
    bg_view = Visor(
        VisorMode.RegionExpand,
        app.screen.get_rect(),
        region=(0, 0, 400, 300),
    )
    bg_view_factor = 0.5

    def t(pos: WorldPos) -> WorldPos:
        return pos[0] * bg_view_factor, pos[1] * bg_view_factor

    local_limits = app.extended_limits(-50)
    app.player_pos.center = local_limits[0], local_limits[1]

    view.move_to(app.player_pos.center)
    bg_view.move_to(t(app.player_pos.center))

    # a layer of "smoke"
    smoky_surf = pygame.Surface(app.screen.size, pygame.SRCALPHA)
    smoky_surf.fill((64, 64, 64, 128))

    for delta in app.loop(60):
        view.move_to(app.player_pos.center)
        bg_view.move_to(t(app.player_pos.center))

        bbox = bg_view.get_bounding_box()
        bg_view.render(app.screen, app.get_tiles_for_bbox(app.tiles, bbox))

        # just dump it on top of the entire screen, so the bg is not as bright as the fg.
        app.screen.blit(smoky_surf, (0, 0))

        bbox = view.get_bounding_box()
        view.render(app.screen, app.get_tiles_for_bbox(app.tiles, bbox))

        view.render(app.screen, [(app.player_pos.topleft, app.player_surf)])


if __name__ == "__main__":
    main()
