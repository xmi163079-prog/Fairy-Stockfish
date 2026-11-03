# Chees 620 — per-pawn first-double-step implementation contract

Status: implementation specification and acceptance tests. This file is not evidence that the engine feature is implemented.

## Rule

Every pawn has one lifetime entitlement to make a two-square forward move. The entitlement is attached to the pawn, not to a rank or square. It is consumed by its first move of any kind (single push, double push, or capture). A captured pawn's entitlement disappears. Promotion never transfers the entitlement to the promoted piece.

Pawns supplied in a Chees 620 starting position may begin on any legal pawn rank (2 through 7). Only pawns that have not moved receive the entitlement. A plain six-field FEN cannot represent this distinction for arbitrary midgame positions, so the engine/app boundary must serialize the entitlement explicitly.

## Required engine representation

- Keep two bitboards in the copied portion of StateInfo: white pawn entitlement squares and black pawn entitlement squares.
- Initialize them from the Chees 620 start position; parse and emit an explicit extension in the variant FEN for arbitrary positions. Do not infer rights from rank after a game has started.
- Include both bitboards in the full Zobrist position key. Otherwise transposition/repetition logic can conflate positions with different legal moves.
- In pawn move generation, intersect the normal double-step source set with the moving side's entitlement bitboard.
- In do_move, clear the moving pawn's source bit on every pawn move. Clear the captured pawn's bit on the actual capture square, including en passant. Do not set a bit on the destination. Undo must restore the previous StateInfo unchanged.
- Preserve ordinary chess, Chess960, and all existing variants when this feature is disabled.

## Suggested FEN extension

Use a variant-specific trailing field, for example `c620:<white-hex>:<black-hex>`, where each value is a 64-bit square mask. The parser must reject malformed masks and masks that point to squares without a pawn of the corresponding color. The serializer must round-trip the masks exactly. UCI position parsing must preserve the complete extension.

## Acceptance tests

1. A fresh white or black pawn on each rank 2–7 may double-step if both squares are clear.
2. A fresh pawn may single-step, but then cannot double-step later.
3. A fresh pawn may capture first, but then cannot double-step later.
4. Capturing an entitled pawn removes its entitlement; it must not reappear if another pawn later occupies that square.
5. En passant after a double-step is legal only on the immediately following ply; the captured pawn's entitlement is removed.
6. Promotion consumes the pawn's entitlement and does not transfer it to the promoted piece.
7. make/unmake restores both entitlement masks exactly.
8. Two otherwise identical boards with different entitlement masks have different position keys and are not treated as repetitions/transpositions.
9. FEN parse/serialize round-trips both masks and all ordinary fields.
10. Existing chess and Chess960 perft/legal-move tests remain unchanged.

## Required build split

- A (specialized): default variant is Chees 620; expose only the intended Chees 620 configuration in the shipped profile.
- B (multi-variant): register Chees 620 as a built-in UCI variant while retaining chess and Chess960. No external variants.ini is required.
- Both builds must run the acceptance tests above before being called complete. A branch name or successful compile alone is not proof of correct play.
