# Data Upload API Documentation

This document provides detailed information about the data upload endpoints in the Edu-Guardian system.

## CSV File Upload

### Endpoint

```
POST /api/students/upload-csv
```

### Description

This endpoint allows users to upload CSV files containing student feedback data. The system processes the file, performs emotion analysis on any comments, and saves the data to the database.

### Request

- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file`: CSV file (required)

### CSV File Format

The CSV file should contain the following columns:

| Column Name | Description | Required |
|-------------|-------------|----------|
| student_id | Unique identifier for the student | Yes |
| timestamp | Date of the feedback (YYYY-MM-DD format) | Yes |
| course_id | Identifier for the course | Yes |
| week_number | Week number in the course | Yes |
| nps_score | Net Promoter Score (0-10) | Yes |
| lms_usability_score | Learning Management System usability rating (1-5) | Yes |
| instructor_quality_score | Instructor quality rating (1-5) | Yes |
| content_difficulty_score | Content difficulty rating (1-5) | Yes |
| support_quality_score | Support quality rating (1-5) | Yes |
| course_pace_score | Course pace rating (1-5) | Yes |
| comments | Student's comments or feedback | No |

### Response

```json
{
  "filename": "example.csv",
  "rows_processed": 10,
  "valid_rows": 9,
  "invalid_rows": 1,
  "quality_metrics": {
    "total_rows": 10,
    "valid_rows": 9,
    "invalid_rows": 1,
    "missing_values_count": 3,
    "completeness_score": 0.97,
    "consistency_score": 0.95,
    "emotion_analysis_coverage": 0.8
  },
  "results": [
    {
      "student_id": "student1",
      "course_id": "course101",
      "week_number": 1,
      "status": "created"
    },
    // Additional results...
  ],
  "errors": [
    {
      "row": 5,
      "error": "Missing required field: course_id"
    }
  ]
}
```

## Batch Directory Processing

### Endpoint

```
POST /api/students/upload-batch
```

### Description

This endpoint processes all CSV files in a specified directory. It's useful for bulk data processing when multiple CSV files need to be imported.

### Request

- **Content-Type**: `application/json`
- **Body**:

```json
{
  "directory_path": "/path/to/csv/files"
}
```

### Response

```json
{
  "files_processed": 3,
  "total_rows": 150,
  "valid_rows": 145,
  "invalid_rows": 5,
  "quality_metrics": {
    "total_rows": 150,
    "valid_rows": 145,
    "invalid_rows": 5,
    "missing_values_count": 12,
    "completeness_score": 0.96,
    "consistency_score": 0.94,
    "emotion_analysis_coverage": 0.85
  },
  "file_results": [
    {
      "filename": "class_a.csv",
      "rows_processed": 50,
      "valid_rows": 48,
      "invalid_rows": 2
    },
    // Additional file results...
  ],
  "errors": [
    {
      "filename": "class_a.csv",
      "row": 10,
      "error": "Invalid value for nps_score: 'excellent'"
    },
    // Additional errors...
  ]
}
```

## Error Handling

### Common Error Responses

- **400 Bad Request**: Invalid file format or missing required fields
- **404 Not Found**: Directory not found (for batch processing)
- **413 Payload Too Large**: File size exceeds the maximum allowed size
- **500 Internal Server Error**: Server-side processing error

## Best Practices

1. **File Size**: Keep CSV files under 10MB for optimal processing speed
2. **Data Validation**: Pre-validate CSV files before uploading to minimize errors
3. **Batch Processing**: For large datasets, split into multiple smaller CSV files and use the batch processing endpoint
4. **Comments Analysis**: Include detailed comments for better emotion analysis results
5. **Error Handling**: Check the response for any errors and fix the data accordingly before re-uploading