# Implementation Test Report
Generated on: 2025-04-15 11:09:40

## Summary
- Total Tests: 8
- Failures: 0
- Errors: 9
- Overall Status: FAILED

## Test Details

### Errors

#### Error 1
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpq6fceozj\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 80, in tearDown
    self.temp_dir.cleanup()
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 947, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 929, in _rmtree
    _shutil.rmtree(name, onerror=onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 787, in rmtree
    return _rmtree_unsafe(path, onerror)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 634, in _rmtree_unsafe
    onerror(os.unlink, fullname, sys.exc_info())
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 893, in onerror
    _os.unlink(path)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpq6fceozj\\data\\chroma\\chroma.sqlite3'

```

#### Error 2
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 90, in test_1_1_framework_conflicts
    client = TestClient(self.api_gateway, base_url="http://test")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\venv\Lib\site-packages\starlette\testclient.py", line 429, in __init__
    super().__init__(
TypeError: Client.__init__() got an unexpected keyword argument 'app'

```

#### Error 3
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpwyw1izop\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 80, in tearDown
    self.temp_dir.cleanup()
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 947, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 929, in _rmtree
    _shutil.rmtree(name, onerror=onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 787, in rmtree
    return _rmtree_unsafe(path, onerror)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 634, in _rmtree_unsafe
    onerror(os.unlink, fullname, sys.exc_info())
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 893, in onerror
    _os.unlink(path)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpwyw1izop\\data\\chroma\\chroma.sqlite3'

```

#### Error 4
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpx5gf2584\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 80, in tearDown
    self.temp_dir.cleanup()
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 947, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 929, in _rmtree
    _shutil.rmtree(name, onerror=onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 787, in rmtree
    return _rmtree_unsafe(path, onerror)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 634, in _rmtree_unsafe
    onerror(os.unlink, fullname, sys.exc_info())
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 893, in onerror
    _os.unlink(path)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpx5gf2584\\data\\chroma\\chroma.sqlite3'

```

#### Error 5
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpbo3hx6jh\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 80, in tearDown
    self.temp_dir.cleanup()
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 947, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 929, in _rmtree
    _shutil.rmtree(name, onerror=onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 787, in rmtree
    return _rmtree_unsafe(path, onerror)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 634, in _rmtree_unsafe
    onerror(os.unlink, fullname, sys.exc_info())
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 893, in onerror
    _os.unlink(path)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpbo3hx6jh\\data\\chroma\\chroma.sqlite3'

```

#### Error 6
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpw2kga47q\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 80, in tearDown
    self.temp_dir.cleanup()
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 947, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 929, in _rmtree
    _shutil.rmtree(name, onerror=onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 787, in rmtree
    return _rmtree_unsafe(path, onerror)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 634, in _rmtree_unsafe
    onerror(os.unlink, fullname, sys.exc_info())
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 893, in onerror
    _os.unlink(path)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpw2kga47q\\data\\chroma\\chroma.sqlite3'

```

#### Error 7
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpn3spa5ai\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 80, in tearDown
    self.temp_dir.cleanup()
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 947, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 929, in _rmtree
    _shutil.rmtree(name, onerror=onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 787, in rmtree
    return _rmtree_unsafe(path, onerror)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 634, in _rmtree_unsafe
    onerror(os.unlink, fullname, sys.exc_info())
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 893, in onerror
    _os.unlink(path)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpn3spa5ai\\data\\chroma\\chroma.sqlite3'

```

#### Error 8
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpq97lze9y\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 80, in tearDown
    self.temp_dir.cleanup()
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 947, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 929, in _rmtree
    _shutil.rmtree(name, onerror=onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 787, in rmtree
    return _rmtree_unsafe(path, onerror)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 634, in _rmtree_unsafe
    onerror(os.unlink, fullname, sys.exc_info())
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 893, in onerror
    _os.unlink(path)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpq97lze9y\\data\\chroma\\chroma.sqlite3'

```

#### Error 9
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpwlkx94c4\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 80, in tearDown
    self.temp_dir.cleanup()
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 947, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 929, in _rmtree
    _shutil.rmtree(name, onerror=onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 787, in rmtree
    return _rmtree_unsafe(path, onerror)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 629, in _rmtree_unsafe
    _rmtree_unsafe(fullname, onerror)
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 634, in _rmtree_unsafe
    onerror(os.unlink, fullname, sys.exc_info())
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\tempfile.py", line 893, in onerror
    _os.unlink(path)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpwlkx94c4\\data\\chroma\\chroma.sqlite3'

```
