# Implementation Test Report
Generated on: 2025-04-15 10:55:27

## Summary
- Total Tests: 8
- Failures: 1
- Errors: 1
- Overall Status: FAILED

## Test Details

### Failures

#### Failure 1
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 269, in test_1_5_frontend_backend_integration_conflicts
    self.assertEqual(len(versions), 1)
AssertionError: 5 != 1

```

### Errors

#### Error 1
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 69, in test_1_1_framework_conflicts
    client = TestClient(app)
             ^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\venv\Lib\site-packages\starlette\testclient.py", line 429, in __init__
    super().__init__(
TypeError: Client.__init__() got an unexpected keyword argument 'app'

```
