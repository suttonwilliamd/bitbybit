"""
Visual effects for Bit by Bit Game
"""

import pygame
import math
import random
from constants import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT


class Particle:
    def __init__(self, x, y, color=COLORS["electric_cyan"], particle_type="burst"):
        self.x = x
        self.y = y
        self.color = color
        self.particle_type = particle_type
        self.lifetime = 1.0
        self.size = random.randint(2, 6)

        if particle_type == "burst":
            self.vx = random.uniform(-150, 150)
            self.vy = random.uniform(-250, -100)
        elif particle_type == "click":
            self.vx = random.uniform(-80, 80)
            self.vy = random.uniform(-150, -50)
        elif particle_type == "purchase":
            # Particles that fly toward accumulator
            target_x, target_y = WINDOW_WIDTH // 2, 200
            dx = target_x - x
            dy = target_y - y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                self.vx = (dx / distance) * random.uniform(100, 200)
                self.vy = (dy / distance) * random.uniform(100, 200)
            else:
                self.vx = random.uniform(-100, 100)
                self.vy = random.uniform(-100, 100)

        self.gravity = 200 if particle_type == "burst" else 100
        self.trail = []  # Store previous positions for trail effect

    def update(self, dt):
        # Store current position in trail
        if len(self.trail) < 5:
            self.trail.append((self.x, self.y, self.lifetime))
        else:
            self.trail.pop(0)
            self.trail.append((self.x, self.y, self.lifetime))

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.lifetime -= dt
        self.vx *= 0.98  # friction

    def draw(self, screen):
        if self.lifetime > 0:
            # Draw trail
            for i, (tx, ty, trail_lifetime) in enumerate(self.trail):
                trail_alpha = int(
                    255 * trail_lifetime * (i + 1) / len(self.trail) * 0.3
                )
                trail_size = max(1, self.size - 2)
                trail_color = tuple(int(c * trail_lifetime) for c in self.color)
                pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), trail_size)

            # Draw main particle with glow
            alpha = int(255 * self.lifetime)

            # Outer glow
            glow_size = self.size + 2
            glow_color = tuple(int(c * 0.3 * self.lifetime) for c in self.color)
            pygame.draw.circle(
                screen, glow_color, (int(self.x), int(self.y)), glow_size
            )

            # Main particle
            main_color = tuple(int(c * self.lifetime) for c in self.color)
            pygame.draw.circle(
                screen, main_color, (int(self.x), int(self.y)), self.size
            )


class BinaryRain:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.columns = []
        self.init_columns()

    def init_columns(self):
        # Create columns of binary rain
        num_columns = self.width // 20
        for i in range(num_columns):
            self.columns.append(
                {
                    "x": i * 20 + random.randint(0, 15),
                    "y": random.randint(-self.height, 0),
                    "speed": random.uniform(30, 80),  # Very slow movement
                    "chars": random.choices(["0", "1"], k=random.randint(5, 15)),
                    # flicker_chance removed to prevent visual artifacts
                }
            )

    def update(self, dt):
        for column in self.columns:
            column["y"] += column["speed"] * dt

            # Reset column when it goes off screen
            if column["y"] > self.height + len(column["chars"]) * 20:
                column["y"] = -len(column["chars"]) * 20
                column["chars"] = random.choices(["0", "1"], k=random.randint(5, 15))
                column["speed"] = random.uniform(30, 80)

            # Removed flicker effect to prevent visual artifacts

    def draw(self, screen):
        font = pygame.font.Font(None, 16)
        for column in self.columns:
            for i, char in enumerate(column["chars"]):
                y_pos = column["y"] + i * 20
                if 0 <= y_pos <= self.height:
                    # Very faint green color
                    alpha = max(10, 30 - i * 2)
                    color = (57, 255, 20) if char == "1" else (20, 100, 20)

                    text_surface = font.render(char, True, color)
                    text_surface.set_alpha(alpha)
                    screen.blit(text_surface, (column["x"], y_pos))


