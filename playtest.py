"""Deterministic headless play-test for Bit by Bit.

This is intentionally small and read-only: it creates an in-memory GameState,
replays a few player actions, and reports progression blockers instead of
writing a save file or launching a window.

Run with:
    python playtest.py
"""

from __future__ import annotations

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

from constants import ERAS, PRESTIGE_UPGRADES
from game_state import GameState


def gui_click(state: GameState) -> None:
    """Use the same state API that the real GUI now calls."""
    state.add_manual_currency()


def report(label: str, passed: bool, detail: str) -> None:
    marker = "PASS" if passed else "FINDING"
    print(f"[{marker}] {label}: {detail}")


def main() -> int:
    state = GameState()
    findings = 0

    # 1. Verify the starting state and replay the first ten manual clicks.
    report(
        "starting state",
        state.current_era == 0 and state.get_current_currency() == "pebbles",
        f"era={state.current_era}, currency={state.get_current_currency()}, "
        f"value={state.get_current_currency_value()}",
    )

    for _ in range(10):
        gui_click(state)

    click_currency_ok = state.pebbles == 10 and state.bits == 0
    if not click_currency_ok:
        findings += 1
    report(
        "manual click currency routing",
        click_currency_ok,
        f"after 10 clicks: pebbles={state.pebbles}, bits={state.bits}, "
        f"total_pebbles={state.total_pebbles_earned}, total_bits={state.total_bits_earned}",
    )

    # 2. Confirm the first documented milestone cannot be reached through the
    # actual click path when the game starts in the Pebble currency.
    for _ in range(PRESTIGE_UPGRADES["define_bit"]["unlock_threshold"]):
        gui_click(state)
    define_bit_ok = state.can_define_bit()
    if not define_bit_ok:
        findings += 1
    report(
        "Define Bit milestone",
        define_bit_ok,
        f"threshold={PRESTIGE_UPGRADES['define_bit']['unlock_threshold']}, "
        f"total_pebbles={state.total_pebbles_earned}, can_define_bit={define_bit_ok}",
    )

    # 3. Verify early generator purchases spend Pebbles, not Bits.
    purchase_state = GameState()
    purchase_state.pebbles = 20
    pebble_cost = purchase_state.get_era_generator_cost("pebble")
    purchased = purchase_state.purchase_generator("pebble")
    purchase_ok = (
        purchased
        and purchase_state.pebbles == 20 - pebble_cost
        and purchase_state.bits == 0
        and purchase_state.generators["pebble"]["count"] == 1
    )
    if not purchase_ok:
        findings += 1
    report(
        "early generator currency routing",
        purchase_ok,
        f"cost={pebble_cost}, pebbles={purchase_state.pebbles}, "
        f"bits={purchase_state.bits}, count={purchase_state.generators['pebble']['count']}",
    )

    # 4. Exercise the pure state transition with a valid in-memory milestone
    # to distinguish a progression-model issue from the input-routing issue.
    state.total_pebbles_earned = PRESTIGE_UPGRADES["define_bit"]["unlock_threshold"]
    state.pebbles = PRESTIGE_UPGRADES["define_bit"]["unlock_threshold"]
    define_result = state.perform_define_bit()
    report(
        "Define Bit state transition",
        bool(define_result) and state.binary_invented,
        f"result={define_result}, binary_invented={state.binary_invented}, "
        f"bits={state.bits}, binary_efficiency={state.binary_efficiency}",
    )

    # 4. Check that the next era can be reached using its documented threshold
    # when the state is set to the appropriate currency.
    next_era = ERAS[1]
    state.bits = next_era["unlock_bits"]
    state.total_bits_earned = next_era["unlock_bits"]
    advance_ok = state.can_advance_era() and state.advance_era()
    report(
        "era advancement",
        advance_ok and state.current_era == 1,
        f"required={next_era['unlock_bits']}, era={state.current_era}, "
        f"currency={state.get_current_currency()}, can_advance={advance_ok}",
    )

    # 5. Check for a visible API mismatch: README says compression/data shards
    # are available after rebirth, while perform_rebirth currently requires the
    # motherboard threshold and resets bits. This is informational unless the
    # transition itself fails.
    state.hardware_generation = 0
    state.bits = state.get_rebirth_threshold()
    state.total_bits_earned = state.bits
    rebirth_result = state.perform_rebirth()
    rebirth_ok = bool(rebirth_result)
    shard_balance_ok = state.data_shards >= 0
    report(
        "rebirth transition",
        rebirth_ok,
        f"result={rebirth_result}, data_shards={state.data_shards}, "
        f"era={state.era}, hardware_generation={state.hardware_generation}",
    )
    report(
        "rebirth shard balance",
        shard_balance_ok,
        f"data_shards_after_first_threshold_rebirth={state.data_shards}",
    )
    if not rebirth_ok:
        findings += 1
    if not shard_balance_ok:
        findings += 1

    print(f"\nSUMMARY: {findings} progression finding(s) detected")
    pygame.quit()
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
