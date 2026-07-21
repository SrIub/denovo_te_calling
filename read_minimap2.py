import sys
import re

def log(msg):
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()

def parse_minimap_line(line):
    fields = line.strip().split()

    chrom = fields[0].split("_")[0]
    pos1 = int(fields[1])
    pos2 = int(fields[2])

    contig_info = fields[5].split("_")
    og_chrom = "_".join(contig_info[:-3])
    #rag = contig_info[1]
    og_pos1 = int(contig_info[-3])
    og_pos2 = int(contig_info[-2])
    contig_id = contig_info[-1]

    cigar = None
    for f in fields[12:]:
        if f.startswith("cg:Z:"):
            cigar = f.split(":")[-1]
            break

    return chrom, pos1, pos2, og_chrom, og_pos1, og_pos2, contig_id, cigar

def load_paf(paf):
    with open(paf) as f:
        for line in f:
            if not line.strip():
                continue
            if len(line.split()) < 12:
                continue
            yield parse_minimap_line(line)

def is_nearby(chrom, pos1, pos2, og_chrom, og_pos1, og_pos2, buffer=5000):
    if chrom != og_chrom:
        return False

    # expand TE region
    start = og_pos1 - buffer
    end = og_pos2 + buffer

    # check overlap
    return not (pos2 < start or pos1 > end)

def has_gap(cigar, threshold=50, edge_buffer=50, soft_clip_min=20):
    ops = re.findall(r"(\d+)([MIDNSHP=X])", cigar)
    ref_span = sum(int(l) for l, op in ops if op in "MDN=X")
    ref_pos = 0
    for length, op in ops:
        length = int(length)
        if op == "S" and length >= soft_clip_min:
            return True
        if op in ("D", "N") and length >= threshold:
            gap_mid = ref_pos + (length // 2)
            if edge_buffer < gap_mid < (ref_span - edge_buffer):
                return True
        if op == "I" and length >= threshold:
            if edge_buffer < ref_pos < (ref_span - edge_buffer):
                return True
        if op in "MDN=X":
            ref_pos += length
    return False

def main():
    paf_file = sys.argv[1]
    output_file = sys.argv[2]
    blast_candidates = set()
    not_denovo = set()

    for chrom, pos1, pos2, og_chrom, og_pos1, og_pos2, contig_id, cigar in load_paf(paf_file):
        contig_name = f"{og_chrom}_{og_pos1}_{og_pos2}_{contig_id}"
        nearby = is_nearby(chrom, pos1, pos2, og_chrom, og_pos1, og_pos2)
        if nearby and not has_gap(cigar):
            not_denovo.add(contig_name)
            blast_candidates.discard(contig_name)
        elif contig_name not in not_denovo:
            blast_candidates.add(contig_name)
    
    with open(output_file, "w") as f:
        for name in blast_candidates:
            f.write(f"{name}\n")
    log(f"BLAST candidates: {len(blast_candidates)}")

main()
