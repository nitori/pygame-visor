import pygame

from pygame_visor import Visor, VisorMode
from common import App


def main():
    app = App(resizable=True)

    surf1 = pygame.Surface((app.screen.width, app.screen.height // 2))
    surf2 = pygame.Surface((app.screen.width, app.screen.height // 2))

    view1 = Visor(
        VisorMode.RegionLetterbox,
        surf1.get_rect(),
        region=(0, 0, 400, 300),
        limits=app.extended_limits(10),
    )
    view2 = Visor(
        VisorMode.RegionExpand,
        surf2.get_rect(),
        region=(0, 0, 400, 300),
        limits=app.extended_limits(10),
    )

    view1.move_to(app.player_pos.center)
    view2.move_to(app.player_pos.center)

    font = pygame.font.Font(pygame.font.get_default_font())
    text1 = font.render(f"{view1.mode}", True, "black", "white")
    text2 = font.render(f"{view2.mode}", True, "black", "white")

    def event_handler(event):
        # eh
        nonlocal surf1, surf2
        if event.type == pygame.VIDEORESIZE:
            surf1 = pygame.Surface((app.screen.width, app.screen.height // 2))
            surf2 = pygame.Surface((app.screen.width, app.screen.height // 2))
            view1.update_screen(surf1.get_rect())
            view2.update_screen(surf2.get_rect())

    for delta in app.loop(60, event_handler):
        view1.lerp_to(app.player_pos.center, view1.fps_corrected_weight(0.1, delta))
        view2.lerp_to(app.player_pos.center, view2.fps_corrected_weight(0.1, delta))

        surf1.fill("black")
        bbox = view1.get_bounding_box()
        view1.render(surf1, app.get_tiles_for_bbox(app.tiles, bbox))
        view1.render(surf1, [(app.player_pos.topleft, app.player_surf)])

        surf2.fill("black")
        bbox = view2.get_bounding_box()
        view2.render(surf2, app.get_tiles_for_bbox(app.tiles, bbox))
        view2.render(surf2, [(app.player_pos.topleft, app.player_surf)])

        app.screen.blit(surf1, (0, 0))
        app.screen.blit(surf2, (0, app.screen.height // 2))

        app.screen.blit(text1, (10, 10))
        app.screen.blit(text2, (10, 10 + app.screen.height // 2))


if __name__ == "__main__":
    main()
