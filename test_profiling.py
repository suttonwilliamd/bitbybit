"""
Profiling tests for Bit by Bit Game
Comprehensive coverage of all major systems
Run with: python test_profiling.py
"""

import pygame
import cProfile
import pstats
import io
import time
import math
import random
import sys
from unittest.mock import MagicMock

pygame.init()

from game_state import GameState
from bit_grid import MotherboardBitGrid, LEDGrid
from visual_effects import (
    Particle, BinaryRain, SmartBitVisualization, BitVisualization, BitDot
)
from ui_components import Button, FloatingText, LayoutManager, GameUIState
from constants import COLORS, CONFIG, WINDOW_WIDTH, WINDOW_HEIGHT


class ProfilerTimer:
    """Context manager for timing code blocks"""
    def __init__(self, name, iterations=1):
        self.name = name
        self.start_time = None
        self.iterations = iterations
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, *args):
        elapsed = time.perf_counter() - (self.start_time or 0)
        avg_time = elapsed / self.iterations
        print(f"{self.name}: {avg_time*1000:.3f}ms (total: {elapsed*1000:.1f}ms over {self.iterations} iters)")


def benchmark_game_state():
    """Benchmark GameState methods - all core game logic"""
    print("\n=== GameState Core Benchmarks ===")
    
    state = GameState()
    state.era = "entropy"
    state.bits = 1000000
    state.total_bits_earned = 5000000
    
    hw_gens = CONFIG.get("HARDWARE_GENERATORS", {})
    for gen_id in list(hw_gens.keys())[:4]:
        if gen_id in state.generators:
            state.generators[gen_id]["count"] = 50
    
    state.upgrades["click_power"]["level"] = 10
    state.upgrades["entropy_amplification"]["level"] = 5
    
    print("\nProduction calculations:")
    with ProfilerTimer("get_production_rate", 1000):
        for _ in range(1000):
            state.get_production_rate()
    
    with ProfilerTimer("get_click_power", 1000):
        for _ in range(1000):
            state.get_click_power()
    
    with ProfilerTimer("get_generator_cost", 1000):
        for _ in range(1000):
            state.get_generator_cost("rng", 1)
    
    with ProfilerTimer("can_afford", 10000):
        for _ in range(10000):
            state.can_afford(1000)
    
    with ProfilerTimer("is_generator_unlocked", 1000):
        for _ in range(1000):
            state.is_generator_unlocked("rng")
    
    with ProfilerTimer("get_upgrade_cost", 1000):
        for _ in range(1000):
            state.get_upgrade_cost("click_power")
    
    with ProfilerTimer("get_category_multiplier", 1000):
        for _ in range(1000):
            state.get_category_multiplier("cpu")
    
    with ProfilerTimer("is_upgrade_unlocked", 1000):
        for _ in range(1000):
            state.is_upgrade_unlocked("click_power")


def benchmark_game_state_era_specific():
    """Benchmark era-specific calculations"""
    print("\n=== Era-Specific Calculations ===")
    
    state = GameState()
    state.era = "entropy"
    state.bits = 1000000
    state.total_bits_earned = 5000000
    
    hw_gens = CONFIG.get("HARDWARE_GENERATORS", {})
    for gen_id in list(hw_gens.keys())[:4]:
        if gen_id in state.generators:
            state.generators[gen_id]["count"] = 50
    
    print("\nEntropy Era:")
    with ProfilerTimer("entropy get_production_rate", 500):
        for _ in range(500):
            state.get_production_rate()
    
    state.era = "compression"
    state.compressed_bits = 100000
    state.data_shards = 100
    
    if state.compression_generators:
        for gen_id in list(state.compression_generators.keys())[:2]:
            state.compression_generators[gen_id]["count"] = 20
    
    print("\nCompression Era:")
    with ProfilerTimer("compression get_production_rate", 500):
        for _ in range(500):
            state.get_production_rate()


def benchmark_rebirth_system():
    """Benchmark rebirth/prestige calculations"""
    print("\n=== Rebirth System Benchmarks ===")
    
    state = GameState()
    state.era = "entropy"
    state.bits = 10000000
    state.total_bits_earned = 100000000
    state.data_shards = 500
    state.total_data_shards = 1000
    state.hardware_generation = 3
    
    with ProfilerTimer("get_rebirth_progress", 1000):
        for _ in range(1000):
            state.get_rebirth_progress()
    
    with ProfilerTimer("get_rebirth_threshold", 1000):
        for _ in range(1000):
            state.get_rebirth_threshold()
    
    with ProfilerTimer("get_estimated_rebirth_tokens", 1000):
        for _ in range(1000):
            state.get_estimated_rebirth_tokens()
    
    with ProfilerTimer("get_hardware_generation_info", 1000):
        for _ in range(1000):
            state.get_hardware_generation_info()
    
    with ProfilerTimer("can_rebirth", 1000):
        for _ in range(1000):
            state.can_rebirth()


