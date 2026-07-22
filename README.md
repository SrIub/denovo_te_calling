# De Novo TE Calling Pipeline

A pipeline for detecting non-reference (de novo) transposable element insertions from paired-end short-read sequencing data. Uses [TEMP2](https://github.com/weng-lab/TEMP2) for initial insertion calling, followed by local assembly (SPAdes) and BLAST verification.

## Requirements

- [Conda](https://docs.conda.io/) or [Mamba](https://github.com/mamba-org/mamba) (recommended)
- Git
- A SLURM cluster (TEMP2 requires `$SLURM_SUBMIT_DIR`)

## Installation

```bash
git clone https://github.com/SrIub/denovo_te_calling.git
cd denovo_te_calling
mamba env create -f environment.yml
conda activate denovo_te
bash setup.sh
```

> **Note:** On HPC clusters, conda may need to be initialized before use. This is typically done with `module load anaconda/miniconda` or by sourcing a conda init script.

`setup.sh` clones TEMP2 from GitHub into the pipeline directory. It only needs to be run once.

## Preparing Inputs

### Reference genome
The reference FASTA must be indexed with BWA before running:
```bash
bwa index reference.fasta
```

### TE consensus and BLAST database
If running on *D. melanogaster*, the bundled Dmel v10.2 consensus and BLAST database are used by default — no extra steps needed.

For other species, provide your own consensus FASTA (`-R`) and a pre-built BLAST database (`-B`):
```bash
makeblastdb -in your_consensus.fa -dbtype nucl -out your_consensus_db
```

### FASTQ files
Input FASTQs should be adapter-trimmed (e.g. with Trim Galore) before running.

## Usage
Run from within an active SLURM job with the conda environment activated:
```bash
conda activate denovo_te
bash denovo_te_calling.sub \
  -s SAMPLE \
  -l R1.fq \
  -r R2.fq \
  -i sample.bam \
  -g reference.fasta \
  -a annotation.bed
```

### Required flags

| Flag | Description |
|------|-------------|
| `-s SAMPLE` | Sample name (used for output file naming) |
| `-l FQ1` | Path to trimmed R1 FASTQ |
| `-r FQ2` | Path to trimmed R2 FASTQ |
| `-i BAM` | Path to BAM file |
| `-g REFERENCE` | Reference genome FASTA (full path, must be BWA indexed) |
| `-a ANNOTATION` | BED file of reference TE annotations (used to exclude existing insertions) |

### Optional flags

| Flag | Default | Description |
|------|---------|-------------|
| `-e EUCHROMATIN` | *(all regions kept)* | BED file of euchromatic regions. If provided, calls are restricted to these regions. Useful for filtering out heterochromatic false positives |
| `-t THREADS` | `1` | Number of threads |
| `-o OUTPUT` | `SAMPLE-Calls` | Output directory |
| `-w WINDOW` | `500` | Flanking window size (bp) used when matching BLAST results back to TEMP2 calls |
| `-R CONSENSUS` | Bundled Dmel v10.2 | TE consensus FASTA for TEMP2 and BLAST |
| `-B BLAST_DB` | Bundled Dmel v10.2 | BLAST database prefix (must match `-R` if overriding) |

## Output

A TSV file named `SAMPLE_denovo_TEs.tsv` with the following columns:

| Column | Description |
|--------|-------------|
| `Chr` | Chromosome |
| `Pos1` | Start position of insertion |
| `Pos2` | End position of insertion |
| `Blast_ID` | TE family identified by BLAST |
| `Temp2_ID` | TE family identified by TEMP2 |
| `Sample` | Sample name |

## Notes

- **INE-1 filtering:** INE-1 insertions are automatically removed from TEMP2 calls before downstream analysis, as they are abundant reference-strain insertions that frequently produce false positives.
- **TEMP2 mode:** The pipeline runs TEMP2 in `insertion2` mode, which detects germline insertions only (not somatic).
- **Cleanup:** Intermediate files are removed automatically after the TSV is written.
