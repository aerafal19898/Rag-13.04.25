#!/usr/bin/env python
"""
Script to run implementation tests and generate a report.
"""

import os
import sys
import unittest
import json
from datetime import datetime
from test_implementation_conflicts import TestImplementationConflicts

def run_tests():
    """Run the implementation tests and return the results."""
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestImplementationConflicts)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return the results
    return {
        'total': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success': result.wasSuccessful(),
        'details': {
            'failures': [str(f[1]) for f in result.failures],
            'errors': [str(e[1]) for e in result.errors]
        }
    }

def generate_report(results):
    """Generate a markdown report from the test results."""
    # Create the report directory if it doesn't exist
    os.makedirs('reports', exist_ok=True)
    
    # Generate the report filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f'reports/implementation_test_report_{timestamp}.md'
    
    # Generate the report content
    report_content = f"""# Implementation Test Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Tests: {results['total']}
- Failures: {results['failures']}
- Errors: {results['errors']}
- Overall Status: {'PASSED' if results['success'] else 'FAILED'}

## Test Details
"""
    
    # Add failure details
    if results['details']['failures']:
        report_content += "\n### Failures\n"
        for i, failure in enumerate(results['details']['failures'], 1):
            report_content += f"\n#### Failure {i}\n```\n{failure}\n```\n"
    
    # Add error details
    if results['details']['errors']:
        report_content += "\n### Errors\n"
        for i, error in enumerate(results['details']['errors'], 1):
            report_content += f"\n#### Error {i}\n```\n{error}\n```\n"
    
    # Write the report to file
    with open(report_file, 'w') as f:
        f.write(report_content)
    
    return report_file

def main():
    """Main function to run tests and generate report."""
    print("Running implementation tests...")
    results = run_tests()
    
    print("\nGenerating report...")
    report_file = generate_report(results)
    
    print(f"\nTest results:")
    print(f"Total tests: {results['total']}")
    print(f"Failures: {results['failures']}")
    print(f"Errors: {results['errors']}")
    print(f"Overall status: {'PASSED' if results['success'] else 'FAILED'}")
    print(f"\nDetailed report generated: {report_file}")
    
    # Return appropriate exit code
    sys.exit(0 if results['success'] else 1)

if __name__ == '__main__':
    main() 