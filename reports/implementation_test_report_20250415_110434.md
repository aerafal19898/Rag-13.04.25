# Implementation Test Report
Generated on: 2025-04-15 11:04:34

## Summary
- Total Tests: 8
- Failures: 1
- Errors: 9
- Overall Status: FAILED

## Test Details

### Failures

#### Failure 1
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 272, in test_1_5_frontend_backend_integration_conflicts
    self.assertEqual(len(versions), 1)
AssertionError: 9 != 1

```

### Errors

#### Error 1
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 59, in tearDown
    self.temp_dir.cleanup()
    ^^^^^^^^^^^^^
AttributeError: 'TestImplementationConflicts' object has no attribute 'temp_dir'

```

#### Error 2
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 69, in test_1_1_framework_conflicts
    client = TestClient(self.api_gateway)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\venv\Lib\site-packages\starlette\testclient.py", line 429, in __init__
    super().__init__(
TypeError: Client.__init__() got an unexpected keyword argument 'app'

```

#### Error 3
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 59, in tearDown
    self.temp_dir.cleanup()
    ^^^^^^^^^^^^^
AttributeError: 'TestImplementationConflicts' object has no attribute 'temp_dir'

```

#### Error 4
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 59, in tearDown
    self.temp_dir.cleanup()
    ^^^^^^^^^^^^^
AttributeError: 'TestImplementationConflicts' object has no attribute 'temp_dir'

```

#### Error 5
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 59, in tearDown
    self.temp_dir.cleanup()
    ^^^^^^^^^^^^^
AttributeError: 'TestImplementationConflicts' object has no attribute 'temp_dir'

```

#### Error 6
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 59, in tearDown
    self.temp_dir.cleanup()
    ^^^^^^^^^^^^^
AttributeError: 'TestImplementationConflicts' object has no attribute 'temp_dir'

```

#### Error 7
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 59, in tearDown
    self.temp_dir.cleanup()
    ^^^^^^^^^^^^^
AttributeError: 'TestImplementationConflicts' object has no attribute 'temp_dir'

```

#### Error 8
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 59, in tearDown
    self.temp_dir.cleanup()
    ^^^^^^^^^^^^^
AttributeError: 'TestImplementationConflicts' object has no attribute 'temp_dir'

```

#### Error 9
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 59, in tearDown
    self.temp_dir.cleanup()
    ^^^^^^^^^^^^^
AttributeError: 'TestImplementationConflicts' object has no attribute 'temp_dir'

```
