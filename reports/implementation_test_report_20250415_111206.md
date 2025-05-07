# Implementation Test Report
Generated on: 2025-04-15 11:12:06

## Summary
- Total Tests: 8
- Failures: 0
- Errors: 1
- Overall Status: FAILED

## Test Details

### Errors

#### Error 1
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 96, in test_1_1_framework_conflicts
    client = TestClient(self.api_gateway, base_url="http://test")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\venv\Lib\site-packages\starlette\testclient.py", line 429, in __init__
    super().__init__(
TypeError: Client.__init__() got an unexpected keyword argument 'app'

```
