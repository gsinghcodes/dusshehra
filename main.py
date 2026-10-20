import math
import sys
from random import randint

import pygame as pygame
from pygame import gfxdraw

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

FIRE_PIXEL_SIZE = 4
FIRE_HORIZONTAL_REPETITIONS = 4
FIRE_GRID_WIDTH = WINDOW_WIDTH // (FIRE_PIXEL_SIZE * FIRE_HORIZONTAL_REPETITIONS)
FIRE_GRID_HEIGHT = WINDOW_HEIGHT // FIRE_PIXEL_SIZE

PALETTE_COLOR_STEPS = 9
FIRE_PALETTE_COLORS = ["black", "red", "orange", "yellow", "white"]

RAVANA_IMAGE_SIZE = (600, 600)
RAVANA_TERRIFIED_VERTICAL_OFFSET = 8
RAVANA_SLIDE_SPEED = 5

BHIBHISHAN_IMAGE_SIZE = (300, 300)
BHIBHISHAN_SLIDE_SPEED = 5
BHIBHISHAN_LEAVE_SPEED = 8
BHIBHISHAN_APPEAR_DELAY_MS = 500
BHIBHISHAN_LEAVE_DELAY_MS = 1000

NAVEL_HIT_EFFECT_DURATION_MS = 600
NAVEL_HIT_PIXEL_SIZE = 6

CURSOR_IMAGE_SIZE = (69, 69)
NAVEL_HITBOX = pygame.Rect(590, 285, 40, 40)


