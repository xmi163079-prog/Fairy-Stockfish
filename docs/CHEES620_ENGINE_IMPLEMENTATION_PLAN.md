# Chees 620 engine integration plan

Status: design/audit only. This file does NOT claim that Chees 620 is implemented.

## Required rule

Each pawn has one individual right to make a two-square advance. The right exists only until that pawn makes its first move. A pawn may start on any rank permitted by the Chees 620 starting-position generator; therefore the right cannot be inferred from rank 2/7 or from the current square. A one-square move, capture, promotion, or any other pawn move consumes the right permanently.

## Required engine state

- Store the remaining double-step entitlement per pawn, keyed to its current square and color (or an equivalent identity-safe representation).
- Initialize entitlements from the Chees 620 start position / explicit extended position metadata, not from the ordinary FEN rank rule.
- On every pawn move, consume the source pawn's entitlement; never transfer it to the destination square.
- On captures, remove any entitlement attached to the captured pawn.
- Preserve the previous entitlement state in StateInfo so do_move/undo_move and search null-move paths restore it exactly.
- Include entitlement state in the full Zobrist position key so transpositions and repetition distinguish positions with different legal moves.
- Ensure pawn hash/evaluation caches are either updated or deliberately remain independent of this rule.
- Generate a double push only when that exact pawn still has entitlement and all intermediate/destination squares are clear.
- En-passant target creation must follow the existing variant rules and only follow a valid two-square move; it expires normally after the opponent's reply.
- Promotions must consume the pawn entitlement and must not grant it to the promoted piece.

## Serialization and protocol

Ordinary six-field FEN cannot encode per-pawn entitlement. Chees 620 therefore needs a documented extended FEN field or equivalent UCI position metadata. Parsing and printing must round-trip it. A plain FEN import needs an explicit, deterministic policy and must not silently claim that all pawns retain their rights.

## Built-in variants

Register a built-in `chees620` variant in VariantMap::init() so users do not need a separate variants.ini file. The specialized build should default UCI_Variant to chees620. The multi-variant build should retain chess/chess960 and expose chees620 as a selectable UCI_Variant.

## Mandatory tests before calling this complete

1. A pawn starting on each supported rank can double-step exactly once if entitled.
2. After a one-step move, the same pawn cannot double-step later.
3. After a capture, the capturing pawn cannot double-step later.
4. Capturing an entitled pawn removes its entitlement.
5. Undo restores the exact entitlement state.
6. Search make/unmake and null-move paths preserve state and hash.
7. Distinct entitlement states produce distinct position keys.
8. FEN/extended metadata round-trips through UCI position setup.
9. En-passant is available only immediately after a legal double-step.
10. Standard chess and Chess960 behavior remains unchanged.

## Branch intent

- `chees620/pawn-first-double-step-specialized`: dedicated Chees 620 engine, default variant Chees 620.
- `chees620/pawn-first-double-step-check2`: multi-variant engine, Chees 620 selectable without an external variant file.

Do not merge either branch or publish a binary until implementation, compilation, and the test matrix above have passed.
