from pathlib import Path

from sentence_transformers import SentenceTransformer
import faiss


BASE_DIR = Path(__file__).resolve().parent

POLICY_FILE = BASE_DIR / "policies" / "classroom_rules.txt"


# Load policy document
with open(POLICY_FILE, "r", encoding="utf-8") as file:
    policy_text = file.read()


# Split rules
rules = [
    rule.strip()
    for rule in policy_text.split("\n\n")
    if rule.strip()
]


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Convert rules into embeddings
embeddings = model.encode(rules)


# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)


def search_policies(query, top_k=3):

    query_embedding = model.encode([query])

    distances, indices = index.search(
        query_embedding,
        min(top_k, len(rules))
    )

    results = []

    for position in indices[0]:

        results.append(rules[position])

    return results


if __name__ == "__main__":

    query = "Can more than 20 students request a classroom?"

    results = search_policies(query)

    print("\nRelevant Policies:\n")

    for result in results:
        print(result)
        print()