"""
Usage: python extract_contigs.py <candidates.txt> <input.fasta> <output.fasta>
"""

import sys

def extract_contigs(candidates_file, fasta_file, output_file):
    # Load the target contig names into a set
    with open(candidates_file) as f:
        targets = set(line.strip() for line in f if line.strip())
    found = set()
    writing = False
    with open(fasta_file) as fin, open(output_file, "w") as fout:
        for line in fin:
            if line.startswith(">"):
                contig_name = line[1:].strip()
                if contig_name in targets:
                    writing = True
                    found.add(contig_name)
                    fout.write(line)
                else:
                    writing = False
            elif writing:
                fout.write(line)
    missing = targets - found


if __name__ == "__main__":
    extract_contigs(sys.argv[1], sys.argv[2], sys.argv[3])
