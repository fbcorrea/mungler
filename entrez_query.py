#!/gpfs1/data/mie/felipe/conda/envs/ollama/bin/python

import argparse
from Bio import Entrez
import os
import pandas as pd
import subprocess
from io import StringIO
import sys



# setting up query input fromn arguments
print("Setting up query input...")
argparser = argparse.ArgumentParser()
argparser.add_argument("--accession", type=str, help="The query text.", default="SAMN06512631")
# add email argument
argparser.add_argument("--email", type=str, help="The email for Entrez.", default="your-email")
args = argparser.parse_args()

Entrez.email = args.email

# Running biosample2table.py to convert the biosample data to a table
# print("Running biosample2table.py...")
# define options
options = f"-s {args.accession}"
# add email option
options += f" -e {args.email}"
# run biosample2table.py
results = subprocess.check_output(f"python biosample2table.py {options}", shell=True)

# # Convert the output to a DataFrame
results = pd.read_csv(StringIO(results.decode('utf-8')), sep='\t')
results = results.set_index(['BioSample']).stack().reset_index()

# add column with the accession args.accession as first column
results.insert(0, 'accession', args.accession)

# print to stdout
results.to_csv(sys.stdout, index=False, header=False, sep=',')
# save to file
results.to_csv("biosample.csv", index=False, header=False, sep=',')


link_result = Entrez.elink(dbfrom="biosample", id=args.accession, linkname="biosample_nucleotide")
record = Entrez.read(link_result)
print(record)
link_result.close()

#from Bio import Entrez
#Entrez.email = "Your.Name.Here@example.org"
# handle = Entrez.esummary(db="structure", id="19923")
# record = Entrez.read(handle)
# handle.close()
# print(record[0]["Id"])
# esummary_result = Entrez.esummary(db="biosample", id="SAMEA861651")

# # Use Entrez.elink to find related nucleotide IDs
# link_result = Entrez.elink(dbfrom="biosample", id="SAMEA861651", linkname="biosample_sra")
# record = Entrez.read(link_result)

# print(record)

# link_result.close()

# # Extract nucleotide IDs from the record
# nucleotide_ids = [link["Id"] for link in record[0]["LinkSetDb"][0]["Link"]]

# # Use Entrez.efetch to fetch details for each nucleotide ID
# for nucleotide_id in nucleotide_ids:
#     fetch_result = Entrez.efetch(db="nucleotide", id=nucleotide_id, retmode="xml")
#     fetch_record = Entrez.read(fetch_result)
#     fetch_result.close()
#     # Process fetch_record to extract and print desired metadata
#     print(fetch_record)  # Adjust this to extract specific fields you're interested in