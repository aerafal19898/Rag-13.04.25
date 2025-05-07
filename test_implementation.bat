@echo off
REM Script to run all the implementation tests and generate a report

REM Set the Python path
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Run the tests
echo Running implementation tests...
python run_implementation_tests.py

REM Check if the tests were successful
if %ERRORLEVEL% EQU 0 (
    echo Tests completed successfully.
) else (
    echo Tests failed. Check the test results for details.
)

REM Generate the report
echo Generating test report...
python generate_test_summary.py

REM Check if the report was generated successfully
if %ERRORLEVEL% EQU 0 (
    echo Report generated successfully.
    echo Report saved to implementation_test_report.md
) else (
    echo Failed to generate report.
)

REM Print a summary of the test results
echo Test Summary:
echo -------------
echo Total Tests: 
type implementation_test_report.md | findstr /c:"|" | find /c /v ""
echo Success Rate: 
type implementation_test_report.md | findstr "Success Rate"
echo -------------

REM Exit with the appropriate status code
if %ERRORLEVEL% EQU 0 (
    exit /b 0
) else (
    exit /b 1
) 