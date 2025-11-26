import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from backend import app, initialize_rag, rag_chain

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_rag_chain():
    mock_chain = Mock()
    mock_chain.invoke.return_value = "This is a test response for anime recommendations"
    mock_chain.rag_chain_lcel.stream.return_value = iter(["This ", "is ", "streaming ", "response"])
    return mock_chain

class TestBackendEndpoints:
    
    def test_initialize_endpoint_success(self, client):
        with patch('backend.initialize_rag', return_value=True):
            response = client.post('/initialize', 
                                  json={'k_docs': 5})
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
    
    def test_initialize_endpoint_with_all_params(self, client):
        with patch('backend.initialize_rag', return_value=True):
            config = {
                'data_dir': './test_data',
                'db_dir': './test_db',
                'embedding_model': 'test-model',
                'llm_model': 'test-llm',
                'k_docs': 10
            }
            response = client.post('/initialize', json=config)
            assert response.status_code == 200
    
    def test_initialize_endpoint_error(self, client):
        with patch('backend.initialize_rag', side_effect=Exception("Init failed")):
            response = client.post('/initialize', json={})
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'
    
    @patch('backend.rag_chain')
    def test_query_endpoint_success(self, mock_chain, client):
        mock_chain.invoke.return_value = "Test anime recommendation"
        response = client.post('/anime', 
                              json={'input_': 'recommend action anime'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'response' in data
    
    def test_query_endpoint_empty_input(self, client):
        response = client.post('/anime', json={'input_': ''})
        assert response.status_code == 200
    
    @patch('backend.rag_chain', None)
    @patch('backend.initialize_rag')
    def test_query_endpoint_initializes_if_needed(self, mock_init, client):
        with patch('backend.rag_chain') as mock_chain:
            mock_chain.invoke.return_value = "Response after init"
            response = client.post('/anime', 
                                  json={'input_': 'test query'})
            assert response.status_code == 200
    
    def test_query_endpoint_missing_input_field(self, client):
        response = client.post('/anime', json={})
        assert response.status_code == 500
    
    @patch('backend.rag_chain')
    def test_streaming_endpoint_success(self, mock_chain, client):
        mock_chain.rag_chain_lcel.stream.return_value = iter(["Test ", "stream"])
        response = client.post('/anime/stream',
                              json={'input_': 'test query'})
        assert response.status_code == 200
        assert response.mimetype == 'text/event-stream'
    
    def test_streaming_endpoint_empty_input(self, client):
        response = client.post('/anime/stream', json={'input_': ''})
        assert response.status_code == 200

class TestRAGComponents:
    
    @patch('backend.Dataloader')
    @patch('backend.Splitter')
    @patch('backend.Embed')
    @patch('backend.VectorStore')
    @patch('backend.LLM')
    @patch('backend.Chain')
    def test_initialize_rag_components(self, mock_chain, mock_llm, mock_vector,
                                      mock_embed, mock_splitter, mock_dataloader):
        mock_dataloader.return_value.documents = ['doc1', 'doc2']
        mock_splitter.return_value.chunks = ['chunk1', 'chunk2']
        mock_embed.return_value.embed = Mock()
        mock_vector.return_value.vectorstore.as_retriever = Mock()
        mock_llm.return_value.llm = Mock()
        
        result = initialize_rag()
        assert result == True
        mock_dataloader.assert_called_once()
        mock_splitter.assert_called_once()

class TestErrorHandling:
    
    @patch('backend.rag_chain')
    def test_query_endpoint_handles_exception(self, mock_chain, client):
        mock_chain.invoke.side_effect = Exception("RAG failed")
        response = client.post('/anime',
                              json={'input_': 'test query'})
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'RAG failed' in data['message']
    
    @patch('backend.rag_chain')
    def test_streaming_endpoint_handles_exception(self, mock_chain, client):
        mock_chain.rag_chain_lcel.stream.side_effect = Exception("Stream failed")
        response = client.post('/anime/stream',
                              json={'input_': 'test query'})
        assert response.status_code == 500

class TestIntegration:
    
    @patch('backend.initialize_rag')
    def test_full_flow(self, mock_init, client):
        mock_init.return_value = True
        
        with patch('backend.rag_chain') as mock_chain:
            mock_chain.invoke.return_value = "Anime recommendation"
            
            init_response = client.post('/initialize', json={'k_docs': 3})
            assert init_response.status_code == 200
            
            query_response = client.post('/anime',
                                        json={'input_': 'action anime'})
            assert query_response.status_code == 200
            data = json.loads(query_response.data)
            assert data['response'] == "Anime recommendation"