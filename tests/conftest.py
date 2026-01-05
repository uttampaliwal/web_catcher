import pytest
import os
import sys

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture
def sample_web_content():
    return """
    <html>
        <body>
            <h1>Test Title</h1>
            <p>This is a test paragraph.</p>
            <p>Another paragraph.</p>
        </body>
    </html>
    """

@pytest.fixture
def mock_trafilatura(mocker):
    return mocker.patch("trafilatura.fetch_url")

@pytest.fixture
def mock_trafilatura_extract(mocker):
    return mocker.patch("trafilatura.extract")
