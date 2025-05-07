# Implementation Test Report
Generated on: 2025-04-15 11:06:59

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
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmp5c4u1geh\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 75, in tearDown
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
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmp5c4u1geh\\data\\chroma\\chroma.sqlite3'

```

#### Error 2
```
Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 85, in test_1_1_framework_conflicts
    client = TestClient(self.api_gateway)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\venv\Lib\site-packages\starlette\testclient.py", line 429, in __init__
    super().__init__(
TypeError: Client.__init__() got an unexpected keyword argument 'app'

```

#### Error 3
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmp3lrxjvd0\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 75, in tearDown
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
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmp3lrxjvd0\\data\\chroma\\chroma.sqlite3'

```

#### Error 4
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpuocr2xl6\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 75, in tearDown
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
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpuocr2xl6\\data\\chroma\\chroma.sqlite3'

```

#### Error 5
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpzxhf6qys\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 75, in tearDown
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
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpzxhf6qys\\data\\chroma\\chroma.sqlite3'

```

#### Error 6
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmp3cy55l8x\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 75, in tearDown
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
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmp3cy55l8x\\data\\chroma\\chroma.sqlite3'

```

#### Error 7
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpuof84z68\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 75, in tearDown
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
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpuof84z68\\data\\chroma\\chroma.sqlite3'

```

#### Error 8
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpwdwbb_og\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 75, in tearDown
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
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmpwdwbb_og\\data\\chroma\\chroma.sqlite3'

```

#### Error 9
```
Traceback (most recent call last):
  File "C:\Users\andri\AppData\Local\Programs\Python\Python311\Lib\shutil.py", line 632, in _rmtree_unsafe
    os.unlink(fullname)
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmp27fntbco\\data\\chroma\\chroma.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\andri\OneDrive\Bureau\Rag 13.04.25\test_implementation_conflicts.py", line 75, in tearDown
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
PermissionError: [WinError 32] Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus: 'C:\\Users\\andri\\AppData\\Local\\Temp\\tmp27fntbco\\data\\chroma\\chroma.sqlite3'

```
