# Implementation Test Report
Generated on: 2025-04-15 00:06:24

## Summary
- Total Tests: 8
- Failures: 0
- Errors: 4
- Overall Status: FAILED

## Test Details

### Errors

#### Error 1
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 69, in test_1_1_framework_conflicts
    client = TestClient(app=self.api_gateway)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\venv\Lib\site-packages\starlette\testclient.py", line 429, in __init__
    super().__init__(
TypeError: Client.__init__() got an unexpected keyword argument 'app'

```

#### Error 2
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 146, in test_1_3_authentication_conflicts
    cursor.execute(
sqlite3.IntegrityError: NOT NULL constraint failed: users.email

```

#### Error 3
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 225, in test_1_5_frontend_backend_integration_conflicts
    api_version = self.api_contract.get_api_version(version_id)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'APIContractManager' object has no attribute 'get_api_version'

```

#### Error 4
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 268, in test_1_6_environment_configuration_conflicts
    self.assertEqual(config["id"], config_id)
                     ~~~~~~^^^^^^
KeyError: 'id'

```
