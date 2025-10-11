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

    font = pygame.Font(pygame.font.get_default_font())

    def event_handler(event: pygame.Event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                view.region.scale_by_ip(2, 2)
            elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
                view.region.scale_by_ip(0.5, 0.5)

    for delta in app.loop(60, event_handler):
        view.move_to(app.player_pos.center)
        bbox = view.get_bounding_box()
        view.render(app.screen, app.get_tiles_for_bbox(app.tiles, bbox))
        view.render(app.screen, [
            (app.player_pos.topleft, app.player_surf)
        ])

        size_text = font.render(str(view.region.size), True, 'white', 'black')
        app.screen.blit(size_text, (10, 10))


if __name__ == '__main__':
    main()