def benchmark_prestige_system():
    """Benchmark prestige calculations"""
    print("\n=== Prestige System Benchmarks ===")
    
    state = GameState()
    state.era = "entropy"
    state.total_bits_earned = 100000000
    state.prestige_currency = 100
    state.total_prestige_currency = 500
    state.prestige_count = 5
    state.hardware_generation = 3
    
    with ProfilerTimer("get_prestige_bonus", 1000):
        for _ in range(1000):
            state.get_prestige_bonus()
    
    with ProfilerTimer("get_click_prestige_bonus", 1000):
        for _ in range(1000):
            state.get_click_prestige_bonus()
    
    with ProfilerTimer("get_prestige_currency_earned", 1000):
        for _ in range(1000):
            state.get_prestige_currency_earned()
    
    with ProfilerTimer("can_prestige", 1000):
        for _ in range(1000):
            state.can_prestige()


def benchmark_compression_system():
    """Benchmark compression/Data Shard system"""
    print("\n=== Compression System Benchmarks ===")
    
    state = GameState()
    state.era = "compression"
    state.bits = 500000
    state.compressed_bits = 100000
    state.data_shards = 100
    state.last_collect_bits = 0
    
    state.compression_generators = {
        "zlib": {"count": 10, "total_bought": 10},
        "lzma": {"count": 5, "total_bought": 5},
    }
    
    state.data_shard_upgrades = {
        "compression_mastery": {"level": 3},
        "parallel_streams": {"level": 2},
        "efficiency_shield": {"level": 1},
        "entropy_barrier": {"level": 1},
        "quick_collect": {"level": 2},
        "shard_doubler": {"level": 1},
    }
    
    with ProfilerTimer("get_data_shards_earned", 1000):
        for _ in range(1000):
            state.get_data_shards_earned()
    
    with ProfilerTimer("get_collect_threshold", 1000):
        for _ in range(1000):
            state.get_collect_threshold()
    
    with ProfilerTimer("get_data_shard_upgrade_cost", 1000):
        for _ in range(1000):
            state.get_data_shard_upgrade_cost("compression_mastery")
    
    with ProfilerTimer("get_rebirth_shard_bonus", 1000):
        for _ in range(1000):
            state.get_rebirth_shard_bonus()
    
    with ProfilerTimer("can_collect_data_shards", 1000):
        for _ in range(1000):
            state.can_collect_data_shards()


