#!/bin/bash
# Script to run all the implementation tests and generate a report

# Set the Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the tests
echo "Running implementation tests..."
python run_implementation_tests.py

# Check if the tests were successful
if [ $? -eq 0 ]; then
    echo "Tests completed successfully."
else
    echo "Tests failed. Check the test results for details."
fi

# Generate the report
echo "Generating test report..."
python generate_test_summary.py

# Check if the report was generated successfully
if [ $? -eq 0 ]; then
    echo "Report generated successfully."
    echo "Report saved to implementation_test_report.md"
else
    echo "Failed to generate report."
fi

# Print a summary of the test results
echo "Test Summary:"
echo "-------------"
echo "Total Tests: $(grep -c "|" implementation_test_report.md | awk '{print $1 - 2}')"
echo "Success Rate: $(grep "Success Rate" implementation_test_report.md | awk '{print $3}')"
echo "-------------"

# Exit with the appropriate status code
if [ $? -eq 0 ]; then
    exit 0
else
    exit 1
fi 