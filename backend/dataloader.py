from langchain_community.document_loaders import DirectoryLoader, CSVLoader

class Dataloader:
    def __init__(self, folder_path: str = "data"):
        self.loader = DirectoryLoader(folder_path, glob="*.csv", loader_cls=CSVLoader)
        self.documents = self.loader.load()

    def info(self):
        print(f"Loaded {len(self.documents)} documents")
        print(f"\nFirst document preview:")
        print(self.documents[0].page_content[:200] + "...")
        print(self.documents[-1].page_content[:200] + "...")
