"""Permanent restorations and presentation-only historical catalogue grouping."""
STAGES = ('Assembled', 'Refitted', 'Refined', 'Masterwork')
# These describe visible details, not simulated mechanisms or extra earnings sources.
DETAILS = {
    0: ('Rounded counting beads', 'Smooth bead profiles', 'Warm brass bead finish'),
    1: ('Open-spoke gear wheels', 'Machined hubs and fasteners', 'Engraved crank index'),
    2: ('Individual copper windings', 'Contact pilots and socket screws', 'Knurled tape-feed rollers'),
    3: ('Getter patches and support rods', 'Vented valve plates', 'Polished glass and sockets'),
    4: ('Gold card-edge contacts', 'Ceramic bypass capacitors', 'Machined metal-can packages'),
    5: ('Full Bloch reference grid', 'Cryostat machining and fasteners', 'Reconstructed state-vector trail'),
    6: ('Second orbit and guide stars', 'Three spiral streams and orbit markers', 'Full star field and result history'),
}


def technology_era(definition):
    """Catalogue location only; never changes introduction-era pricing or eligibility."""
    return definition.get('era', {'quantum': 5, 'hyper': 6, 'singularity': 6,
                                  'cosmic': 6}.get(definition.get('category'), 4))
