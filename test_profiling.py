"""
Profiling tests for Bit by Bit Game
Run with: python -m pytest test_profiling.py -v --benchmark-only
Or manually: python test_profiling.py
"""

import pygame
import cProfile
import pstats
import io
import time
import math
import random
from unittest.mock import MagicMock

pygame.init()

from game_state import GameState
from bit_grid import MotherboardBitGrid
from visual_effects import (
    Particle, BinaryRain, SmartBitVisualization, BitVisualization, BitDot
)
from ui_components import Button, FloatingText, LayoutManager, GameUIState
from constants import COLORS, CONFIG, WINDOW_WIDTH, WINDOW_HEIGHT


class ProfilerTimer:
    """Context manager for timing code blocks"""
    def __init__(self, name):
        self.name = name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, *args):
        elapsed = time.perf_counter() - (self.start_time or 0)
        print(f"{self.name}: {elapsed*1000:.3f}ms")


def profile_function(func, *args, iterations=1000, **kwargs):
    """Profile a function and return timing statistics"""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(*args, **kwargs)
        times.append(time.perf_counter() - start)
    
    return {
        'mean': sum(times) / len(times),
        'min': min(times),
        'max': max(times),
        'total': sum(times),
    }


def print_profile_stats(stats, top_n=20):
    """Print profile statistics in readable format"""
    print(f"\n{'Function':<50} {'Calls':<10} {'Time (ms)':<15} {'Per Call':<15}")
    print("-" * 90)
    
    for func_name, call_info in list(stats.items())[:top_n]:
        total_time = call_info.get('total_time', 0)
        calls = call_info.get('calls', 0)
        per_call = total_time / calls if calls > 0 else 0
        print(f"{func_name:<50} {calls:<10} {total_time*1000:<15.3f} {per_call*1000:<15.3f}")


def benchmark_game_state():
    """Benchmark GameState methods"""
    print("\n=== GameState Benchmarks ===")
    
    state = GameState()
    state.era = "entropy"  # Ensure era is set
    
    # Simulate some game progress - use actual generator IDs from CONFIG
    state.generators["rng"]["count"] = 100
    state.generators["cpu_core"]["count"] = 50
    state.generators["memory_stick"]["count"] = 30
    state.generators["cpu_cache"]["count"] = 20
    state.generators["biased_coin"]["count"] = 10
    state.upgrades["click_power"]["level"] = 10
    state.upgrades["entropy_amplification"]["level"] = 5
    state.bits = 1000000
    state.total_bits_earned = 5000000
    
    # Benchmark get_production_rate
    with ProfilerTimer("get_production_rate"):
        for _ in range(1000):
            state.get_production_rate()
    
    # Benchmark get_click_power
    with ProfilerTimer("get_click_power"):
        for _ in range(1000):
            state.get_click_power()
    
    # Benchmark get_generator_cost
    with ProfilerTimer("get_generator_cost"):
        for _ in range(1000):
            state.get_generator_cost("rng", 1)
    
    # Benchmark can_afford
    with ProfilerTimer("can_afford"):
        for _ in range(10000):
            state.can_afford(1000)
    
    # Benchmark is_generator_unlocked
    with ProfilerTimer("is_generator_unlocked"):
        for _ in range(1000):
            state.is_generator_unlocked("rng")
    
    # Benchmark get_upgrade_cost
    with ProfilerTimer("get_upgrade_cost"):
        for _ in range(1000):
            state.get_upgrade_cost("click_power")
    
    # Benchmark get_category_multiplier
    with ProfilerTimer("get_category_multiplier"):
        for _ in range(1000):
            state.get_category_multiplier("cpu")
    
    # Benchmark is_upgrade_unlocked
    with ProfilerTimer("is_upgrade_unlocked"):
        for _ in range(1000):
            state.is_upgrade_unlocked("click_power")


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
    
    # Benchmark get_rebirth_progress
    with ProfilerTimer("get_rebirth_progress"):
        for _ in range(1000):
            state.get_rebirth_progress()
    
    # Benchmark get_rebirth_threshold
    with ProfilerTimer("get_rebirth_threshold"):
        for _ in range(1000):
            state.get_rebirth_threshold()
    
    # Benchmark get_estimated_rebirth_tokens
    with ProfilerTimer("get_estimated_rebirth_tokens"):
        for _ in range(1000):
            state.get_estimated_rebirth_tokens()
    
    # Benchmark get_hardware_generation_info
    with ProfilerTimer("get_hardware_generation_info"):
        for _ in range(1000):
            state.get_hardware_generation_info()


