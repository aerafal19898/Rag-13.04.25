#!/usr/bin/env python
"""
Test script for semantic chunking feature.
"""

import os
import sys
from pathlib import Path

# Add project directories to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

from app.utils.document_processor import LegalDocumentProcessor
from app.config import CHROMA_DIR, EMBEDDING_MODEL

print("Testing Semantic and Recursive Chunking")
print("-------------------------------------")

# Create a sample legal text
sample_text = """
Article 1: General Provisions

1.1 This regulation establishes the framework for sanctions implementation.
1.2 It applies to all natural and legal persons under the jurisdiction of Member States.

Article 2: Definitions

For the purposes of this Regulation, the following definitions apply:
(a) 'funds' means financial assets and benefits of any kind;
(b) 'economic resources' means assets of any kind, whether tangible or intangible, movable or immovable.

Article 3: Asset Freezing

3.1 All funds and economic resources belonging to, owned, held or controlled by natural or legal persons, entities or bodies listed in Annex I shall be frozen.
3.2 No funds or economic resources shall be made available, directly or indirectly, to or for the benefit of natural or legal persons, entities or bodies listed in Annex I.

Article 4: Penalties
Member States shall lay down the rules on penalties applicable to infringements of the provisions of this Regulation and shall take all measures necessary to ensure that they are implemented. The penalties provided for must be effective, proportionate and dissuasive.

Article 5: Entry into Force
This Regulation shall enter into force on the day following that of its publication in the Official Journal of the European Union.
This Regulation shall be binding in its entirety and directly applicable in all Member States.

Done at Brussels, 30 July 2023.
"""

# Initialize document processor
processor = LegalDocumentProcessor(
    embedding_model=EMBEDDING_MODEL,
    chroma_path=CHROMA_DIR
)

# Call the chunking function directly
chunks = processor._chunk_text([sample_text], chunk_size=1000, chunk_overlap=200)

# Print the chunks
print(f"\nGenerated {len(chunks)} chunks from the sample text.")
for i, chunk in enumerate(chunks):
    print(f"\nChunk {i+1}:")
    print(f"Length: {len(chunk)}")
    print(f"Preview: {chunk[:100]}...")

print("\nDone.")