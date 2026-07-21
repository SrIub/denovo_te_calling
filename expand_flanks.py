"""Expand the flanks of TEMP2's de novo TE annotations by +- 500 bp"""
import sys

window = 500

def load_calls(calls):
    TE_locations = []
    with open(calls) as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split('\t')
            chrom, pos1, pos2 = parts[0], parts[1], parts[2]
            TE_locations.append((chrom, int(pos1), int(pos2)))
    return TE_locations

def expand_flanks(TE_locations, window = 500):
    expanded = []
    for chrom, pos1, pos2 in TE_locations:
        start = max(0, pos1 - window)
        end = pos2 + window
        expanded.append((chrom, int(start), int(end)))
    return expanded

def main():
    calls = sys.argv[1]
    output = sys.argv[2]
    TEs = load_calls(calls)
    expanded = expand_flanks(TEs)
    with open(output, 'w') as f:
        for chrom, start, end in expanded:
            f.write(f"{chrom}\t{start}\t{end}\n")

if __name__ == '__main__':
    main()

