import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import tempfile
import csv

# Create test client
client = TestClient(app)

def create_test_csv():
    """Create a temporary CSV file for testing"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    temp_file_path = temp_file.name
    
    # Create test data
    test_data = [
        {
            'student_id': 'test_student_1',
            'timestamp': '2023-01-01',
            'course_id': 'test_course_1',
            'week_number': '1',
            'nps_score': '8',
            'lms_usability_score': '4',
            'instructor_quality_score': '5',
            'content_difficulty_score': '3',
            'support_quality_score': '4',
            'course_pace_score': '3',
            'comments': 'The course is going well, but I find some concepts challenging.'
        },
        {
            'student_id': 'test_student_2',
            'timestamp': '2023-01-01',
            'course_id': 'test_course_1',
            'week_number': '1',
            'nps_score': '7',
            'lms_usability_score': '3',
            'instructor_quality_score': '4',
            'content_difficulty_score': '4',
            'support_quality_score': '3',
            'course_pace_score': '2',
            'comments': 'I am struggling with the pace of the course.'
        }
    ]
    
    # Write to CSV file
    with open(temp_file_path, 'w', newline='') as csvfile:
        fieldnames = test_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in test_data:
            writer.writerow(row)
    
    return temp_file_path

def test_upload_csv_endpoint():
    """Test the CSV upload endpoint"""
    # Create a test CSV file
    csv_file_path = create_test_csv()
    
    try:
        # Open the file for reading
        with open(csv_file_path, 'rb') as f:
            # Send the file to the upload endpoint
            response = client.post(
                "/api/students/upload-csv",
                files={"file": ("test_data.csv", f, "text/csv")}
            )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check that the file was processed correctly
        assert data["filename"] == "test_data.csv"
        assert data["rows_processed"] == 2
        assert data["valid_rows"] == 2
        assert data["invalid_rows"] == 0
        assert len(data["results"]) == 2
        
        # Check that the results contain the expected student IDs
        student_ids = [result["student_id"] for result in data["results"]]
        assert "test_student_1" in student_ids
        assert "test_student_2" in student_ids
        
    finally:
        # Clean up the test file
        if os.path.exists(csv_file_path):
            os.unlink(csv_file_path)

def test_invalid_file_type():
    """Test uploading a non-CSV file"""
    # Create a temporary text file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
    temp_file_path = temp_file.name
    
    try:
        # Write some content to the file
        with open(temp_file_path, 'w') as f:
            f.write("This is not a CSV file")
        
        # Open the file for reading
        with open(temp_file_path, 'rb') as f:
            # Send the file to the upload endpoint
            response = client.post(
                "/api/students/upload-csv",
                files={"file": ("test_data.txt", f, "text/plain")}
            )
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert "Only CSV files are allowed" in data["detail"]
        
    finally:
        # Clean up the test file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)