class BitDot:
    def __init__(self, center_x, center_y, bits_value):
        self.center_x = center_x
        self.center_y = center_y
        self.angle = random.uniform(0, 2 * math.pi)
        self.radius = 0
        self.target_radius = random.uniform(20, 80)
        self.lifetime = 1.0
        self.size = 4
        self.bits_value = bits_value
        self.spiral_speed = random.uniform(1, 3)

    def update(self, dt):
        # Spiral outward animation
        self.radius += (self.target_radius - self.radius) * 2 * dt
        self.angle += self.spiral_speed * dt
        self.lifetime -= dt
        # Calculate actual position
        self.x = self.center_x + math.cos(self.angle) * self.radius
        self.y = self.center_y + math.sin(self.angle) * self.radius

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * self.lifetime)

            color = COLORS["electric_cyan"]
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class SmartBitVisualization:
    """Enhanced visualization system with smart scaling and performance optimization"""

    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y
        self.dots = []
        self.clusters = []  # Bit clusters for larger numbers
        self.formations = []  # Byte formations
        self.data_streams = []
        self.pulse_timer = 0
        self.background_particles = []
        self.spawn_timer = 0

        # Visualization modes based on bit count
        self.visualization_modes = {
            "individual": 1000,  # < 1K: Individual bits
            "clusters": 1000000,  # 1K-1M: Bit clusters
            "formations": 100000000,  # 1M-100M: Byte formations
            "streams": float("inf"),  # >100M: Data streams
        }

        # Performance settings
        self.quality_level = "high"  # high, medium, low
        self.max_particles = 1000
        self.particle_pool = []  # Object pooling for performance

    def get_visualization_mode(self, bits):
        """Determine visualization mode based on bit count"""
        if bits < self.visualization_modes["individual"]:
            return "individual"
        elif bits < self.visualization_modes["clusters"]:
            return "clusters"
        elif bits < self.visualization_modes["formations"]:
            return "formations"
        else:
            return "streams"

    def spawn_bit_cluster(self, bits):
        """Spawn clusters of bits for medium-scale visualization"""
        cluster_size = random.randint(4, 8)  # 4-8 bits per cluster
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(80, 120)

        cluster_x = self.center_x + math.cos(angle) * radius
        cluster_y = self.center_y + math.sin(angle) * radius

        # Create cluster formation
        cluster = {
            "x": cluster_x,
            "y": cluster_y,
            "bits": cluster_size,
            "angle": random.uniform(0, 2 * math.pi),
            "rotation_speed": random.uniform(-2, 2),
            "lifetime": 2.0,
            "formation": self._get_cluster_formation(cluster_size),
        }

        self.clusters.append(cluster)

    def spawn_byte_formation(self, bits):
        """Spawn hexagonal byte formations for large-scale visualization"""
        formation_size = random.randint(8, 16)  # 8-16 bytes
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(120, 180)

        formation_x = self.center_x + math.cos(angle) * radius
        formation_y = self.center_y + math.sin(angle) * radius

        # Create hexagonal formation
        formation = {
            "x": formation_x,
            "y": formation_y,
            "bytes": formation_size,
            "angle": angle,
            "rotation_speed": random.uniform(-1, 1),
            "lifetime": 3.0,
            "hex_pattern": self._generate_hex_pattern(formation_size),
        }

        self.formations.append(formation)

    def _get_cluster_formation(self, size):
        """Generate formation pattern for bit cluster"""
        patterns = {4: "square", 5: "cross", 6: "hexagon", 7: "circle", 8: "star"}
        return patterns.get(size, "circle")

    def _generate_hex_pattern(self, size):
        """Generate hexagonal pattern coordinates"""
        pattern = []
        positions = []

        # Center position
        positions.append((0, 0))

        # Surrounding positions in hex pattern
        for i in range(1, size):
            angle = (2 * math.pi * i) / (size - 1)
            x = math.cos(angle) * 15
            y = math.sin(angle) * 15
            positions.append((x, y))

        return positions

    def update(self, bits, dt):
        # Update pulse effect
        self.pulse_timer += dt * 2

        # Get current visualization mode
        mode = self.get_visualization_mode(bits)

        # Spawn based on mode and performance settings
        self.spawn_timer += dt

        # Adjust spawn rate based on quality level
        quality_multipliers = {"high": 1.0, "medium": 0.6, "low": 0.3}
        quality_mult = quality_multipliers.get(self.quality_level, 1.0)

        if self.spawn_timer >= (0.5 / quality_mult):
            self.spawn_timer = 0

            if mode == "individual":
                # Spawn individual bits (original behavior)
                num_dots = max(1, min(3, int(bits / 1000)))
                for _ in range(num_dots):
                    angle = random.uniform(0, 2 * math.pi)
                    radius = random.uniform(100, 150)
                    spawn_x = self.center_x + math.cos(angle) * radius
                    spawn_y = self.center_y + math.sin(angle) * radius
                    self.dots.append(BitDot(spawn_x, spawn_y, bits))

            elif mode == "clusters":
                # Spawn bit clusters
                if random.random() < 0.3 * quality_mult:
                    self.spawn_bit_cluster(bits)

            elif mode == "formations":
                # Spawn byte formations
                if random.random() < 0.2 * quality_mult:
                    self.spawn_byte_formation(bits)

            elif mode == "streams":
                # Spawn data streams for very large values
                if random.random() < 0.15 * quality_mult:
                    self.data_streams.append(
                        {
                            "start_x": random.randint(50, WINDOW_WIDTH - 50),
                            "start_y": 0,
                            "end_x": self.center_x + random.randint(-50, 50),
                            "end_y": self.center_y,
                            "progress": 0,
                            "speed": random.uniform(1.0, 3.0),
                            "width": random.randint(3, 8),
                            "color": random.choice(
                                [COLORS["electric_cyan"], COLORS["neon_purple"]]
                            ),
                        }
                    )

        # Limited ambient particles based on quality
        if random.random() < 0.01 * quality_mult:
            self._spawn_ambient_particle()

        # Update all visualization elements
        self._update_dots(dt)
        self._update_clusters(dt)
        self._update_formations(dt)
        self._update_data_streams(dt)
        self._update_background_particles(dt)

        # Performance cleanup
        self._cleanup_elements()

    def _spawn_ambient_particle(self):
        """Spawn ambient background particle away from accumulator"""
        while True:
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)

            # Check if not over accumulator area
            acc_left = self.center_x - 100
            acc_right = self.center_x + 100
            acc_top = self.center_y - 75
            acc_bottom = self.center_y + 75

            if not (acc_left <= x <= acc_right and acc_top <= y <= acc_bottom):
                break

        self.background_particles.append(
            {
                "x": x,
                "y": y,
                "vx": random.uniform(-20, 20),
                "vy": random.uniform(-30, -10),
                "size": random.randint(1, 2),
                "lifetime": random.uniform(3, 8),
                "color": random.choice(
                    [
                        COLORS["electric_cyan"],
                        COLORS["neon_purple"],
                        COLORS["matrix_green"],
                    ]
                ),
            }
        )

    def _update_dots(self, dt):
        """Update individual bit dots"""
        self.dots = [dot for dot in self.dots if dot.lifetime > 0]
        for dot in self.dots:
            dot.update(dt)

    def _update_clusters(self, dt):
        """Update bit clusters"""
        self.clusters = [
            cluster for cluster in self.clusters if cluster["lifetime"] > 0
        ]
        for cluster in self.clusters:
            cluster["angle"] += cluster["rotation_speed"] * dt
            cluster["lifetime"] -= dt

    def _update_formations(self, dt):
        """Update byte formations"""
        self.formations = [
            formation for formation in self.formations if formation["lifetime"] > 0
        ]
        for formation in self.formations:
            formation["angle"] += formation["rotation_speed"] * dt
            formation["lifetime"] -= dt

    def _update_data_streams(self, dt):
        """Update data streams"""
        self.data_streams = [
            stream for stream in self.data_streams if stream["progress"] < 1.0
        ]
        for stream in self.data_streams:
            stream["progress"] += stream["speed"] * dt

    def _update_background_particles(self, dt):
        """Update background particles"""
        self.background_particles = [
            p for p in self.background_particles if p["lifetime"] > 0
        ]
        for particle in self.background_particles:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["lifetime"] -= dt

    def _cleanup_elements(self):
        """Clean up elements to maintain performance"""
        # Limit particle count based on quality level
        max_counts = {"high": 1000, "medium": 500, "low": 200}
        max_count = max_counts.get(self.quality_level, 1000)

        if len(self.dots) > max_count // 4:
            self.dots = self.dots[-max_count // 4 :]
        if len(self.clusters) > max_count // 3:
            self.clusters = self.clusters[-max_count // 3 :]
        if len(self.formations) > max_count // 3:
            self.formations = self.formations[-max_count // 3 :]
        if len(self.background_particles) > max_count // 2:
            self.background_particles = self.background_particles[-max_count // 2 :]

    def set_quality_level(self, level):
        """Set visualization quality level"""
        self.quality_level = level

    def draw(self, screen, bits):
        """Draw all visualization elements"""
        # Draw background particles first
        for particle in self.background_particles:
            alpha = particle["lifetime"] / 8.0
            color = tuple(int(c * alpha) for c in particle["color"])
            pygame.draw.circle(
                screen,
                color,
                (int(particle["x"]), int(particle["y"])),
                particle["size"],
            )

        # Draw data streams
        for stream in self.data_streams:
            if stream["progress"] > 0:
                current_x = (
                    stream["start_x"]
                    + (stream["end_x"] - stream["start_x"]) * stream["progress"]
                )
                current_y = (
                    stream["start_y"]
                    + (stream["end_y"] - stream["start_y"]) * stream["progress"]
                )

                # Draw trail
                for i in range(5):
                    trail_progress = max(0, stream["progress"] - (i * 0.02))
                    if trail_progress > 0:
                        trail_x = (
                            stream["start_x"]
                            + (stream["end_x"] - stream["start_x"]) * trail_progress
                        )
                        trail_y = (
                            stream["start_y"]
                            + (stream["end_y"] - stream["start_y"]) * trail_progress
                        )
                        alpha = (1.0 - i / 5) * (1.0 - stream["progress"])
                        color = tuple(int(c * alpha) for c in stream["color"])
                        pygame.draw.circle(
                            screen,
                            color,
                            (int(trail_x), int(trail_y)),
                            max(1, stream["width"] - i),
                        )

        # Draw based on current mode
        mode = self.get_visualization_mode(bits)

        if mode == "individual":
            # Draw individual dots
            for dot in self.dots:
                dot.draw(screen)

        elif mode == "clusters":
            # Draw clusters
            for cluster in self.clusters:
                self._draw_cluster(screen, cluster)

        elif mode == "formations":
            # Draw byte formations
            for formation in self.formations:
                self._draw_formation(screen, formation)

        # Draw central pulse
        if self.pulse_timer > 0:
            pulse_radius = int(abs(math.sin(self.pulse_timer)) * 30)
            pulse_alpha = abs(math.sin(self.pulse_timer)) * 0.3
            pulse_color = tuple(int(c * pulse_alpha) for c in COLORS["electric_cyan"])
            pygame.draw.circle(
                screen, pulse_color, (self.center_x, self.center_y), pulse_radius, 2
            )

    def _draw_cluster(self, screen, cluster):
        """Draw a bit cluster"""
        alpha = cluster["lifetime"] / 2.0
        base_color = COLORS["electric_cyan"]
        color = tuple(int(c * alpha) for c in base_color)

        # Draw cluster based on formation type
        formation = cluster["formation"]
        size = 4

        if formation == "square":
            positions = [(-size, -size), (size, -size), (size, size), (-size, size)]
        elif formation == "cross":
            positions = [(0, -size * 2), (size * 2, 0), (0, size * 2), (-size * 2, 0)]
        elif formation == "hexagon":
            positions = [
                (size * math.cos(i * math.pi / 3), size * math.sin(i * math.pi / 3))
                for i in range(6)
            ]
        else:  # circle/star
            positions = [
                (
                    size * math.cos(i * 2 * math.pi / cluster["bits"]),
                    size * math.sin(i * 2 * math.pi / cluster["bits"]),
                )
                for i in range(cluster["bits"])
            ]

        # Draw cluster dots
        for dx, dy in positions:
            x = (
                cluster["x"]
                + dx * math.cos(cluster["angle"])
                - dy * math.sin(cluster["angle"])
            )
            y = (
                cluster["y"]
                + dx * math.sin(cluster["angle"])
                + dy * math.cos(cluster["angle"])
            )
            pygame.draw.circle(screen, color, (int(x), int(y)), 3)

    def _draw_formation(self, screen, formation):
        """Draw a byte formation"""
        alpha = formation["lifetime"] / 3.0
        base_color = COLORS["neon_purple"]
        color = tuple(int(c * alpha) for c in base_color)

        # Draw hexagonal pattern
        for dx, dy in formation["hex_pattern"]:
            x = (
                formation["x"]
                + dx * math.cos(formation["angle"])
                - dy * math.sin(formation["angle"])
            )
            y = (
                formation["y"]
                + dx * math.sin(formation["angle"])
                + dy * math.cos(formation["angle"])
            )
            pygame.draw.circle(screen, color, (int(x), int(y)), 2)


# Legacy BitVisualization for backward compatibility
class BitVisualization(SmartBitVisualization):
    """Legacy wrapper for BitVisualization"""

    def __init__(self, center_x, center_y):
        super().__init__(center_x, center_y)
        # Set high quality by default for legacy behavior
        self.set_quality_level("high")

    def draw(self, screen, bits=None):
        """Legacy draw method that doesn't require bits parameter"""
        if bits is None:
            bits = 0  # Default value for compatibility
        super().draw(screen, bits=bits)

    def draw(self, screen):
        # Draw background particles
        for particle in self.background_particles:
            alpha = particle["lifetime"] / 8.0  # Normalize to 0-1
            color = tuple(int(c * alpha) for c in particle["color"])
            # Ensure color values are valid (0-255)
            color = tuple(max(0, min(255, c)) for c in color)
            pygame.draw.circle(
                screen,
                color,
                (int(particle["x"]), int(particle["y"])),
                particle["size"],
            )

        # Draw data streams
        for stream in self.data_streams:
            if stream["progress"] > 0:
                current_x = (
                    stream["start_x"]
                    + (stream["end_x"] - stream["start_x"]) * stream["progress"]
                )
                current_y = (
                    stream["start_y"]
                    + (stream["end_y"] - stream["start_y"]) * stream["progress"]
                )

                # Draw stream as connected dots
                trail_length = 5
                for i in range(trail_length):
                    trail_progress = max(0, stream["progress"] - (i * 0.02))
                    if trail_progress > 0:
                        trail_x = (
                            stream["start_x"]
                            + (stream["end_x"] - stream["start_x"]) * trail_progress
                        )
                        trail_y = (
                            stream["start_y"]
                            + (stream["end_y"] - stream["start_y"]) * trail_progress
                        )
                        alpha = (1.0 - i / trail_length) * (1.0 - stream["progress"])
                        color = tuple(int(c * alpha) for c in stream["color"])
                        # Ensure color values are valid (0-255)
                        color = tuple(max(0, min(255, c)) for c in color)
                        pygame.draw.circle(
                            screen,
                            color,
                            (int(trail_x), int(trail_y)),
                            stream["width"] - i,
                        )

        # Draw main bit dots with enhanced glow
        for dot in self.dots:
            # Add extra glow effect
            if dot.lifetime > 0.5:
                glow_size = dot.size + 4
                glow_alpha = (dot.lifetime - 0.5) * 0.3
                glow_color = tuple(int(c * glow_alpha) for c in COLORS["electric_cyan"])
                pygame.draw.circle(
                    screen, glow_color, (int(dot.x), int(dot.y)), glow_size
                )

            dot.draw(screen)

        # Draw central pulse effect
        if self.pulse_timer > 0:
            pulse_radius = int(abs(math.sin(self.pulse_timer)) * 30)
            pulse_alpha = abs(math.sin(self.pulse_timer)) * 0.3
            pulse_color = tuple(int(c * pulse_alpha) for c in COLORS["electric_cyan"])
            pygame.draw.circle(
                screen, pulse_color, (self.center_x, self.center_y), pulse_radius, 2
            )
