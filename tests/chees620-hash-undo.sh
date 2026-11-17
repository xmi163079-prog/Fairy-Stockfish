#!/usr/bin/env bash
set -euo pipefail

# Verify that a real capture updates the Zobrist key exactly like loading the
# equivalent resulting FEN with the captured pawn's entitlement removed.
# Then verify Perft make/unmake restores the original root key.
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

cat > "$tmp" <<'EXPECT'
set timeout 120
spawn ./src/stockfish
send "setoption name UCI_Variant value chees620\n"

send "position fen 7k/8/8/3p4/4P3/8/8/4K3 w - - 0 1 c620:10000000:800000000 moves e4d5\n"
send "d\n"
expect -re {Key: ([0-9A-F]+)}
set after_capture $expect_out(1,string)

send "position fen 7k/8/8/3P4/8/8/8/4K3 b - - 0 1 c620:0:0\n"
send "d\n"
expect -re {Key: ([0-9A-F]+)}
set expected_after_capture $expect_out(1,string)

if {$after_capture ne $expected_after_capture} {
    puts stderr "Chees 620 capture hash mismatch: actual=$after_capture expected=$expected_after_capture"
    exit 1
}
puts "Chees 620 capture hash equivalence passed: $after_capture"

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
