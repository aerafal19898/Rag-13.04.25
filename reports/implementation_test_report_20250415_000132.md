# Implementation Test Report
Generated on: 2025-04-15 00:01:32

## Summary
- Total Tests: 8
- Failures: 0
- Errors: 8
- Overall Status: FAILED

## Test Details

### Errors

#### Error 1
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 50, in setUp
    self.deployment_manager = DeploymentManager(db_manager=self.db_manager)
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 40, in __init__
    self._init_db()
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 50, in _init_db
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 2
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 50, in setUp
    self.deployment_manager = DeploymentManager(db_manager=self.db_manager)
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 40, in __init__
    self._init_db()
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 50, in _init_db
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 3
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 50, in setUp
    self.deployment_manager = DeploymentManager(db_manager=self.db_manager)
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 40, in __init__
    self._init_db()
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 50, in _init_db
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 4
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 50, in setUp
    self.deployment_manager = DeploymentManager(db_manager=self.db_manager)
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 40, in __init__
    self._init_db()
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 50, in _init_db
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 5
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 50, in setUp
    self.deployment_manager = DeploymentManager(db_manager=self.db_manager)
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 40, in __init__
    self._init_db()
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 50, in _init_db
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 6
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 50, in setUp
    self.deployment_manager = DeploymentManager(db_manager=self.db_manager)
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 40, in __init__
    self._init_db()
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 50, in _init_db
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 7
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 50, in setUp
    self.deployment_manager = DeploymentManager(db_manager=self.db_manager)
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 40, in __init__
    self._init_db()
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 50, in _init_db
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```

#### Error 8
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 50, in setUp
    self.deployment_manager = DeploymentManager(db_manager=self.db_manager)
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 40, in __init__
    self._init_db()
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\app\services\deployment.py", line 50, in _init_db
    self.db_manager.execute("""
    ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'DatabaseManager' object has no attribute 'execute'

```
