import pygame
from pygame._sdl2.video import Texture

from pygame_visor import WorldPos
from pygame_visor.video import Visor, VisorMode
from common import App


def main():
    app = App(use_sdl2=True)

    view = Visor(
        VisorMode.RegionLetterbox,
        app.window.size,
        region=(0, 0, 400, 300),
    )
    bg_view = Visor(
        VisorMode.RegionExpand,
        app.window.size,
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
    smoky_surf = pygame.Surface(app.window.size, pygame.SRCALPHA)
    smoky_surf.fill((64, 64, 64, 128))
    smoky_surf = Texture.from_surface(app.renderer, smoky_surf)

    for delta in app.loop(60):
        view.move_to(app.player_pos.center)
        bg_view.move_to(t(app.player_pos.center))

        bbox = bg_view.get_bounding_box()
        bg_view.render(app.renderer, app.get_tiles_for_bbox(app.tiles, bbox))

        # just dump it on top of the entire screen, so the bg is not as bright as the fg.
        # app.screen.blit(smoky_surf, (0, 0))
        smoky_surf.draw(dstrect=(0, 0))

        bbox = view.get_bounding_box()
        view.render(app.renderer, app.get_tiles_for_bbox(app.tiles, bbox))

        view.render(app.renderer, [(app.player_pos.topleft, app.player_surf)])


if __name__ == "__main__":
    main()
