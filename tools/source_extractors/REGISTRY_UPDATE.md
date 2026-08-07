Update `tools/source_extractors/registry.py` to include:

```python
from . import source_00, source_01, source_02

EXTRACTORS = {
    "SOURCE_00": source_00.extract,
    "SOURCE_01": source_01.extract,
    "SOURCE_02": source_02.extract,
}
```
