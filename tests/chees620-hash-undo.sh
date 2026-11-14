#!/usr/bin/env bash
set -euo pipefail

# Perft recursively makes and unmakes moves. Compare the root Zobrist key
# before and after a tree containing a capture of an entitled Chees 620 pawn.
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

cat > "$tmp" <<'EXPECT'
set timeout 120
spawn ./src/stockfish
send "setoption name UCI_Variant value chees620\n"
send "position fen 7k/8/8/3p4/4P3/8/8/4K3 w - - 0 1 c620:10000000:800000000\n"
send "d\n"
expect -re {Key: ([0-9A-F]+)}
set before $expect_out(1,string)
send "go perft 3\n"
expect -re {Nodes searched: [0-9]+}
send "d\n"
expect -re {Key: ([0-9A-F]+)}
set after $expect_out(1,string)
if {$before ne $after} {
    puts stderr "Chees 620 hash/undo mismatch: before=$before after=$after"
    exit 1
}
puts "Chees 620 hash/undo root-key check passed: $before"
send "quit\n"
expect eof
EXPECT

expect "$tmp"
