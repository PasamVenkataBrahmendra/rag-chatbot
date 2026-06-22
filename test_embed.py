from sentence_transformers import SentenceTransformer

print("Step 1")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Step 2")

embedding = model.encode(["hello"])

print("Step 3")
print(embedding.shape)