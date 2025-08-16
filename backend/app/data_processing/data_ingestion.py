
"""Data Ingestion module for the application.

This module provides functionality related to data ingestion.
"""
from typing import List, Dict, Any, Optional, Tuple
import csv
import json
import os
import io
from datetime import datetime
from pydantic import BaseModel, ValidationError, field_validator, Field
from pathlib import Path

import pandas as pd
import numpy as np
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.document_loaders.csv_loader import CSVLoader

from ..emotion_analysis.analyzer import AdvancedEmotionAnalyzer, EmotionProfile
from ..models.student_journey import StudentJourneyCreate
from ..database.db import get_db
class CSVDataRow(BaseModel):
    """Model for validating a row of CSV data"""
    student_id: str
    timestamp: datetime
    course_id: str
    week_number: int
    nps_score: int = Field(ge=0, le=10)

    # Aspect scores (1-5 scale)
    lms_usability_score: int = Field(ge=1, le=5)
    instructor_quality_score: int = Field(ge=1, le=5)
    content_difficulty_score: int = Field(ge=1, le=5)
    support_quality_score: int = Field(ge=1, le=5)
    course_pace_score: int = Field(ge=1, le=5)

    comments: Optional[str] = None

    # Optional emotion fields that might be in the CSV
    frustration_level: Optional[float] = Field(None, ge=0, le=1)
    frustration_type: Optional[str] = None
    urgency_level: Optional[str] = None
    emotional_temperature: Optional[float] = Field(None, ge=0, le=1)
    hidden_dissatisfaction_flag: Optional[bool] = None
    hidden_dissatisfaction_confidence: Optional[float] = Field(None, ge=0, le=1)

    # Optional demographic and outcome fields
    demographic_type: Optional[str] = None
    current_grade: Optional[float] = None
    attendance_rate: Optional[float] = Field(None, ge=0, le=1)
    completion_status: Optional[str] = None
    job_placement: Optional[str] = None

    @field_validator('timestamp', mode='before')
    def parse_timestamp(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                try:
                    return datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    raise ValueError(f"Cannot parse timestamp: {v}")
        return v

class DataQualityMetrics(BaseModel):
    """Model for data quality assessment metrics"""
    total_rows: int
    valid_rows: int
    invalid_rows: int
    missing_values_count: Dict[str, int]
    validation_errors: List[str]
    completeness_score: float  # Percentage of non-null values
    consistency_score: float   # Measure of data consistency
    emotion_analysis_coverage: float  # Percentage of rows with emotion analysis

class CSVDataImporter:
    """Class for importing and processing CSV data with emotion field mapping"""

    def __init__(self, emotion_analyzer: AdvancedEmotionAnalyzer = None):
        self.emotion_analyzer = emotion_analyzer or AdvancedEmotionAnalyzer()
        self.validation_errors = []
        self.processed_rows = 0
        self.valid_rows = 0
        self.invalid_rows = 0
        self.missing_values = {}
        
    def import_csv(self, file_path: str) -> Tuple[List[StudentJourneyCreate], DataQualityMetrics]:
        """Import data from a CSV file and map to StudentJourneyCreate objects"""
        data_importer = DataImporter(self.emotion_analyzer)
        return data_importer.import_data(file_path)

class BatchProcessor:
    """Class for batch processing of student data"""
    
    def __init__(self, emotion_analyzer: AdvancedEmotionAnalyzer = None):
        self.emotion_analyzer = emotion_analyzer or AdvancedEmotionAnalyzer()
        self.csv_importer = CSVDataImporter(self.emotion_analyzer)
    
    def process_batch(self, file_path: str) -> Tuple[List[StudentJourneyCreate], DataQualityMetrics]:
        """Process a batch of student data from a file"""
        return self.csv_importer.import_csv(file_path)

class RealTimeProcessor:
    """Class for real-time processing of student data"""
    
    def __init__(self, emotion_analyzer: AdvancedEmotionAnalyzer = None):
        self.emotion_analyzer = emotion_analyzer or AdvancedEmotionAnalyzer()
    
    def process_entry(self, data: Dict[str, Any]) -> StudentJourneyCreate:
        """Process a single student data entry in real-time"""
        try:
            # Clean and validate data
            cleaned_data = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}
            cleaned_data = {k: None if v == '' else v for k, v in cleaned_data.items()}
            
            # Validate data
            validated_data = CSVDataRow(**cleaned_data)
            
            # Map to student journey
            data_importer = DataImporter(self.emotion_analyzer)
            return data_importer._map_to_student_journey(validated_data)
        except Exception as e:
            raise ValueError(f"Error processing entry: {str(e)}")

