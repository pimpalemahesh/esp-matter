#!/usr/bin/env python3
"""
Integration tests for the data model validator application.
Tests end-to-end workflows including file upload and validation.
"""
import requests
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest

pytest.importorskip("requests", reason="requests not installed")


BASE_URL = "http://localhost:5000"
TEST_TIMEOUT = 30

pytestmark = pytest.mark.integration


class TestServerEndpoints:
    """Test server endpoints"""

    def test_index_page_loads(self):
        """Test that index page loads successfully"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        assert "Device Datamodel Parser & Validator" in response.text

    def test_static_files_accessible(self):
        """Test that static files are accessible"""
        static_files = [
            "/static/css/style.css",
            "/static/js/app.js",
            "/static/js/file-upload.js",
            "/static/js/modal.js",
            "/static/js/pyodide-bridge.js",
            "/static/js/results-renderer.js",
            "/static/js/session-management.js",
            "/static/js/utils.js",
            "/static/js/validation.js",
        ]

        for static_file in static_files:
            response = requests.get(f"{BASE_URL}{static_file}", timeout=10)
            assert response.status_code == 200, f"Failed to load {static_file}"


class TestFileUploadFlow:
    """Test file upload workflow - client-side only"""

    def test_file_upload_form_exists(self):
        """Test that file upload form exists in HTML"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        html = response.text
        assert 'id="uploadForm"' in html
        assert 'id="fileInput"' in html
        assert 'id="uploadArea"' in html

    def test_file_input_accepts_txt_files(self):
        """Test that file input accepts .txt files"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        html = response.text
        assert 'accept=".txt"' in html or 'accept=".txt"' in html.lower()


class TestApplicationStructure:
    """Test application structure and configuration"""

    def test_html_structure(self):
        """Test HTML structure"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        html = response.text

        assert '<div id="uploadSection">' in html
        assert 'id="uploadSuccessSection"' in html
        assert 'id="resultsSection"' in html
        assert 'id="clusterModal"' in html
        assert 'static/js/app.js' in html

    def test_pyodide_configuration(self):
        """Test Pyodide configuration"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        html = response.text

        assert 'pyodide.js' in html or 'pyodide' in html.lower()
        assert 'DMV_PACKAGE_URL' in html or 'DMV_USE_TEST_PYPI' in html


class TestErrorHandling:
    """Test error handling UI elements"""

    def test_error_message_element_exists(self):
        """Test that error message element exists in HTML"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        html = response.text
        assert 'id="errorMessage"' in html
        assert 'class="error-message"' in html

    def test_validation_message_element_exists(self):
        """Test that validation message element exists"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200
        html = response.text
        assert 'id="validateMessage"' in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
