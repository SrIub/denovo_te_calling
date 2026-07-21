import sys
from collections import defaultdict

def log(msg):
    sys.stderr.write(f"{msg}")
    sys.stderr.flush()

def parse_blast(blast_file):
    # Accumulate family hit counts keyed by locus (chrom, pos1, pos2)
    # hit_counts[(chrom, pos1, pos2)][family] = count
    hit_counts = defaultdict(lambda: defaultdict(int))
 
    with open(blast_file) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            contig_id = fields[0]
            family    = fields[1]
 
            parts = contig_id.split("_")
 
            chrom = "_".join(parts[:-3])
            pos1  = parts[-3]
            pos2  = parts[-2]
            hit_counts[(chrom, pos1, pos2)][family] += 1
 
    # Resolve best family per locus
    results = {}
    for (chrom, pos1, pos2), family_counts in hit_counts.items():
        max_count = max(family_counts.values())
        best_families = sorted(
            fam for fam, cnt in family_counts.items() if cnt == max_count
        )
        results[(chrom, pos1, pos2)] = {
            "blast_id": ",".join(best_families),
        }
 
    return results

def parse_temp2(temp2_file):
    temp2_dict = {}
 
    with open(temp2_file) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            
            chrom    = fields[0]
            pos1     = fields[1]
            pos2     = fields[2]
            temp2_id = fields[3]
 
            key = (chrom, int(pos1))
            temp2_dict[key] = temp2_id
 
    return temp2_dict

def main():
    blast_file  = sys.argv[1]
    temp2_file  = sys.argv[2]
    sample  = sys.argv[3]
    output = sys.argv[4]
    window = sys.argv[5]

    blast_data = parse_blast(blast_file)
    temp2_data  = parse_temp2(temp2_file)
    
    with open(output, "w") as out:
        out.write("Chr\tPos1\tPos2\tBlast_ID\tTemp2_ID\tSample\n")
        for (chrom, pos1, pos2), info in sorted(blast_data.items()):
            blast_id = info["blast_id"]
            temp2_chrom = f"{chrom}"
            key = (temp2_chrom, int(pos1)+int(window))
            temp2_id = temp2_data.get(key)
            out.write(f"{chrom}\t{pos1}\t{pos2}\t{blast_id}\t{temp2_id}\t{sample}\n")

main()
