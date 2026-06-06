import pygame

from pygame_visor import Visor, VisorMode
from common import App


def main():
    app = App((1000, 600))

    view = Visor(
        VisorMode.RegionLetterbox,
        app.screen.get_rect(),
        region=(0, 0, 400, 300),
        limits=app.extended_limits(10),
    )

    map_surface = pygame.Surface((100, 75))
    map_view = Visor(
        VisorMode.RegionLetterbox,
        map_surface.get_rect(),
        region=(0, 0, 1000, 750),
        limits=app.limits,
    )

    view.move_to(app.player_pos.center)
    map_view.move_to(app.player_pos.center)

    for delta in app.loop(60):
        view.lerp_to(app.player_pos.center, view.fps_corrected_weight(0.1, delta))
        map_view.move_to(app.player_pos.center)

        bbox = view.get_bounding_box()
        view.render(app.screen, app.get_tiles_for_bbox(app.tiles, bbox))
        view.render(app.screen, [(app.player_pos.topleft, app.player_surf)])

        bbox = map_view.get_bounding_box()
        map_surface.fill("black")
        map_view.render(map_surface, app.get_tiles_for_bbox(app.tiles, bbox))
        map_view.render(map_surface, [(app.player_pos.topleft, app.player_surf)])

        area = view.get_active_screen_area()
        factor = view.get_scaling_factor()
        map_surf_temp = pygame.transform.scale_by(map_surface, factor)
        app.screen.blit(
            map_surf_temp,
            (area.right - map_surf_temp.width, area.bottom - map_surf_temp.height),
        )


if __name__ == "__main__":
    main()