class DataQualityAssessor:
    """Class for assessing data quality"""
    
    def assess_quality(self, file_path: str) -> DataQualityMetrics:
        """Assess the quality of data in a file"""
        importer = DataImporter()
        _, quality_metrics = importer.import_data(file_path)
        return quality_metrics

class DataImporter:
    """Class for importing and processing CSV data with emotion field mapping"""

    def __init__(self, emotion_analyzer: AdvancedEmotionAnalyzer = None):
        self.emotion_analyzer = emotion_analyzer or AdvancedEmotionAnalyzer()
        self.validation_errors = []
        self.processed_rows = 0
        self.valid_rows = 0
        self.invalid_rows = 0
        self.missing_values = {}

    def import_data(self, file_path: str) -> Tuple[List[StudentJourneyCreate], DataQualityMetrics]:
        """Import data from a file (CSV or Excel) and map to StudentJourneyCreate objects"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Reset counters for the new file
        self._reset_counters()

        # Load data using the appropriate langchain loader
        raw_data = self._load_data(file_path)
        self.processed_rows = len(raw_data)

        # Process data using the existing logic
        student_journeys, quality_metrics = self._process_data(raw_data)
        return student_journeys, quality_metrics

    def _reset_counters(self):
        """Resets the counters for a new import operation."""
        self.validation_errors = []
        self.processed_rows = 0
        self.valid_rows = 0
        self.invalid_rows = 0
        self.missing_values = {}

    def _load_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Loads data from a file using the appropriate langchain loader."""
        file_ext = Path(file_path).suffix.lower()
        if file_ext == '.csv':
            return self._load_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return self._load_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    def _load_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Loads data from a CSV file."""
        loader = CSVLoader(file_path=file_path, encoding="utf-8")
        docs = loader.load()
        # Each doc represents a row. The page_content needs to be parsed into a dict.
        # A more direct way is to just read the csv into dicts.
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _load_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """Loads data from an Excel file, extracting tables."""
        loader = UnstructuredExcelLoader(file_path, mode="elements")
        docs = loader.load()

        all_rows = []
        for doc in docs:
            if doc.metadata.get("category") == "Table":
                # The table data is in an HTML table in the metadata
                html_table = doc.metadata.get("text_as_html")
                if html_table:
                    # Use pandas to parse the HTML table
                    df = pd.read_html(io.StringIO(html_table))[0]
                    all_rows.extend(df.to_dict('records'))
        return all_rows

    def _process_data(
        self, raw_data: List[Dict[str, Any]]) -> Tuple[List[StudentJourneyCreate], DataQualityMetrics]:
        """Process raw data and convert to StudentJourneyCreate objects"""
        student_journeys = []

        # Clean and validate each row
        for row in raw_data:
            try:
                # Clean row data (strip whitespace, handle empty strings)
                cleaned_row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
                cleaned_row = {k: None if v == '' else v for k, v in cleaned_row.items()}

                # Count missing values
                for key, value in cleaned_row.items():
                    if value is None or value == '':
                        self.missing_values[key] = self.missing_values.get(key, 0) + 1

                # Validate row data
                validated_row = CSVDataRow(**cleaned_row)

                # Perform emotion analysis if needed
                journey = self._map_to_student_journey(validated_row)
                student_journeys.append(journey)
                self.valid_rows += 1

            except ValidationError as e:
                self.validation_errors.append(f"Row {self.processed_rows}: {str(e)}")
                self.invalid_rows += 1
                continue
            except Exception as e:
                self.validation_errors.append(
                    f"Row {self.processed_rows}: Unexpected error: {str(e)}")
                self.invalid_rows += 1
                continue

        # Calculate data quality metrics
        quality_metrics = self._calculate_quality_metrics()

        return student_journeys, quality_metrics

    def _map_to_student_journey(self, row: CSVDataRow) -> StudentJourneyCreate:
        """Map validated CSV row to StudentJourneyCreate object with emotion analysis"""
        # Perform emotion analysis on comments if needed
        emotion_data = {}
        if row.comments and not all([
            row.frustration_level is not None,
            row.frustration_type is not None,
            row.urgency_level is not None,
            row.emotional_temperature is not None,
            row.hidden_dissatisfaction_flag is not None
        ]):
            # Analyze emotions from comments
            emotion_profile = self.emotion_analyzer.analyze_text(row.comments)
            emotion_data = emotion_profile.dict()

        # Create StudentJourneyCreate object
        journey_data = row.dict()
        journey_data.update(emotion_data)

        return StudentJourneyCreate(**journey_data)

    def _calculate_quality_metrics(self) -> DataQualityMetrics:
        """Calculate data quality metrics"""
        total_fields = self.processed_rows * len(CSVDataRow.__annotations__)
        missing_count = sum(self.missing_values.values())
        completeness = 1.0 - (missing_count / total_fields) if total_fields > 0 else 0.0

        # Simple consistency score based on validation success rate
        consistency = self.valid_rows / self.processed_rows if self.processed_rows > 0 else 0.0

        # Calculate emotion analysis coverage
        emotion_coverage = 0.0  # This would be calculated based on how many rows had emotion analysis performed

        return DataQualityMetrics(
            total_rows=self.processed_rows,
            valid_rows=self.valid_rows,
            invalid_rows=self.invalid_rows,
            missing_values_count=self.missing_values,
            validation_errors=self.validation_errors,
            completeness_score=completeness,
            consistency_score=consistency,
            emotion_analysis_coverage=emotion_coverage
        )

class BatchProcessor:
    """Class for batch processing of historical data"""

    def __init__(self, importer: DataImporter, db=None):
        self.importer = importer
        self.db = db

    async def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """Process all CSV files in a directory"""
        directory = Path(directory_path)
        if not directory.exists() or not directory.is_dir():
            raise ValueError(f"Invalid directory path: {directory_path}")

        results = {
            "files_processed": 0,
            "total_rows": 0,
            "valid_rows": 0,
            "invalid_rows": 0,
            "quality_metrics": [],
            "errors": []
        }

        # Process each data file in the directory
        for file_path in list(directory.glob("*.csv")) + list(directory.glob("*.xlsx")):
            try:
                student_journeys, quality_metrics = self.importer.import_data(str(file_path))

                # Save to database if db session is provided
                if self.db:
                    await self._save_to_database(student_journeys)

                # Update results
                results["files_processed"] += 1
                results["total_rows"] += quality_metrics.total_rows
                results["valid_rows"] += quality_metrics.valid_rows
                results["invalid_rows"] += quality_metrics.invalid_rows
                results["quality_metrics"].append({
                    "file": file_path.name,
                    "metrics": quality_metrics.dict()
                })

            except Exception as e:
                results["errors"].append(f"Error processing {file_path.name}: {str(e)}")

        return results

    async def _save_to_database(self, student_journeys: List[StudentJourneyCreate]):
        """Save processed student journeys to database"""
        from ..models.student_journey import StudentJourney
        import uuid

        results = []
        for journey in student_journeys:
            try:
                # Check if there's already an entry for this student, course, and week
                existing_entry = self.db.query(StudentJourney).filter(
                    StudentJourney.student_id == journey.student_id,
                    StudentJourney.course_id == journey.course_id,
                    StudentJourney.week_number == journey.week_number
                ).first()

                if existing_entry:
                    # Update existing entry
                    for key, value in journey.model_dump(exclude_unset=True).items():
                        if hasattr(existing_entry, key):
                            setattr(existing_entry, key, value)

                    results.append({
                        "student_id": journey.student_id,
                        "course_id": journey.course_id,
                        "week_number": journey.week_number,
                        "status": "updated"
                    })
                else:
                    # Create new entry
                    new_journey = StudentJourney(
                        id=uuid.uuid4(),
                        **journey.model_dump()
                    )

                    self.db.add(new_journey)
                    results.append({
                        "student_id": journey.student_id,
                        "course_id": journey.course_id,
                        "week_number": journey.week_number,
                        "status": "created"
                    })
            except Exception as e:
                results.append({
                    "student_id": journey.student_id if hasattr(
                        journey, "student_id") else "unknown",
                    "course_id": journey.course_id if hasattr(journey, "course_id") else "unknown",
                    "week_number": journey.week_number if hasattr(
                        journey, "week_number") else "unknown",
                    "status": "error",
                    "error": str(e)
                })

        self.db.commit()
        return results

class RealTimeProcessor:
    """Class for real-time processing of new feedback data"""

    def __init__(self, emotion_analyzer: AdvancedEmotionAnalyzer = None, db=None):
        self.emotion_analyzer = emotion_analyzer or AdvancedEmotionAnalyzer()
        self.db = db

    async def process_feedback(self, feedback_data: Dict[str, Any]) -> StudentJourneyCreate:
        """Process a single feedback entry in real-time"""
        try:
            # Validate the feedback data
            validated_data = CSVDataRow(**feedback_data)

            # Perform emotion analysis if comments are provided
            if validated_data.comments:
                emotion_profile = self.emotion_analyzer.analyze_text(validated_data.comments)
                emotion_data = emotion_profile.dict()

                # Update feedback data with emotion analysis
                journey_data = validated_data.dict()
                journey_data.update(emotion_data)

                # Create StudentJourneyCreate object
                student_journey = StudentJourneyCreate(**journey_data)

                # Save to database if db session is provided
                if self.db:
                    await self._save_to_database(student_journey)

                return student_journey
            else:
                # If no comments, just create the journey with the provided data
                return StudentJourneyCreate(**validated_data.dict())

        except ValidationError as e:
            raise ValueError(f"Invalid feedback data: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing feedback: {str(e)}")

    async def _save_to_database(self, student_journey: StudentJourneyCreate):
        """Save processed student journey to database"""
        from ..models.student_journey import StudentJourney
        import uuid

        try:
            # Check if there's already an entry for this student, course, and week
            existing_entry = self.db.query(StudentJourney).filter(
                StudentJourney.student_id == student_journey.student_id,
                StudentJourney.course_id == student_journey.course_id,
                StudentJourney.week_number == student_journey.week_number
            ).first()

            if existing_entry:
                # Update existing entry
                for key, value in student_journey.model_dump(exclude_unset=True).items():
                    if hasattr(existing_entry, key):
                        setattr(existing_entry, key, value)

                self.db.commit()
                self.db.refresh(existing_entry)
                return existing_entry
            else:
                # Create new entry
                new_journey = StudentJourney(
                    id=uuid.uuid4(),
                    **student_journey.model_dump()
                )

                self.db.add(new_journey)
                self.db.commit()
                self.db.refresh(new_journey)
                return new_journey

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error saving to database: {str(e)}")

class DataQualityAssessor:
    """Class for assessing data quality and generating metrics"""

    def assess_dataset(self, data: pd.DataFrame) -> DataQualityMetrics:
        """Assess the quality of a dataset"""
        total_rows = len(data)
        total_fields = total_rows * len(data.columns)

        # Count missing values
        missing_values = data.isnull().sum().to_dict()
        missing_count = sum(missing_values.values())

        # Calculate completeness score
        completeness = 1.0 - (missing_count / total_fields) if total_fields > 0 else 0.0

        # Check for validation errors (this would be more complex in a real implementation)
        validation_errors = []
        valid_rows = total_rows  # Assume all rows are valid initially

        # Calculate consistency score (simplified version)
        consistency = valid_rows / total_rows if total_rows > 0 else 0.0

        # Calculate emotion analysis coverage
        emotion_fields = ['frustration_level', 'frustration_type', 'urgency_level',
                         'emotional_temperature', 'hidden_dissatisfaction_flag']
        emotion_coverage = data[emotion_fields].notnull().all(axis=1).mean()

        return DataQualityMetrics(
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=total_rows - valid_rows,
            missing_values_count=missing_values,
            validation_errors=validation_errors,
            completeness_score=completeness,
            consistency_score=consistency,
            emotion_analysis_coverage=emotion_coverage
        )
