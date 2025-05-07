#!/usr/bin/env python
"""
Script to generate a summary report of the test results.
"""

import os
import sys
import json
import datetime
import argparse
from collections import Counter

def load_test_results(file_path):
    """Load the test results from a file."""
    with open(file_path, "r") as f:
        return json.load(f)

def generate_summary(test_results):
    """Generate a summary of the test results."""
    # Count the test results
    status_counts = Counter(test["status"] for test in test_results["tests"])
    
    # Calculate the total number of tests
    total_tests = len(test_results["tests"])
    
    # Calculate the success rate
    success_rate = status_counts.get("success", 0) / total_tests * 100 if total_tests > 0 else 0
    
    # Generate the summary
    summary = {
        "timestamp": test_results["timestamp"],
        "total_tests": total_tests,
        "success_rate": success_rate,
        "status_counts": dict(status_counts),
        "tests": test_results["tests"]
    }
    
    return summary

def generate_markdown_report(summary, output_file=None):
    """Generate a markdown report of the test results."""
    # Create the markdown report
    report = f"# Implementation Conflicts & Mitigation Strategies Test Report\n\n"
    report += f"**Generated on:** {summary['timestamp']}\n\n"
    
    # Add the summary
    report += "## Summary\n\n"
    report += f"- **Total Tests:** {summary['total_tests']}\n"
    report += f"- **Success Rate:** {summary['success_rate']:.2f}%\n\n"
    
    # Add the status counts
    report += "## Status Counts\n\n"
    for status, count in summary["status_counts"].items():
        report += f"- **{status.capitalize()}:** {count}\n"
    
    # Add the test results
    report += "\n## Test Results\n\n"
    report += "| Test | Status | Time (s) | Error |\n"
    report += "|------|--------|----------|-------|\n"
    
    for test in summary["tests"]:
        name = test["name"].split(".")[-1]
        status = test["status"]
        time = test.get("time", 0)
        error = test.get("error", "")
        
        report += f"| {name} | {status} | {time:.2f} | {error} |\n"
    
    # Write the report to a file if specified
    if output_file:
        with open(output_file, "w") as f:
            f.write(report)
    
    return report

def main():
    """Main function."""
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Generate a summary report of the test results.")
    parser.add_argument("--input", "-i", default="implementation_test_results.json", help="Input file containing the test results.")
    parser.add_argument("--output", "-o", default="implementation_test_report.md", help="Output file for the markdown report.")
    args = parser.parse_args()
    
    # Load the test results
    test_results = load_test_results(args.input)
    
    # Generate the summary
    summary = generate_summary(test_results)
    
    # Generate the markdown report
    report = generate_markdown_report(summary, args.output)
    
    # Print the report to the console
    print(report)
    
    print(f"\nReport saved to {args.output}")

if __name__ == "__main__":
    main() 