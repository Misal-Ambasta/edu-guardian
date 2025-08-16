import json
"""
Utility functions for common operations.
"""


async def process_interventions_from_patterns(similar_patterns):
    """process_interventions_from_patterns extracts common functionality."""

            for pattern in similar_patterns:
                metadata = pattern.get("metadata", {})
                if "successful_interventions" in metadata:
                    interventions = metadata["successful_interventions"]
                    if isinstance(interventions, str):
                        try:
                            interventions = json.loads(interventions)
                        except json.JSONDecodeError:
                            interventions = []

                    for intervention in interventions:
                        # Add similarity score to intervention
                        intervention["similarity_score"] = pattern.get("similarity_score", 0.0)
