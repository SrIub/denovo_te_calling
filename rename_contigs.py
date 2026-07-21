"""
rename_contigs.py

Renames and combines SPAdes contigs from all region directories into a single FASTA file.

Sample command:
python post_spades.py /path/to/named_spades_dir /path/to/output/sample_contigs.fasta

Inputs:
- named_spades_dir: Directory containing subfolders for each region (e.g., named_spades/)
- output_fasta: Path to the final combined and renamed contigs file

Outputs:
- Renamed contigs saved per region as <region_name>_contigs.fasta in each region folder
- Combined FASTA of all contigs written to output_fasta
- Logs written to stderr
"""

import sys
from pathlib import Path

def log(msg):
    """
    Write a message to stderr.
    """
    sys.stderr.write(f"{msg}\n")
    sys.stderr.flush()

def rename_contigs(contig_path: Path, new_path: Path, region_name: str):
    """
    Rename each SPAdes contig header with the region name and a unique number.
    Writes the renamed FASTA to a new file.
    """
    with contig_path.open() as infile, new_path.open("w") as outfile:
        count = 1
        for line in infile:
            if line.startswith(">NODE_"):
                outfile.write(f">{region_name}_{count}\n")
                count += 1
            else:
                outfile.write(line)
    log(f"[rename_contigs] Renamed and saved {region_name}_contigs.fasta")

def main():
    """
    Iterate over each region directory, rename SPAdes contigs, and concatenate into one output contig file.
    """
    if len(sys.argv) != 3:
        print("Usage: python post_spades.py <named_spades_dir> <output_fasta>")
        sys.exit(1)

    named_spades_dir = Path(sys.argv[1])
    output_fasta = Path(sys.argv[2])

    output_fasta.parent.mkdir(parents=True, exist_ok=True)

    with output_fasta.open("w") as out_concat:
        for region_dir in sorted(named_spades_dir.iterdir()):
            if not region_dir.is_dir():
                continue
            region_name = region_dir.name
            contig_path = region_dir / "spades" / "contigs.fasta"
            if not contig_path.exists():
                log(f"[SKIP] No contigs found for {region_name}")
                continue

            renamed_path = region_dir / f"{region_name}_contigs.fasta"
            try:
                rename_contigs(contig_path, renamed_path, region_name)
                with renamed_path.open() as r:
                    out_concat.write(r.read())
            except Exception as e:
                log(f"[ERROR] Failed processing {region_name}: {e}")

    log(f"[DONE] Combined contigs written to {output_fasta}")

if __name__ == "__main__":
    main()


