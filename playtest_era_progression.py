"""Deterministic no-save pacing probe, not a promise about every play style.

Start with ten real clicks, then rely entirely on idle income. Once per simulated
second, buy affordable machines by current production/cost, at most 12 purchases.
After advancing, save for the entry machine before buying anything else; advance
again only after buying that starter. Compare Define Bit only with all research. Never inject money,
grant generators, auto-prestige or change prices. Fail on any era income drop.
"""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from constants import get_all_generators
from game_state import GameState


def simulate(research=False, seconds=3600):
    state = GameState()
    definitions = get_all_generators()
    for _ in range(10):
        state.add_manual_currency()
    assert state.purchase_generator('pebble')
    entries = []
    starters = {1: 'lever', 2: 'relay', 3: 'vacuum_diode', 4: 'cpu_core'}
    zero_income_seconds = 0
    for second in range(seconds):
        rate = state.get_production_rate()
        if rate <= 0:
            zero_income_seconds += 1
        state.add_idle_currency(rate)
        if state.can_define_bit():
            state.perform_define_bit()
        if research:
            for project in state.get_research_projects():
                if project['ready']:
                    state.complete_research(project['id'])
        if state.can_advance_era() and (not entries or entries[-1]['first_new_machine_after'] is not None):
            before = state.get_production_rate()
            state.advance_era()
            after = state.get_production_rate()
            assert after >= before > 0, 'Era advancement retired existing income'
            entries.append(dict(era=state.current_era, entered_at=second,
                                carried_production=round(after, 2), first_new_machine_after=None))
        for _ in range(12):
            if entries and entries[-1]['first_new_machine_after'] is None:
                key = starters[state.current_era]
                if not state.is_era_generator_unlocked(key) or not state.purchase_generator(key):
                    break
                entries[-1]['first_new_machine_after'] = second - entries[-1]['entered_at']
                continue
            candidates = []
            for key, definition in definitions.items():
                if not state.is_era_generator_unlocked(key):
                    continue
                cost = state.get_generator_cost(key)
                if cost > state.get_active_currency_value():
                    continue
                category = definition.get('category')
                bonus = (state.get_era_upgrade_multiplier(category) if state.get_generator_era(key) < 4
                         else state.get_category_multiplier(category))
                unit = definition['base_production'] * bonus
                candidates.append((cost / max(unit, 0.001), key))
            if not candidates:
                break
            _, key = min(candidates)
            assert state.purchase_generator(key)
            if entries and state.get_generator_era(key) == state.current_era:
                entry = entries[-1]
                if entry['first_new_machine_after'] is None:
                    entry['first_new_machine_after'] = second - entry['entered_at']
        # Eras 5/6 currently reuse modern hardware rather than a new generator family.
        if state.current_era >= 4 and entries[-1]['first_new_machine_after'] is not None:
            break
    assert zero_income_seconds == 0, f'{zero_income_seconds} seconds without income'
    assert state.current_era >= 4, 'Did not reach modern hardware within the probe limit'
    return entries


def main():
    for research in (False, True):
        print('\nPolicy:', 'claim available research' if research else 'Define Bit only')
        for entry in simulate(research):
            print(f"Era {entry['era']}: entry t={entry['entered_at']}s; "
                  f"carried +{entry['carried_production']}/s; "
                  f"starter purchased after {entry['first_new_machine_after']}s")
    print('\nPASS: no zero-income intervals or production loss at advancement')


if __name__ == '__main__':
    main()
