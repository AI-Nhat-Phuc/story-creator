# DESIGN — [Feature Name]

> **Status**: DRAFT | APPROVED
> **Phase**: DESIGN
> **Date**:

---

## Changed Files

| File | Change Type  | Maps to Spec Clause |
| ---- | ------------ | ------------------- |
|      | NEW / MODIFY |                     |

## Schema / Interface Changes

> Signatures and types only. NO business logic.

```python
# api/schemas/...
```

## Model Changes

> Changes in api/core/models/.

```python
# api/core/models/...
```

## New Method Signatures

> Declare interfaces — body should be `pass` or `raise NotImplementedError`.

```python
def new_method(arg1: type, arg2: type) -> ReturnType:
    raise NotImplementedError
```
