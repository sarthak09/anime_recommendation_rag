import pytest
from unittest.mock import Mock, patch, MagicMock
import os

class TestDataloader:
    
    @patch('dataloader.DirectoryLoader')
    def test_dataloader_initialization(self, mock_loader):
        from dataloader import Dataloader
        
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = ['doc1', 'doc2']
        mock_loader.return_value = mock_loader_instance
        
        loader = Dataloader("./test_data")
        assert loader.documents == ['doc1', 'doc2']
        mock_loader.assert_called_once_with("./test_data", glob="*.csv", loader_cls=Mock)
    
    @patch('dataloader.DirectoryLoader')
    def test_dataloader_info(self, mock_loader):
        from dataloader import Dataloader
        
        mock_doc = Mock()
        mock_doc.page_content = "Test content that is long enough for preview"
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [mock_doc, mock_doc]
        mock_loader.return_value = mock_loader_instance
        
        loader = Dataloader("./test_data")
        loader.info()
        assert len(loader.documents) == 2

class TestSplitter:
    
    def test_splitter_initialization(self):
        from split import Splitter
        
        mock_doc = Mock()
        mock_doc.page_content = "Test content"
        documents = [mock_doc]
        
        splitter = Splitter(documents, chunk_size=100, chunk_overlap=10)
        assert splitter.text_splitter is not None
        assert splitter.chunks is not None
    
    @patch('split.RecursiveCharacterTextSplitter')
    def test_splitter_custom_params(self, mock_text_splitter):
        from split import Splitter
        
        mock_splitter_instance = Mock()
        mock_splitter_instance.split_documents.return_value = ['chunk1', 'chunk2']
        mock_text_splitter.return_value = mock_splitter_instance
        
        documents = [Mock()]
        splitter = Splitter(documents, chunk_size=1000, chunk_overlap=100)
        
        mock_text_splitter.assert_called_once_with(
            chunk_size=1000,
            chunk_overlap=100
        )
        assert splitter.chunks == ['chunk1', 'chunk2']

class TestEmbedding:
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_key'})
    @patch('embedding.HuggingFaceBgeEmbeddings')
    def test_embed_initialization(self, mock_embeddings):
        from embedding import Embed
        
        embedder = Embed("test-model")
        mock_embeddings.assert_called_once_with(
            model_name="test-model",
            model_kwargs={"device": "cpu"}
        )
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_key'})
    @patch('embedding.HuggingFaceBgeEmbeddings')
    def test_embed_test_embedding(self, mock_embeddings):
        from embedding import Embed
        
        mock_embed_instance = Mock()
        mock_embed_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_embeddings.return_value = mock_embed_instance
        
        embedder = Embed()
        embedder.test_embedding("test text")
        mock_embed_instance.embed_query.assert_called_once_with("test text")

class TestVectorStore:
    
    @patch('vectorestor.Chroma')
    def test_vectorstore_initialization(self, mock_chroma):
        from vectorestor import VectorStore
        
        chunks = ['chunk1', 'chunk2']
        embedding = Mock()
        
        VectorStore(chunks, embedding, "./test_db")
        mock_chroma.from_documents.assert_called_once_with(
            documents=chunks,
            embedding=embedding,
            persist_directory="./test_db",
            collection_name="rag_collection"
        )
    
    @patch('vectorestor.Chroma')
    def test_vectorstore_info(self, mock_chroma):
        from vectorestor import VectorStore
        
        mock_collection = Mock()
        mock_collection.count.return_value = 100
        mock_vectorstore_instance = Mock()
        mock_vectorstore_instance._collection = mock_collection
        mock_chroma.from_documents.return_value = mock_vectorstore_instance
        
        store = VectorStore(['chunk'], Mock())
        store.info()
        assert store.vectorstore._collection.count() == 100

class TestLLM:
    
    @patch.dict(os.environ, {
        'GROQ_API_KEY': 'test_groq_key',
        'HUGGINGFACEHUB_API_TOKEN': 'test_hf_token'
    })
    @patch('llm.init_chat_model')
    def test_llm_initialization(self, mock_init_chat):
        from llm import LLM
        
        llm = LLM("test-model")
        mock_init_chat.assert_called_once_with(model="test-model")
    
    @patch.dict(os.environ, {
        'GROQ_API_KEY': 'test_groq_key',
        'HUGGINGFACEHUB_API_TOKEN': 'test_hf_token'
    })
    @patch('llm.init_chat_model')
    def test_llm_test_method(self, mock_init_chat):
        from llm import LLM
        
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = mock_response
        mock_init_chat.return_value = mock_llm_instance
        
        llm = LLM("test-model")
        llm.llmtest("Test prompt")
        mock_llm_instance.invoke.assert_called_once_with("Test prompt")