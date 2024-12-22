"""
Tests pour le module custom_dataset
"""

import pytest
from unittest.mock import patch, MagicMock
from AuditronAI.core.custom_dataset import CustomDataset

@pytest.fixture
def dataset():
    """Fixture pour le dataset."""
    return CustomDataset("test_dataset")

def test_openai_completion(dataset):
    """Test de la génération avec OpenAI."""
    with patch('openai.ChatCompletion.create') as mock_create:
        mock_create.return_value.choices[0].message.content = "Test response"
        
        response = dataset.generate_completion("test", {
            "file_path": "test.py",
            "code": "print('test')"
        })
        
        assert response == "Test response"
        mock_create.assert_called_once()

def test_google_completion(dataset):
    """Test de la génération avec Google."""
    with patch('google.generativeai.GenerativeModel') as mock_model:
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = "Test response"
        mock_model.return_value = mock_instance
        
        dataset.service = 'google'
        response = dataset.generate_completion("test", {
            "file_path": "test.py",
            "code": "print('test')"
        })
        
        assert response == "Test response"
        mock_instance.generate_content.assert_called_once() 