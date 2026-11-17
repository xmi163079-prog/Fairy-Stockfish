#!/usr/bin/env python3
"""Targeted Chees 620 pawn lifetime double-step regression checks."""
import re
import subprocess
import sys

ENGINE = "./src/stockfish"


def placement(pawn_color, rank):
    board = [["." for _ in range(8)] for _ in range(8)]
    board[0][0] = "K"       # a1
    board[7][7] = "k"       # h8
    board[rank - 1][3] = "P" if pawn_color == "white" else "p"
    rows = []
    for row in reversed(board):
        out = ""
        empty = 0
        for piece in row:
            if piece == ".":
                empty += 1
            else:
                if empty:
                    out += str(empty)
                    empty = 0
                out += piece
        if empty:
            out += str(empty)
        rows.append(out)
    return "/".join(rows)


def run_perft(fen):
    commands = (
        "setoption name UCI_Variant value chees620\n"
        f"position fen {fen}\n"
        "go perft 1\n"
        "quit\n"
    )
    result = subprocess.run(
        [ENGINE], input=commands, text=True, capture_output=True, timeout=20
    )
    output = result.stdout + result.stderr
    if result.returncode != 0 or "Nodes searched:" not in output:
        raise AssertionError(f"engine/perft failed for FEN: {fen}\n{output}")
    return output


def has_move(output, move):
    return re.search(rf"^{re.escape(move)}: [0-9]+$", output, re.MULTILINE) is not None


def check_origin(color, rank):
    square_index = (rank - 1) * 8 + 3  # file d, rank rank
    mask = 1 << square_index
    white_rights = mask if color == "white" else 0
    black_rights = mask if color == "black" else 0
    side = "w" if color == "white" else "b"
    move = f"d{rank}d{rank + 2 if color == 'white' else rank - 2}"
    promotion_destination = (color == "white" and rank == 6) or (color == "black" and rank == 3)
    expected_moves = [move + suffix for suffix in "qrbn"] if promotion_destination else [move]
    board = placement(color, rank)

    with_right = (
        f"{board} {side} - - 0 1 "
        f"c620:{white_rights:x}:{black_rights:x}"
    )
    without_right = f"{board} {side} - - 0 1 c620:0:0"

    with_right_output = run_perft(with_right)
    without_right_output = run_perft(without_right)
    if not any(has_move(with_right_output, candidate) for candidate in expected_moves):
        raise AssertionError(
            f"{color} pawn from d{rank}: expected one of {expected_moves} with right"
        )
    if any(has_move(without_right_output, candidate) for candidate in expected_moves):
        raise AssertionError(
            f"{color} pawn from d{rank}: double-step appeared without right"
        )


def main():
    # All in-board two-square origins are covered. A two-square move that
    # lands on the promotion rank must carry a promotion suffix.
    for rank in range(2, 7):
        check_origin("white", rank)
    for rank in range(3, 8):
        check_origin("black", rank)

    # White rank 7 and black rank 2 still have an entitlement, but a two-square
    # move would leave the board, so no such move may be generated.
    for color, rank, move in (
        ("white", 7, "d7d9"),
        ("black", 2, "d2d0"),
    ):
        square_index = (rank - 1) * 8 + 3
        mask = 1 << square_index
        white_rights = mask if color == "white" else 0
        black_rights = mask if color == "black" else 0
        side = "w" if color == "white" else "b"
        fen = (
            f"{placement(color, rank)} {side} - - 0 1 "
            f"c620:{white_rights:x}:{black_rights:x}"
        )
        if has_move(run_perft(fen), move):
            raise AssertionError(f"{color} pawn from d{rank}: generated off-board move {move}")

    # A pawn's first move consumes its right; it cannot double-step later.
    fen = (
        "7k/8/8/8/3P4/8/8/K7 w - - 0 1 "
        "c620:8000000:0"
    )
    output = run_perft_after_moves(fen, "d4d5 h8g8")
    if has_move(output, "d5d7"):
        raise AssertionError("White pawn regained its double-step right after d4-d5")

    print("Chees 620 pawn-origin rights: 10/10 in-board origins passed")
    print("Chees 620 off-board edge origins: 2/2 correctly excluded")
    print("Chees 620 first-move consumption: passed")


def run_perft_after_moves(fen, moves):
    commands = (
        "setoption name UCI_Variant value chees620\n"
        f"position fen {fen} moves {moves}\n"
        "go perft 1\n"
        "quit\n"
    )
    result = subprocess.run(
        [ENGINE], input=commands, text=True, capture_output=True, timeout=20
    )
    output = result.stdout + result.stderr
    if result.returncode != 0 or "Nodes searched:" not in output:
        raise AssertionError(f"engine/perft failed after moves {moves}\n{output}")
    return output


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Chees 620 pawn-right regression FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