def benchmark_prestige_system():
    """Benchmark prestige calculations"""
    print("\n=== Prestige System Benchmarks ===")
    
    state = GameState()
    state.era = "entropy"
    state.total_bits_earned = 100000000
    state.prestige_currency = 100
    state.total_prestige_currency = 500
    
    # Benchmark get_prestige_bonus
    with ProfilerTimer("get_prestige_bonus"):
        for _ in range(1000):
            state.get_prestige_bonus()
    
    # Benchmark get_click_prestige_bonus
    with ProfilerTimer("get_click_prestige_bonus"):
        for _ in range(1000):
            state.get_click_prestige_bonus()
    
    # Benchmark get_prestige_currency_earned
    with ProfilerTimer("get_prestige_currency_earned"):
        for _ in range(1000):
            state.get_prestige_currency_earned()


def benchmark_compression_system():
    """Benchmark compression/Data Shard system"""
    print("\n=== Compression System Benchmarks ===")
    
    state = GameState()
    state.era = "compression"
    state.bits = 500000
    state.compressed_bits = 100000
    state.data_shards = 100
    
    # Benchmark get_data_shards_earned
    with ProfilerTimer("get_data_shards_earned"):
        for _ in range(1000):
            state.get_data_shards_earned()
    
    # Benchmark get_collect_threshold
    with ProfilerTimer("get_collect_threshold"):
        for _ in range(1000):
            state.get_collect_threshold()
    
    # Benchmark get_data_shard_upgrade_cost
    with ProfilerTimer("get_data_shard_upgrade_cost"):
        for _ in range(1000):
            state.get_data_shard_upgrade_cost("compression_efficiency")
    
    # Benchmark get_rebirth_shard_bonus
    with ProfilerTimer("get_rebirth_shard_bonus"):
        for _ in range(1000):
            state.get_rebirth_shard_bonus()


