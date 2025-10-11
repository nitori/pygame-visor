import pygame

from pygame_visor import Visor, VisorMode
from common import App


def main():
    app = App((1000, 600))

    view = Visor(
        VisorMode.RegionExpand,
        app.screen.get_rect(),
        region=(0, 0, 400, 300),
        limits=app.extended_limits(10),
    )

    view.move_to(app.player_pos.center)

    acc = 0

    health_bar = pygame.Surface((250, 20))
    health_bar.fill((0, 128, 0))

    item_bar = pygame.Surface((500, 50), pygame.SRCALPHA)
    items = []
    for n in range(10):
        item = pygame.Surface((40, 40))
        item.fill("blue")
        x = n * 50 + 5
        y = 5
        items.append((x, y, item))
        item_bar.blit(item, (x, y))

    for delta in app.loop(60):
        acc += delta
        if acc > 10:
            acc -= 10

        # just a simple "prograssing" health bar
        health = max(0, min(100, int(100 - acc * 10))) / 100
        health_bar.fill("red")
        pygame.draw.rect(health_bar, (0, 128, 0), (0, 0, int(health * 250), 20))

        # render the map
        view.move_to(app.player_pos.center)
        bbox = view.get_bounding_box()
        view.render(app.screen, app.get_tiles_for_bbox(app.tiles, bbox))

        # render the player
        view.render(app.screen, [(app.player_pos.topleft, app.player_surf)])

        # Render health bar to the "active area".
        # With RegionExpand, the healthbar might be positioned slightly inward
        # and not at the left-most screen border.
        game_area = view.get_active_screen_area()
        app.screen.blit(health_bar, (game_area.x + 10, game_area.y + 10))

        # blit item bar at the bottom center
        r = item_bar.get_rect()
        r.midbottom = (game_area.centerx, game_area.bottom - 10)
        app.screen.blit(item_bar, r)


if __name__ == "__main__":
    main()