def benchmark_visual_effects():
    """Benchmark visual effects - comprehensive"""
    print("\n=== Visual Effects Benchmarks ===")
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    print("\nParticle benchmarks:")
    for count in [10, 50, 100]:
        particles = [Particle(400, 300, COLORS["electric_cyan"], "burst") for _ in range(count)]
        
        with ProfilerTimer(f"Particle.update ({count} particles)", 60):
            for _ in range(60):
                for p in particles:
                    p.update(0.016)
        
        with ProfilerTimer(f"Particle.draw ({count} particles)", 60):
            for _ in range(60):
                screen.fill((0, 0, 0))
                for p in particles:
                    p.draw(screen)
    
    print("\nBinaryRain benchmarks:")
    rain = BinaryRain(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    with ProfilerTimer("BinaryRain.update", 60):
        for _ in range(60):
            rain.update(0.016)
    
    with ProfilerTimer("BinaryRain.draw", 60):
        for _ in range(60):
            screen.fill((0, 0, 0))
            rain.draw(screen)
    
    print("\nSmartBitVisualization benchmarks:")
    viz = SmartBitVisualization(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    
    for bits in [1000, 100000, 1000000]:
        with ProfilerTimer(f"SmartBitVisualization.update ({bits:,} bits)", 60):
            for _ in range(60):
                viz.update(bits, 0.016)
        
        with ProfilerTimer(f"SmartBitVisualization.draw ({bits:,} bits)", 60):
            for _ in range(60):
                screen.fill((0, 0, 0))
                viz.draw(screen, bits)


def benchmark_bit_grid():
    """Benchmark BitGrid operations - comprehensive"""
    print("\n=== BitGrid Benchmarks ===")
    
    grid = MotherboardBitGrid(100, 100, 600, 240)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    print("\nCore operations:")
    with ProfilerTimer("MotherboardBitGrid.update", 60):
        for _ in range(60):
            grid.update(1000, 1000, 10240, 0, 0.016)
    
    with ProfilerTimer("MotherboardBitGrid.draw", 60):
        for _ in range(60):
            screen.fill((0, 0, 0))
            grid.draw(screen)
    
    print("\nPercentage calculations:")
    grid.total_bits_earned = 100000
    
    with ProfilerTimer("get_era_completion_percentage", 1000):
        for _ in range(1000):
            grid.get_era_completion_percentage()
    
    with ProfilerTimer("get_bit_completeness_percentage", 1000):
        for _ in range(1000):
            grid.get_bit_completeness_percentage()
    
    print("\nScaling with bits:")
    for bits in [1000, 100000, 1000000, 10000000]:
        grid.total_bits_earned = bits
        with ProfilerTimer(f"get_bit_completeness_percentage ({bits:,})", 500):
            for _ in range(500):
                grid.get_bit_completeness_percentage()


def benchmark_ui_components():
    """Benchmark UI components"""
    print("\n=== UI Components Benchmarks ===")
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    print("\nButton benchmarks:")
    button = Button(100, 100, 200, 50, "Test Button", COLORS["electric_cyan"])
    
    with ProfilerTimer("Button.draw", 60):
        for _ in range(60):
            screen.fill((0, 0, 0))
            button.draw(screen)
    
    print("\nFloatingText benchmarks:")
    texts = [FloatingText(400, 300, "+1", COLORS["matrix_green"]) for _ in range(20)]
    
    with ProfilerTimer("FloatingText.update (20 texts)", 60):
        for _ in range(60):
            for text in texts:
                text.update(0.016)
    
    with ProfilerTimer("FloatingText.draw (20 texts)", 60):
        for _ in range(60):
            screen.fill((0, 0, 0))
            for text in texts:
                text.draw(screen)
    
    print("\nLayoutManager benchmarks:")
    layout = LayoutManager(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    with ProfilerTimer("LayoutManager.update_size", 100):
        for _ in range(100):
            layout.update_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    with ProfilerTimer("LayoutManager.get_top_bar_rect", 1000):
        for _ in range(1000):
            layout.get_top_bar_rect()
    
    with ProfilerTimer("LayoutManager.get_bottom_bar_rect", 1000):
        for _ in range(1000):
            layout.get_bottom_bar_rect()
    
    with ProfilerTimer("LayoutManager.get_bit_grid_rect", 1000):
        for _ in range(1000):
            layout.get_bit_grid_rect()
    
    with ProfilerTimer("LayoutManager.get_left_panel_rect", 1000):
        for _ in range(1000):
            layout.get_left_panel_rect()


def benchmark_save_load():
    """Benchmark save/load operations"""
    print("\n=== Save/Load Benchmarks ===")
    
    state = GameState()
    state.era = "entropy"
    state.bits = 1000000
    state.total_bits_earned = 5000000
    
    hw_gens = CONFIG.get("HARDWARE_GENERATORS", {})
    for gen_id in list(hw_gens.keys())[:4]:
        if gen_id in state.generators:
            state.generators[gen_id]["count"] = 50
    
    state.upgrades["click_power"]["level"] = 10
    
    import json
    
    save_data = {
        "bits": state.bits,
        "total_bits_earned": state.total_bits_earned,
        "generators": state.generators,
        "upgrades": state.upgrades,
        "era": state.era,
    }
    
    with ProfilerTimer("json.dumps (game state)", 500):
        for _ in range(500):
            json.dumps(save_data)
    
    json_str = json.dumps(save_data)
    
    with ProfilerTimer("json.loads (game state)", 500):
        for _ in range(500):
            json.loads(json_str)


def benchmark_generator_iteration():
    """Benchmark iterating over generators with production calculations"""
    print("\n=== Generator Iteration Benchmarks ===")
    
    state = GameState()
    state.era = "entropy"
    
    hw_gens = list(CONFIG.get("HARDWARE_GENERATORS", {}).keys())
    
    for count in [10, 50, 100, 500]:
        if hw_gens:
            gen_id = hw_gens[0]
            if gen_id in state.generators:
                state.generators[gen_id]["count"] = count
        
        with ProfilerTimer(f"get_production_rate ({count} gens)", 100):
            for _ in range(100):
                state.get_production_rate()


def benchmark_multiplier_calculations():
    """Benchmark multiplier calculations across categories"""
    print("\n=== Multiplier Calculation Benchmarks ===")
    
    state = GameState()
    state.era = "entropy"
    
    for upgrade_id in ["overclock", "memory_optimization", "data_compression"]:
        if upgrade_id in state.upgrades:
            state.upgrades[upgrade_id]["level"] = 3
    
    categories = ["cpu", "ram", "storage", "network", "gpu"]
    
    for cat in categories:
        with ProfilerTimer(f"get_category_multiplier ({cat})", 1000):
            for _ in range(1000):
                state.get_category_multiplier(cat)


def benchmark_led_grid():
    """Benchmark LEDGrid specifically"""
    print("\n=== LEDGrid Benchmarks ===")
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    from bit_grid import LEDGrid
    
    for exact_bits in [512, 4096, 16384]:
        rect = pygame.Rect(100, 100, 200, 100)
        led_grid = LEDGrid(rect, exact_bits)
        
        with ProfilerTimer(f"LEDGrid.update_fill ({exact_bits} bits)", 60):
            for _ in range(60):
                led_grid.update_fill(0.5)
        
        with ProfilerTimer(f"LEDGrid.render ({exact_bits} bits)", 60):
            for _ in range(60):
                screen.fill((0, 0, 0))
                led_grid.render(screen)


def cprofile_game_loop():
    """Profile the main game loop with cProfile"""
    print("\n=== cProfile: Game Loop Simulation ===")
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    state = GameState()
    state.era = "entropy"
    grid = MotherboardBitGrid(100, 100, 600, 240)
    rain = BinaryRain(WINDOW_WIDTH, WINDOW_HEIGHT)
    viz = SmartBitVisualization(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    
    def game_loop_frame():
        production = state.get_production_rate()
        state.bits = int(state.bits + production / 60)
        state.total_bits_earned = int(state.total_bits_earned + production / 60)
        
        rain.update(0.016)
        rebirth_threshold = state.get_rebirth_threshold()
        grid.update(state.bits, state.total_bits_earned, rebirth_threshold, state.hardware_generation, 0.016)
        viz.update(state.bits, 0.016)
        
        screen.fill((10, 12, 20))
        rain.draw(screen)
        grid.draw(screen)
        viz.draw(screen, state.bits)
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    for _ in range(60):
        game_loop_frame()
    
    profiler.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(30)
    print(s.getvalue())


def identify_bottlenecks():
    """Identify specific bottlenecks in rendering and updates"""
    print("\n=== Bottleneck Identification ===")
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    print("\nParticle scaling:")
    for count in [10, 50, 100, 500]:
        particles = [Particle(400, 300, COLORS["electric_cyan"], "burst") for _ in range(count)]
        
        start = time.perf_counter()
        for _ in range(60):
            for p in particles:
                p.update(0.016)
        update_time = time.perf_counter() - start
        
        start = time.perf_counter()
        for _ in range(60):
            screen.fill((0, 0, 0))
            for p in particles:
                p.draw(screen)
        draw_time = time.perf_counter() - start
        
        total_time = update_time + draw_time
        print(f"Particles={count:4d}: update={update_time*1000:6.1f}ms, draw={draw_time*1000:6.1f}ms, total_frame={total_time*1000:6.1f}ms")
    
    print("\nVisualization scaling:")
    for bits in [1000, 10000, 100000, 1000000, 10000000]:
        viz = SmartBitVisualization(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        
        for _ in range(30):
            viz.update(bits, 0.016)
        
        start = time.perf_counter()
        for _ in range(60):
            viz.update(bits, 0.016)
        update_time = time.perf_counter() - start
        
        start = time.perf_counter()
        for _ in range(60):
            screen.fill((0, 0, 0))
            viz.draw(screen, bits)
        draw_time = time.perf_counter() - start
        
        print(f"Bits={bits:>10,}: update={update_time*1000:6.1f}ms, draw={draw_time*1000:6.1f}ms")


def run_all_benchmarks():
    """Run all benchmark tests"""
    print("=" * 60)
    print("BIT BY BIT GAME - COMPREHENSIVE PROFILING BENCHMARKS")
    print("=" * 60)
    
    benchmark_game_state()
    benchmark_game_state_era_specific()
    benchmark_rebirth_system()
    benchmark_prestige_system()
    benchmark_compression_system()
    benchmark_visual_effects()
    benchmark_bit_grid()
    benchmark_ui_components()
    benchmark_save_load()
    benchmark_generator_iteration()
    benchmark_multiplier_calculations()
    benchmark_led_grid()
    cprofile_game_loop()
    identify_bottlenecks()
    
    print("\n" + "=" * 60)
    print("BENCHMARKS COMPLETE")
    print("=" * 60)
    print("\n=== KEY BOTTLENECKS IDENTIFIED ===")
    print("1. MotherboardBitGrid.draw - slow due to text rendering every frame")
    print("2. Particle.draw - pygame.draw.circle is slow for many particles")
    print("3. BinaryRain.draw - character rendering")
    print("4. Button.draw - similar pygame.draw issues")


if __name__ == "__main__":
    run_all_benchmarks()
    pygame.quit()
