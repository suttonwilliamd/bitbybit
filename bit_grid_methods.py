    def _draw_component(self, screen, comp_name, comp):
        """Draw a single component with its bits"""
        # Draw component background
        if comp["unlocked"]:
            bg_color = tuple(c // 4 for c in comp["color"])  # Darker version
            border_color = comp["color"]
        else:
            bg_color = self.colors["locked"]
            border_color = (60, 60, 60)

        pygame.draw.rect(
            screen, bg_color, (comp["x"], comp["y"], comp["width"], comp["height"])
        )
        pygame.draw.rect(
            screen,
            border_color,
            (comp["x"], comp["y"], comp["width"], comp["height"]),
            3,
        )

        if comp["unlocked"]:
            # Draw component label
            font = pygame.font.Font(None, 16)
            label = font.render(
                f"{comp['name']} Lvl.{comp['level']}", True, (255, 255, 255)
            )
            screen.blit(label, (comp["x"] + 5, comp["y"] + 5))

            # Draw bits in a grid layout
            if comp["width"] > 30 and comp["height"] > 50:  # Ensure minimum size
                self._draw_component_bits(screen, comp)
        else:
            # Draw locked indicator
            font = pygame.font.Font(None, 20)
            label = font.render("LOCKED", True, (100, 100, 100))
            text_rect = label.get_rect(
                center=(comp["x"] + comp["width"] // 2, comp["y"] + comp["height"] // 2)
            )
            screen.blit(label, text_rect)

    def _draw_component_bits(self, screen, comp):
        """Draw the bits within a component"""
        total_bits = comp["bits"]

        # Calculate grid dimensions for bits
        total_bits = comp["bits"]

        # Ensure minimum component size
        if comp["width"] <= 30 or comp["height"] <= 50:
            return

        # Calculate grid dimensions for bits
        grid_cols = max(1, int(math.sqrt(total_bits * comp["width"] / comp["height"])))
        grid_rows = (total_bits + grid_cols - 1) // grid_cols

        bit_width = max(1, (comp["width"] - 20) // grid_cols)
        bit_height = max(1, (comp["height"] - 40) // grid_rows)

        start_x = comp["x"] + 10
        start_y = comp["y"] + 30

        for bit_idx in range(total_bits):
            row = bit_idx // grid_cols
            col = bit_idx % grid_cols

            if row >= grid_rows:
                continue

            bit_x = start_x + col * bit_width
            bit_y = start_y + row * bit_height

            # Check if bit is animating
            anim_key = (comp["name"], bit_idx)
            bit_value = comp["bit_states"][bit_idx]

            if anim_key in comp["bit_animations"]:
                anim = comp["bit_animations"][anim_key]
                progress = anim["progress"] / anim["duration"]

                # Interpolate color during animation
                from_color = self.colors[anim["from_value"]]
