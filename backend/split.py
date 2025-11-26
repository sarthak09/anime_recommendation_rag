from langchain_text_splitters import RecursiveCharacterTextSplitter

class Splitter:
    def __init__(self, documents, chunk_size: int = 500, chunk_overlap: int = 50):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.chunks = self.text_splitter.split_documents(documents)

    def info(self):
        print(f"Created {len(self.chunks)} chunks")
        print(f"\nFirst chunk preview:")
        print(self.chunks[0].page_content[:200] + "...")
        print(self.chunks[-1].page_content[:200] + "...")



# splitter=Splitter(dataloader.documents)

# print(f"Created {len(splitter.chunks)} chunks from {len(dataloader.documents)} documents")
# print(f"\nChunk example:")
# print(f"Content: {splitter.chunks[0].page_content[:150]}...")
# print(f"Metadata: {splitter.chunks[0].metadata}")