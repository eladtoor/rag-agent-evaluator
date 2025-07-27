import chromadb

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# List all collections
print("📊 Available Collections:")
collections = client.list_collections()
for collection in collections:
    print(f"- {collection.name}")

if collections:
    # Use the first collection
    collection = collections[0]
    print(f"\n📄 Collection: {collection.name}")
    print(f"Total documents: {collection.count()}")
    
    # Get all documents
    print("\n📄 All Documents:")
    results = collection.get()
    
    for i, (doc_id, doc_text, metadata) in enumerate(zip(results['ids'], results['documents'], results['metadatas'])):
        print(f"\n--- Document {i+1} ---")
        print(f"ID: {doc_id}")
        print(f"Text (first 200 chars): {doc_text[:200]}...")
        print(f"Metadata: {metadata}")
        print("-" * 50)

else:
    print("❌ No collections found!")

print("\n✅ ChromaDB viewer complete!") 