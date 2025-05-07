# Implementation Test Report
Generated on: 2025-04-15 00:05:11

## Summary
- Total Tests: 8
- Failures: 0
- Errors: 5
- Overall Status: FAILED

## Test Details

### Errors

#### Error 1
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 68, in test_1_1_framework_conflicts
    client = TestClient(self.api_gateway)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\venv\Lib\site-packages\starlette\testclient.py", line 429, in __init__
    super().__init__(
TypeError: Client.__init__() got an unexpected keyword argument 'app'

```

#### Error 2
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 142, in test_1_3_authentication_conflicts
    password_hash = self.auth_service._hash_password(password)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'AuthService' object has no attribute '_hash_password'

```

#### Error 3
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 199, in test_1_4_model_deployment_conflicts
    model = self.model_registry.get_model(model_id)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'ModelRegistry' object has no attribute 'get_model'

```

#### Error 4
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 237, in test_1_5_frontend_backend_integration_conflicts
    api_version = self.api_contract.get_api_version(version_id)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'APIContractManager' object has no attribute 'get_api_version'

```

#### Error 5
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 280, in test_1_6_environment_configuration_conflicts
    self.assertEqual(config["id"], config_id)
                     ~~~~~~^^^^^^
KeyError: 'id'

```