class RavanDahan:
    def __init__(self, app):
        self.app = app

        self.fire_palette = self.create_fire_palette()
        self.fire_grid = self.create_fire_grid()
        self.fire_surface = pygame.Surface(
            (FIRE_PIXEL_SIZE * FIRE_GRID_WIDTH, WINDOW_HEIGHT)
        )
        self.fire_surface.set_colorkey("black")

        self.ravan_smiling_image = self.load_scaled_image(
            "ravan-smile.png", RAVANA_IMAGE_SIZE
        )
        self.ravan_terrified_image = self.load_scaled_image(
            "ravan-terrified.png", RAVANA_IMAGE_SIZE
        )
        self.ravan_current_image = self.ravan_smiling_image
        self.ravan_image_x = (WINDOW_WIDTH - self.ravan_smiling_image.get_width()) // 2
        self.ravan_image_start_y = WINDOW_HEIGHT
        self.ravan_target_y = WINDOW_HEIGHT - self.ravan_smiling_image.get_height() + 8

        self.bhibhishan_prompt_image = self.load_scaled_image(
            "bhibhishan-prompt.png", BHIBHISHAN_IMAGE_SIZE
        )
        self.bhibhishan_happy_image = self.load_scaled_image(
            "bhibhishan-happy.png", BHIBHISHAN_IMAGE_SIZE
        )
        self.bhibhishan_current_image = self.bhibhishan_prompt_image
        self.bhibhishan_x = WINDOW_WIDTH
        self.bhibhishan_y = WINDOW_HEIGHT - self.bhibhishan_prompt_image.get_height()
        self.bhibhishan_appearance_started_at = None
        self.bhibhishan_leave_started_at = None
        self.bhibhishan_is_leaving = False
        self.bhibhishan_is_hidden = False

        self.custom_cursor_image = self.load_scaled_image(
            "arrow.png", CURSOR_IMAGE_SIZE
        )

        self.navel_hit_effect_started_at = None
        self.fire_animation_started = False

    @staticmethod
    def load_scaled_image(image_path, size):
        return pygame.transform.scale(
            pygame.image.load(image_path).convert_alpha(),
            size,
        )

    def draw_custom_cursor(self):
        cursor_hitbox = NAVEL_HITBOX
        bhibhishan_target_x = WINDOW_WIDTH - self.bhibhishan_prompt_image.get_width()

        bhibhishan_is_in_position = self.bhibhishan_x == bhibhishan_target_x
        bhibhishan_has_not_been_clicked = self.bhibhishan_leave_started_at is None
        mouse_position = pygame.mouse.get_pos()

        if (
            bhibhishan_is_in_position
            and bhibhishan_has_not_been_clicked
            and cursor_hitbox.collidepoint(mouse_position)
        ):
            pygame.mouse.set_visible(False)
            self.app.screen.blit(self.custom_cursor_image, mouse_position)
        else:
            pygame.mouse.set_visible(True)

    def draw_ravan(self):
        if self.ravan_image_start_y > self.ravan_target_y:
            self.ravan_image_start_y = max(
                self.ravan_target_y,
                self.ravan_image_start_y - RAVANA_SLIDE_SPEED,
            )

        if self.ravan_image_start_y == self.ravan_target_y:
            self.app.ravan_is_visible = True

        image_y = self.ravan_image_start_y
        if self.ravan_current_image == self.ravan_terrified_image:
            image_y += RAVANA_TERRIFIED_VERTICAL_OFFSET

        self.app.screen.blit(
            self.ravan_current_image,
            (self.ravan_image_x, image_y),
        )

    def draw_bhibhishan(self):
        if self.bhibhishan_leave_started_at is not None:
            elapsed_ms = pygame.time.get_ticks() - self.bhibhishan_leave_started_at
            if elapsed_ms >= BHIBHISHAN_LEAVE_DELAY_MS:
                self.bhibhishan_is_leaving = True

        if self.bhibhishan_is_hidden:
            return

        if self.bhibhishan_is_leaving:
            self.bhibhishan_x += BHIBHISHAN_LEAVE_SPEED

            if self.bhibhishan_x >= WINDOW_WIDTH:
                self.bhibhishan_x = WINDOW_WIDTH
                self.bhibhishan_is_hidden = True
                self.bhibhishan_is_leaving = False
                self.fire_animation_started = True
                return

            self.app.screen.blit(
                self.bhibhishan_current_image,
                (self.bhibhishan_x, self.bhibhishan_y),
            )
            return

        if not self.app.ravan_is_visible:
            return

        if self.bhibhishan_appearance_started_at is None:
            self.bhibhishan_appearance_started_at = pygame.time.get_ticks()

        elapsed_ms = pygame.time.get_ticks() - self.bhibhishan_appearance_started_at
        if elapsed_ms < BHIBHISHAN_APPEAR_DELAY_MS:
            return

        bhibhishan_target_x = WINDOW_WIDTH - self.bhibhishan_prompt_image.get_width()
        if self.bhibhishan_x > bhibhishan_target_x:
            self.bhibhishan_x = max(
                bhibhishan_target_x,
                self.bhibhishan_x - BHIBHISHAN_SLIDE_SPEED,
            )

        self.app.screen.blit(
            self.bhibhishan_current_image,
            (self.bhibhishan_x, self.bhibhishan_y),
        )

    def handle_click(self, mouse_position):
        if (
            NAVEL_HITBOX.collidepoint(mouse_position)
            and self.bhibhishan_leave_started_at is None
            and self.bhibhishan_x
            == WINDOW_WIDTH - self.bhibhishan_prompt_image.get_width()
            and not self.bhibhishan_is_hidden
        ):
            self.ravan_current_image = self.ravan_terrified_image
            self.bhibhishan_current_image = self.bhibhishan_happy_image
            current_time = pygame.time.get_ticks()
            self.bhibhishan_leave_started_at = current_time
            self.navel_hit_effect_started_at = current_time

    def draw_navel_hit_effect(self):
        if self.navel_hit_effect_started_at is None:
            return

        elapsed_ms = pygame.time.get_ticks() - self.navel_hit_effect_started_at
        if elapsed_ms >= NAVEL_HIT_EFFECT_DURATION_MS:
            self.navel_hit_effect_started_at = None
            return

        center_x = NAVEL_HITBOX.centerx
        center_y = NAVEL_HITBOX.centery
        progress = elapsed_ms / NAVEL_HIT_EFFECT_DURATION_MS
        pixel_size = NAVEL_HIT_PIXEL_SIZE
        outer_radius = 6 + int(progress * 42)

        blue_ring_colors = [
            (30, 80, 255),
            (40, 160, 255),
            (100, 220, 255),
        ]

        for ring_index, ring_color in enumerate(blue_ring_colors):
            ring_radius = outer_radius - ring_index * 8
            if ring_radius <= 0:
                continue

            for offset_x in range(-ring_radius, ring_radius + 1, pixel_size):
                for offset_y in range(-ring_radius, ring_radius + 1, pixel_size):
                    distance_squared = offset_x**2 + offset_y**2
                    inner_radius = max(0, ring_radius - pixel_size)

                    if inner_radius**2 <= distance_squared <= ring_radius**2:
                        pygame.draw.rect(
                            self.app.screen,
                            ring_color,
                            (
                                center_x + offset_x,
                                center_y + offset_y,
                                pixel_size,
                                pixel_size,
                            ),
                        )

        if elapsed_ms < 100:
            pygame.draw.rect(
                self.app.screen,
                (180, 245, 255),
                (center_x - 6, center_y - 6, 12, 12),
            )

        for spark_index in range(8):
            angle = spark_index * math.pi / 4
            spark_distance = 12 + int(progress * 48)
            spark_x = center_x + int(math.cos(angle) * spark_distance)
            spark_y = center_y + int(math.sin(angle) * spark_distance)

            pygame.draw.rect(
                self.app.screen,
                blue_ring_colors[spark_index % len(blue_ring_colors)],
                (spark_x, spark_y, pixel_size, pixel_size),
            )

    def update_fire(self):
        for column_index in range(FIRE_GRID_WIDTH):
            for row_index in range(1, FIRE_GRID_HEIGHT):
                color_index = self.fire_grid[row_index][column_index]

                if color_index:
                    random_spread = randint(0, 3)
                    destination_column = (
                        column_index - random_spread + 1
                    ) % FIRE_GRID_WIDTH
                    self.fire_grid[row_index - 1][destination_column] = (
                        color_index - random_spread % 2
                    )
                else:
                    self.fire_grid[row_index - 1][column_index] = 0

    def draw_fire(self):
        self.fire_surface.fill("black")

        for row_index, fire_row in enumerate(self.fire_grid):
            for column_index, color_index in enumerate(fire_row):
                if color_index:
                    pixel_color = self.fire_palette[color_index]
                    gfxdraw.box(
                        self.fire_surface,
                        (
                            column_index * FIRE_PIXEL_SIZE,
                            row_index * FIRE_PIXEL_SIZE,
                            FIRE_PIXEL_SIZE,
                            FIRE_PIXEL_SIZE,
                        ),
                        pixel_color,
                    )

        for repetition_index in range(FIRE_HORIZONTAL_REPETITIONS):
            self.app.screen.blit(
                self.fire_surface,
                (self.fire_surface.get_width() * repetition_index, 0),
            )

    def create_fire_grid(self):
        fire_grid = [
            [0 for _ in range(FIRE_GRID_WIDTH)] for _ in range(FIRE_GRID_HEIGHT)
        ]
        hottest_color_index = len(self.fire_palette) - 1

        for column_index in range(FIRE_GRID_WIDTH):
            fire_grid[FIRE_GRID_HEIGHT - 1][column_index] = hottest_color_index

        return fire_grid

    @staticmethod
    def create_fire_palette():
        palette = [(0, 0, 0)]

        for color_index, starting_color in enumerate(FIRE_PALETTE_COLORS[:-1]):
            ending_color = FIRE_PALETTE_COLORS[color_index + 1]

            for step_index in range(PALETTE_COLOR_STEPS):
                blend_amount = (step_index + 0.5) / PALETTE_COLOR_STEPS
                blended_color = pygame.Color(starting_color).lerp(
                    ending_color,
                    blend_amount,
                )
                palette.append(blended_color)

        return palette

    def update(self):
        if self.fire_animation_started:
            self.update_fire()

    def draw(self):
        self.draw_ravan()
        self.draw_navel_hit_effect()
        self.draw_bhibhishan()

        if self.fire_animation_started:
            self.draw_fire()

        self.draw_custom_cursor()


class App:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.ravan_is_visible = False
        self.ravan_dahan = RavanDahan(self)

    def update(self):
        self.ravan_dahan.update()
        self.clock.tick(60)
        pygame.display.set_caption("Happy Dussehra")

    def draw(self):
        self.screen.fill("black")
        self.ravan_dahan.draw()
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.ravan_dahan.handle_click(event.pos)

            self.update()
            self.draw()


if __name__ == "__main__":
    app = App()
    app.run()
