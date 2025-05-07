# Implementation Test Report
Generated on: 2025-04-15 11:02:50

## Summary
- Total Tests: 8
- Failures: 0
- Errors: 2
- Overall Status: FAILED

## Test Details

### Errors

#### Error 1
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 68, in test_1_1_framework_conflicts
    client = TestClient(app=self.api_gateway)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\venv\Lib\site-packages\starlette\testclient.py", line 429, in __init__
    super().__init__(
TypeError: Client.__init__() got an unexpected keyword argument 'app'

```

#### Error 2
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 218, in test_1_5_frontend_backend_integration_conflicts
    cursor.execute("DELETE FROM contract_tests")
sqlite3.OperationalError: no such table: contract_tests

```
