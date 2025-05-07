# Implementation Test Report
Generated on: 2025-04-15 00:02:32

## Summary
- Total Tests: 8
- Failures: 0
- Errors: 16
- Overall Status: FAILED

## Test Details

### Errors

#### Error 1
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 320, in test_1_10_testing_strategy_conflicts
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 2
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 55, in tearDown
    self.db_manager.close()
    ^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'close'

```

#### Error 3
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 71, in test_1_1_framework_conflicts
    client = TestClient(self.api_gateway)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\venv\Lib\site-packages\starlette\testclient.py", line 429, in __init__
    super().__init__(
TypeError: Client.__init__() got an unexpected keyword argument 'app'

```

#### Error 4
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 55, in tearDown
    self.db_manager.close()
    ^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'close'

```

#### Error 5
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 94, in test_1_2_database_conflicts
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 6
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 55, in tearDown
    self.db_manager.close()
    ^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'close'

```

#### Error 7
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 132, in test_1_3_authentication_conflicts
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 8
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 55, in tearDown
    self.db_manager.close()
    ^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'close'

```

#### Error 9
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 177, in test_1_4_model_deployment_conflicts
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 10
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 55, in tearDown
    self.db_manager.close()
    ^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'close'

```

#### Error 11
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 213, in test_1_5_frontend_backend_integration_conflicts
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 12
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 55, in tearDown
    self.db_manager.close()
    ^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'close'

```

#### Error 13
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 248, in test_1_6_environment_configuration_conflicts
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 14
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 55, in tearDown
    self.db_manager.close()
    ^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'close'

```

#### Error 15
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 283, in test_1_9_monitoring_conflicts
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 16
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 55, in tearDown
    self.db_manager.close()
    ^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'close'

```