def benchmark_visual_effects():
    """Benchmark visual effects"""
    print("\n=== Visual Effects Benchmarks ===")
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Benchmark Particle update
    particles = [Particle(400, 300, COLORS["electric_cyan"], "burst") for _ in range(100)]
    
    with ProfilerTimer("Particle.update (100 particles)"):
        for _ in range(60):
            for p in particles:
                p.update(0.016)
    
    # Benchmark Particle draw
    with ProfilerTimer("Particle.draw (100 particles)"):
        for _ in range(60):
            screen.fill((0, 0, 0))
            for p in particles:
                p.draw(screen)
    
    # Benchmark BinaryRain
    rain = BinaryRain(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    with ProfilerTimer("BinaryRain.update"):
        for _ in range(60):
            rain.update(0.016)
    
    with ProfilerTimer("BinaryRain.draw"):
        for _ in range(60):
            screen.fill((0, 0, 0))
            rain.draw(screen)
    
    # Benchmark SmartBitVisualization
    viz = SmartBitVisualization(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    
    with ProfilerTimer("SmartBitVisualization.update (1K bits)"):
        for _ in range(60):
            viz.update(1000, 0.016)
    
    with ProfilerTimer("SmartBitVisualization.draw (1K bits)"):
        for _ in range(60):
            screen.fill((0, 0, 0))
            viz.draw(screen, 1000)
    
    with ProfilerTimer("SmartBitVisualization.update (1M bits)"):
        for _ in range(60):
            viz.update(1000000, 0.016)
    
    with ProfilerTimer("SmartBitVisualization.draw (1M bits)"):
        for _ in range(60):
            screen.fill((0, 0, 0))
            viz.draw(screen, 1000000)


def benchmark_bit_grid():
    """Benchmark BitGrid operations"""
    print("\n=== BitGrid Benchmarks ===")
    
    grid = MotherboardBitGrid(100, 100, 600, 240)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Benchmark update
    with ProfilerTimer("MotherboardBitGrid.update"):
        for _ in range(60):
            grid.update(1000, 1000, 10240, 0, 0.016)
    
    # Benchmark draw
    with ProfilerTimer("MotherboardBitGrid.draw"):
        for _ in range(60):
            screen.fill((0, 0, 0))
            grid.draw(screen)
    
    # Benchmark get_era_completion_percentage
    grid.total_bits_earned = 100000
    
    with ProfilerTimer("get_era_completion_percentage"):
        for _ in range(1000):
            grid.get_era_completion_percentage()
    
    # Benchmark get_bit_completeness_percentage
    with ProfilerTimer("get_bit_completeness_percentage"):
        for _ in range(1000):
            grid.get_bit_completeness_percentage()
    
    # Test with different bit scales
    for bits in [1000, 100000, 1000000, 10000000]:
        grid.total_bits_earned = bits
        with ProfilerTimer(f"get_bit_completeness_percentage ({bits:,} bits)"):
            for _ in range(500):
                grid.get_bit_completeness_percentage()


def benchmark_ui_components():
    """Benchmark UI components"""
    print("\n=== UI Components Benchmarks ===")
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Benchmark Button
    button = Button(100, 100, 200, 50, "Test Button", COLORS["electric_cyan"])
    
    with ProfilerTimer("Button.draw"):
        for _ in range(60):
            screen.fill((0, 0, 0))
            button.draw(screen)
    
    # Benchmark FloatingText
    texts = [FloatingText(400, 300, "+1", COLORS["matrix_green"]) for _ in range(20)]
    
    with ProfilerTimer("FloatingText.update (20 texts)"):
        for _ in range(60):
            for text in texts:
                text.update(0.016)
    
    with ProfilerTimer("FloatingText.draw (20 texts)"):
        for _ in range(60):
            screen.fill((0, 0, 0))
            for text in texts:
                text.draw(screen)
    
    # Benchmark LayoutManager - test layout calculations
    layout = LayoutManager(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    with ProfilerTimer("LayoutManager.update_size"):
        for _ in range(100):
            layout.update_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # Benchmark LayoutManager get_* methods
    with ProfilerTimer("LayoutManager.get_top_bar_rect"):
        for _ in range(1000):
            layout.get_top_bar_rect()
    
    with ProfilerTimer("LayoutManager.get_bottom_bar_rect"):
        for _ in range(1000):
            layout.get_bottom_bar_rect()
    
    with ProfilerTimer("LayoutManager.get_bit_grid_rect"):
        for _ in range(1000):
            layout.get_bit_grid_rect()
    
    with ProfilerTimer("LayoutManager.get_left_panel_rect"):
        for _ in range(1000):
            layout.get_left_panel_rect()


def benchmark_save_load():
    """Benchmark save/load operations"""
    print("\n=== Save/Load Benchmarks ===")
    
    state = GameState()
    state.era = "entropy"
    state.bits = 1000000
    state.total_bits_earned = 5000000
    state.generators["rng"]["count"] = 100
    state.generators["cpu_core"]["count"] = 50
    state.upgrades["click_power"]["level"] = 10
    
    # Benchmark save operation (JSON serialization)
    import json
    import io
    
    save_data = {
        "bits": state.bits,
        "total_bits_earned": state.total_bits_earned,
        "generators": state.generators,
        "upgrades": state.upgrades,
        "era": state.era,
    }
    
    with ProfilerTimer("json.dumps (game state)"):
        for _ in range(500):
            json.dumps(save_data)
    
    # Benchmark load operation (JSON deserialization)
    json_str = json.dumps(save_data)
    
    with ProfilerTimer("json.loads (game state)"):
        for _ in range(500):
            json.loads(json_str)


def benchmark_generator_iteration():
    """Benchmark iterating over generators with production calculations"""
    print("\n=== Generator Iteration Benchmarks ===")
    
    state = GameState()
    state.era = "entropy"
    
    # Set up generators with various counts
    gen_counts = [10, 50, 100, 500, 1000]
    
    for count in gen_counts:
        state.generators["rng"]["count"] = count
        
        with ProfilerTimer(f"get_production_rate (rng={count})"):
            for _ in range(100):
                state.get_production_rate()


def benchmark_multiplier_calculations():
    """Benchmark multiplier calculations across categories"""
    print("\n=== Multiplier Calculation Benchmarks ===")
    
    state = GameState()
    state.era = "entropy"
    state.upgrades["overclock"]["level"] = 10
    state.upgrades["memory_optimization"]["level"] = 5
    state.upgrades["data_compression"]["level"] = 3
    
    categories = ["cpu", "ram", "storage", "network", "gpu"]
    
    for cat in categories:
        with ProfilerTimer(f"get_category_multiplier ({cat})"):
            for _ in range(1000):
                state.get_category_multiplier(cat)


def cprofile_game_loop():
    """Profile the main game loop with cProfile"""
    print("\n=== cProfile: Game Loop Simulation ===")
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    state = GameState()
    state.era = "entropy"  # Set default era
    grid = MotherboardBitGrid(100, 100, 600, 240)
    rain = BinaryRain(WINDOW_WIDTH, WINDOW_HEIGHT)
    viz = SmartBitVisualization(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    
    # Simulate game loop for ~1 second (60 frames)
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
    
    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(25)
    print(s.getvalue())


def benchmark_memory_usage():
    """Check memory usage of key objects"""
    print("\n=== Memory Usage Estimates ===")
    
    import sys
    
    state = GameState()
    grid = MotherboardBitGrid(100, 100, 600, 240)
    rain = BinaryRain(WINDOW_WIDTH, WINDOW_HEIGHT)
    viz = SmartBitVisualization(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    
    # Create many objects
    particles = [Particle(400, 300) for _ in range(1000)]
    floating_texts = [FloatingText(400, 300, "+1", COLORS["matrix_green"]) for _ in range(100)]
    
    print(f"GameState: ~{sys.getsizeof(state)} bytes")
    print(f"MotherboardBitGrid: ~{sys.getsizeof(grid)} bytes")
    print(f"BinaryRain: ~{sys.getsizeof(rain)} bytes")
    print(f"SmartBitVisualization: ~{sys.getsizeof(viz)} bytes")
    print(f"1000 Particles: ~{sys.getsizeof(particles) + sum(sys.getsizeof(p) for p in particles)} bytes")
    print(f"100 FloatingTexts: ~{sys.getsizeof(floating_texts) + sum(sys.getsizeof(t) for t in floating_texts)} bytes")


def identify_bottlenecks():
    """Identify specific bottlenecks in rendering and updates"""
    print("\n=== Bottleneck Identification ===")
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Test with increasing particle counts
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
        fps = 60 / (total_time * 60 / 60)  # Approximate FPS
        
        print(f"Particles={count:4d}: update={update_time*1000:6.1f}ms, draw={draw_time*1000:6.1f}ms, total_frame={total_time*1000:6.1f}ms")
    
    # Test visualization with different bit values
    print("\nVisualization scaling:")
    for bits in [1000, 10000, 100000, 1000000, 10000000]:
        viz = SmartBitVisualization(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        
        # Pre-warm
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
    print("BIT BY BIT GAME - PROFILING BENCHMARKS")
    print("=" * 60)
    
    benchmark_game_state()
    benchmark_rebirth_system()
    benchmark_prestige_system()
    benchmark_compression_system()
    benchmark_visual_effects()
    benchmark_bit_grid()
    benchmark_ui_components()
    benchmark_save_load()
    benchmark_generator_iteration()
    benchmark_multiplier_calculations()
    cprofile_game_loop()
    benchmark_memory_usage()
    identify_bottlenecks()
    
    print("\n" + "=" * 60)
    print("BENCHMARKS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_all_benchmarks()
    pygame.quit()
