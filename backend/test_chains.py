import pytest
from unittest.mock import Mock, MagicMock, patch
from chains import Chain, format_docs

class TestFormatDocs:
    
    def test_format_docs_single_document(self):
        doc = Mock()
        doc.page_content = "Test content"
        result = format_docs([doc])
        assert result == "Test content"
    
    def test_format_docs_multiple_documents(self):
        doc1 = Mock()
        doc1.page_content = "First document"
        doc2 = Mock()
        doc2.page_content = "Second document"
        result = format_docs([doc1, doc2])
        assert result == "First document\n\nSecond document"
    
    def test_format_docs_empty_list(self):
        result = format_docs([])
        assert result == ""

class TestChain:
    
    @pytest.fixture
    def mock_retriever(self):
        retriever = Mock()
        retriever.invoke.return_value = []
        return retriever
    
    @pytest.fixture
    def mock_llm(self):
        llm = Mock()
        llm.invoke.return_value = Mock(content="Test response")
        return llm
    
    def test_chain_initialization(self, mock_retriever, mock_llm):
        chain = Chain(mock_retriever, mock_llm)
        assert chain.rag_chain_lcel is not None
    
    @patch('chains.ChatPromptTemplate')
    def test_chain_invoke(self, mock_prompt_template, mock_retriever, mock_llm):
        mock_template = Mock()
        mock_prompt_template.from_template.return_value = mock_template
        
        chain = Chain(mock_retriever, mock_llm)
        result = chain.invoke("What anime should I watch?")
        
        assert result is not None
    
    def test_chain_with_real_query(self, mock_retriever, mock_llm):
        mock_retriever.invoke.return_value = [
            Mock(page_content="Anime data 1"),
            Mock(page_content="Anime data 2")
        ]
        
        chain = Chain(mock_retriever, mock_llm)
        chain.rag_chain_lcel = Mock()
        chain.rag_chain_lcel.invoke.return_value = "Recommended anime list"
        
        result = chain.invoke("action anime")
        assert result == "Recommended anime list"
        chain.rag_chain_lcel.invoke.assert_called_once_with("action anime")

class TestChainErrorHandling:
    
    def test_chain_handles_retriever_error(self):
        retriever = Mock()
        retriever.invoke.side_effect = Exception("Retriever failed")
        llm = Mock()
        
        chain = Chain(retriever, llm)
        chain.rag_chain_lcel = Mock()
        chain.rag_chain_lcel.invoke.side_effect = Exception("Retriever failed")
        
        with pytest.raises(Exception):
            chain.invoke("test query")
    
    def test_chain_handles_empty_query(self, mock_retriever, mock_llm):
        chain = Chain(mock_retriever, mock_llm)
        chain.rag_chain_lcel = Mock()
        chain.rag_chain_lcel.invoke.return_value = ""
        
        result = chain.invoke("")
        assert result == ""