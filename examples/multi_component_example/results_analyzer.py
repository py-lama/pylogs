#!/usr/bin/env python3
"""
Results Analyzer Script

This script demonstrates how to use LogLama for logging in a results analysis script.
It loads inference results, analyzes them, and generates a final report.
"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime

# Add the PyLama root directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Import LogLama modules
from loglama.core.logger import get_logger, setup_logging
from loglama.core.env_manager import load_central_env

# Load environment variables from the central .env file
load_central_env()

# Set up logging
setup_logging()

# Get a logger for this script
logger = get_logger("results_analyzer")


def find_latest_inference_file():
    """Find the most recent inference results file in the data directory."""
    data_dir = Path(__file__).parent / "data"
    data_files = list(data_dir.glob("inference_results_*.json"))
    
    if not data_files:
        logger.error("No inference results files found")
        return None
    
    # Sort by modification time (most recent first)
    latest_file = max(data_files, key=lambda f: f.stat().st_mtime)
    logger.info(f"Found latest inference results file: {latest_file.name}")
    return latest_file


def load_inference_results(file_path):
    """Load inference results from a JSON file."""
    logger.info(f"Loading inference results from {file_path.name}")
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        logger.info(f"Successfully loaded inference results from {file_path.name}")
        return data
    except Exception as e:
        logger.exception(f"Error loading inference results from {file_path.name}")
        return {}


def analyze_results(inference_results):
    """Analyze the inference results and generate insights."""
    if not inference_results:
        logger.warning("No inference results to analyze")
        return {}
    
    logger.info("Analyzing inference results")
    
    try:
        with logger.time("results_analysis"):
            # Extract relevant data from inference results
            sources = [s for s in inference_results.keys() if s != "summary"]
            
            # Calculate overall statistics
            all_predictions = []
            all_confidences = []
            source_summaries = {}
            
            for source in sources:
                source_predictions = []
                source_confidences = []
                
                for category, results in inference_results[source].items():
                    prediction = results.get("prediction", 0)
                    confidence = results.get("confidence", 0)
                    
                    all_predictions.append(prediction)
                    all_confidences.append(confidence)
                    source_predictions.append(prediction)
                    source_confidences.append(confidence)
                
                # Calculate source-level statistics
                if source_predictions:
                    source_summaries[source] = {
                        "avg_prediction": sum(source_predictions) / len(source_predictions),
                        "avg_confidence": sum(source_confidences) / len(source_confidences),
                        "max_prediction": max(source_predictions),
                        "min_prediction": min(source_predictions),
                        "prediction_count": len(source_predictions)
                    }
            
            # Calculate overall statistics
            overall_stats = {}
            if all_predictions:
                overall_stats = {
                    "avg_prediction": sum(all_predictions) / len(all_predictions),
                    "avg_confidence": sum(all_confidences) / len(all_confidences),
                    "max_prediction": max(all_predictions),
                    "min_prediction": min(all_predictions),
                    "total_predictions": len(all_predictions),
                    "sources_analyzed": len(sources)
                }
            
            # Generate insights based on the analysis
            insights = []
            if overall_stats:
                insights.append(f"Analyzed {overall_stats['total_predictions']} predictions from {overall_stats['sources_analyzed']} sources.")
                insights.append(f"Average prediction value: {overall_stats['avg_prediction']:.2f} with confidence {overall_stats['avg_confidence']:.2f}.")
                
                # Find the source with highest average prediction
                if source_summaries:
                    best_source = max(source_summaries.items(), key=lambda x: x[1]['avg_prediction'])
                    insights.append(f"Source '{best_source[0]}' has the highest average prediction value of {best_source[1]['avg_prediction']:.2f}.")
            
            # Include the original summary if available
            if "summary" in inference_results:
                insights.append(f"Model summary: {inference_results['summary']}")
            
            analysis_results = {
                "overall_stats": overall_stats,
                "source_summaries": source_summaries,
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            }
            
        logger.info("Results analysis completed", extra={"insights_count": len(insights)})
        return analysis_results
    except Exception as e:
        logger.exception("Error during results analysis")
        return {}


def generate_report(analysis_results):
    """Generate a human-readable report from the analysis results."""
    if not analysis_results:
        logger.warning("No analysis results for report generation")
        return ""
    
    logger.info("Generating final report")
    
    try:
        # Format the report as a string
        report = ["# Analysis Report", ""]
        report.append(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Add insights
        report.append("## Key Insights")
        insights = analysis_results.get("insights", [])
        if insights:
            for insight in insights:
                report.append(f"- {insight}")
        else:
            report.append("*No insights available*")
        report.append("")
        
        # Add overall statistics
        report.append("## Overall Statistics")
        overall_stats = analysis_results.get("overall_stats", {})
        if overall_stats:
            for key, value in overall_stats.items():
                formatted_value = f"{value:.2f}" if isinstance(value, float) else value
                report.append(f"- **{key.replace('_', ' ').title()}:** {formatted_value}")
        else:
            report.append("*No overall statistics available*")
        report.append("")
        
        # Add source summaries
        report.append("## Source Summaries")
        source_summaries = analysis_results.get("source_summaries", {})
        if source_summaries:
            for source, summary in source_summaries.items():
                report.append(f"### {source.title()}")
                for key, value in summary.items():
                    formatted_value = f"{value:.2f}" if isinstance(value, float) else value
                    report.append(f"- **{key.replace('_', ' ').title()}:** {formatted_value}")
                report.append("")
        else:
            report.append("*No source summaries available*")
        
        logger.info("Report generation completed")
        return "\n".join(report)
    except Exception as e:
        logger.exception("Error during report generation")
        return ""


def save_report(report, filename):
    """Save the generated report to a file."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    file_path = output_dir / filename
    
    logger.info(f"Saving report to {filename}", extra={"file_path": str(file_path)})
    
    try:
        with open(file_path, "w") as f:
            f.write(report)
        logger.info(f"Report successfully saved to {filename}")
        return True
    except Exception as e:
        logger.exception(f"Error saving report to {filename}")
        return False


def save_analysis_results(results, filename):
    """Save analysis results to a JSON file."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    file_path = output_dir / filename
    
    logger.info(f"Saving analysis results to {filename}", extra={"file_path": str(file_path)})
    
    try:
        with open(file_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Analysis results successfully saved to {filename}")
        return True
    except Exception as e:
        logger.exception(f"Error saving analysis results to {filename}")
        return False


def main():
    """Main function that analyzes inference results and generates a report."""
    logger.info("Starting results analysis")
    
    # Find the latest inference results file
    latest_file = find_latest_inference_file()
    if not latest_file:
        logger.error("Results analysis failed: No inference results file found")
        return False
    
    # Load the inference results
    inference_results = load_inference_results(latest_file)
    if not inference_results:
        logger.error("Results analysis failed: Could not load inference results")
        return False
    
    # Analyze the results
    analysis_results = analyze_results(inference_results)
    if not analysis_results:
        logger.error("Results analysis failed: Analysis error")
        return False
    
    # Save the analysis results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_filename = f"analysis_results_{timestamp}.json"
    save_success = save_analysis_results(analysis_results, json_filename)
    
    if not save_success:
        logger.error("Results analysis failed: Could not save analysis results")
        return False
    
    # Generate and save the report
    report = generate_report(analysis_results)
    if not report:
        logger.error("Results analysis failed: Could not generate report")
        return False
    
    report_filename = f"analysis_report_{timestamp}.md"
    report_success = save_report(report, report_filename)
    
    if report_success:
        logger.info("Results analysis completed successfully")
        return True
    else:
        logger.error("Results analysis failed: Could not save report")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
