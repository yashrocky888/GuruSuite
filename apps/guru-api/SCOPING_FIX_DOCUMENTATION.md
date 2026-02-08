# 🔒 Python Scoping Error Fix: `get_nakshatra_lord` Variable Access Issue

## 📋 Executive Summary

**Problem**: FastAPI endpoint `/kundli` returned HTTP 500 with error:
```
Error: cannot access local variable 'get_nakshatra_lord' where it is not associated with a value
```

**Root Cause**: Python's scoping rules treated `get_nakshatra_lord` as a local variable inside a nested function, even though it was imported at module level.

**Solution**: Explicit closure binding + module-level import + documentation to prevent future violations.

**Status**: ✅ **FIXED** (Cloud Run revision `guru-api-00083-x7h`)

---

## 🔍 Detailed Problem Analysis

### The Error Message

```
Error: cannot access local variable 'get_nakshatra_lord' where it is not associated with a value
```

This error occurs when Python's compiler sees a variable name used in a function, and determines it should be treated as a **local variable**, but the variable is accessed before it's assigned.

### Where the Error Occurred

**File**: `apps/guru-api/src/api/kundli_routes.py`

**Function**: `kundli_get()` (line ~341)

**Nested Function**: `build_standardized_varga_response()` (line ~648)

**Error Location**: Inside `build_standardized_varga_response()`, when calling `get_nakshatra_lord()` on lines 751 and 774.

### Why Python Thought It Was a Local Variable

Python's scoping rules work as follows:

1. **LEGB Rule** (Local → Enclosing → Global → Built-in):
   - Python first checks if a variable is **local** (assigned inside the function)
   - If ANY assignment to a variable name exists in a function, Python treats it as **local** for the ENTIRE function
   - This happens at **compile time**, not runtime

2. **The Problem Pattern**:
   ```python
   # Module level
   from src.jyotish.dasha_drik import get_nakshatra_lord  # ✅ Global scope
   
   async def kundli_get(...):
       # Inside kundli_get()
       base_kundli["Ascendant"]["nakshatra_lord"] = get_nakshatra_lord(...)  # ✅ Works here
       
       def build_standardized_varga_response(...):  # ❌ Nested function
           # Inside nested function
           "nakshatra_lord": get_nakshatra_lord(...)  # ❌ ERROR: Python thinks it's local!
   ```

3. **Why It Failed**:
   - Even though `get_nakshatra_lord` was imported at module level (global scope)
   - Even though it was used successfully in the outer function `kundli_get()`
   - Python's compiler saw the nested function using `get_nakshatra_lord`
   - If there was ANY possibility of a local assignment (even in a conditional import or try/except), Python treated it as **local**
   - Since no local assignment existed, accessing it raised: "cannot access local variable"

### Historical Context

**Initial Attempts** (that failed):

1. **First Fix**: Moved import to module level
   - ✅ Correct approach
   - ❌ Still failed because nested function couldn't access it properly

2. **Second Fix**: Removed inner imports
   - ✅ Removed `get_nakshatra_lord` from inner `from src.jyotish.dasha_drik import ...`
   - ❌ Still failed because Python's closure mechanism wasn't capturing it

3. **Third Fix**: Added assert guard
   - ✅ Added `assert callable(get_nakshatra_lord)` at function entry
   - ❌ Still failed because assert doesn't help with nested function scoping

**Final Fix** (that worked):
- Explicit closure binding: `_get_nakshatra_lord_fn = get_nakshatra_lord`
- Use the bound alias in nested function
- This forces Python to capture the variable in the closure

---

## ✅ The Complete Fix

### Step 1: Module-Level Import (Single Source of Truth)

**Location**: Top of `apps/guru-api/src/api/kundli_routes.py` (line ~32)

**Code**:
```python
# 🔒 CRITICAL: Import get_nakshatra_lord at module level to prevent scoping errors
from src.jyotish.dasha_drik import get_nakshatra_lord
```

**Why**: This ensures `get_nakshatra_lord` is in the **global scope**, accessible to all functions in the module.

**Documentation Added**:
```python
# 🔒 SCOPING SAFETY CONTRACT (FOR ALL FUTURE EDITS / AI AGENTS)
# - get_nakshatra_lord MUST be imported ONLY at module level, NEVER inside kundli_get()
# - kundli_get() and its nested helpers must ONLY CALL get_nakshatra_lord (or a captured alias),
#   they must NOT re-import or reassign it anywhere inside the function body.
# - Violating this rule causes Python to treat get_nakshatra_lord as a local variable
#   and raises: "cannot access local variable 'get_nakshatra_lord' where it is not associated with a value"
```

### Step 2: Assert Guard at Function Entry

**Location**: Inside `kundli_get()`, immediately after function definition (line ~356)

**Code**:
```python
# 🔒 CRITICAL: Hard asserts at API entry point - ensures core helpers are callable
# This forces immediate failure if scoping/shadowing rules are violated
assert callable(_normalize_sign_index), "_normalize_sign_index is not callable"
assert callable(get_nakshatra_lord), "get_nakshatra_lord is not callable (scoping violation)"
```

**Why**: This provides **early detection** if scoping is broken. If `get_nakshatra_lord` is not accessible, the assert fails immediately with a clear error message.

### Step 3: Explicit Closure Binding (The Key Fix)

**Location**: Inside `kundli_get()`, right before nested function definition (line ~650)

**Code**:
```python
# Helper function to build standardized varga chart response
# 🔒 CRITICAL: Explicitly capture get_nakshatra_lord in closure to prevent scoping errors
# This ensures the nested function can access the module-level import
_get_nakshatra_lord_fn = get_nakshatra_lord  # Explicit closure binding

def build_standardized_varga_response(varga_chart: Dict, chart_type: str) -> Dict:
    """Build standardized varga chart response matching D1 structure."""
    # ... rest of function
```

**Why This Works**:

1. **Explicit Assignment**: `_get_nakshatra_lord_fn = get_nakshatra_lord` creates a **local variable** in `kundli_get()`'s scope
2. **Closure Capture**: When `build_standardized_varga_response` is defined, Python **automatically captures** `_get_nakshatra_lord_fn` in its closure
3. **No Ambiguity**: Python knows `_get_nakshatra_lord_fn` is a closure variable, not a local variable
4. **Safe Access**: The nested function can safely access `_get_nakshatra_lord_fn` without scoping errors

**Python Closure Mechanism**:
```python
# Outer function
def outer():
    x = 10  # Local variable in outer()
    
    def inner():
        print(x)  # ✅ Python captures x from outer()'s closure
    
    return inner

# This works because Python automatically captures variables from enclosing scope
```

### Step 4: Update Nested Function to Use Closure Variable

**Location**: Inside `build_standardized_varga_response()`, lines 751 and 774

**Before** (❌ BROKEN):
```python
"nakshatra_lord": get_nakshatra_lord(base_kundli["Ascendant"].get("nakshatra_index", 0)),
```

**After** (✅ FIXED):
```python
"nakshatra_lord": _get_nakshatra_lord_fn(base_kundli["Ascendant"].get("nakshatra_index", 0)),
```

**Why**: Using the explicitly captured closure variable `_get_nakshatra_lord_fn` instead of the module-level `get_nakshatra_lord` avoids Python's scoping ambiguity.

### Step 5: Keep Outer Function Usage Unchanged

**Location**: Inside `kundli_get()`, lines 462 and 470

**Code** (✅ CORRECT - No changes needed):
```python
# 🔒 D1 NAKSHATRA LORD ATTACHMENT (ASCENDANT)
if "Ascendant" in base_kundli and "nakshatra_index" in base_kundli["Ascendant"]:
    base_kundli["Ascendant"]["nakshatra_lord"] = get_nakshatra_lord(
        base_kundli["Ascendant"]["nakshatra_index"]
    )

# 🔒 D1 NAKSHATRA LORD ATTACHMENT (PLANETS)
for planet_name, pdata in base_kundli.get("Planets", {}).items():
    if "nakshatra_index" in pdata:
        pdata["nakshatra_lord"] = get_nakshatra_lord(pdata["nakshatra_index"])
```

**Why**: The outer function `kundli_get()` can directly access the module-level `get_nakshatra_lord` without issues. Only the **nested function** needed the closure binding.

---

## 📊 Code Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ MODULE LEVEL (Global Scope)                                 │
│                                                             │
│ from src.jyotish.dasha_drik import get_nakshatra_lord      │
│ ✅ get_nakshatra_lord is in GLOBAL scope                    │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ accessible
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ FUNCTION: kundli_get()                                      │
│                                                             │
│ assert callable(get_nakshatra_lord)  ✅ Works (global)     │
│                                                             │
│ base_kundli[...] = get_nakshatra_lord(...)  ✅ Works       │
│                                                             │
│ _get_nakshatra_lord_fn = get_nakshatra_lord  ✅ Closure     │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │ NESTED FUNCTION: build_standardized_varga_response()│  │
│   │                                                     │  │
│   │ ❌ get_nakshatra_lord(...)  → ERROR (scoping)       │  │
│   │ ✅ _get_nakshatra_lord_fn(...)  → WORKS (closure)  │  │
│   └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚫 What NOT To Do (Anti-Patterns)

### ❌ Anti-Pattern 1: Inner Import

```python
async def kundli_get(...):
    # ❌ WRONG: Importing inside function
    from src.jyotish.dasha_drik import get_nakshatra_lord
    
    def nested():
        get_nakshatra_lord(...)  # ❌ Scoping error
```

**Why It Fails**: Python treats `get_nakshatra_lord` as a local variable in `kundli_get()`, but nested function tries to access it before assignment.

### ❌ Anti-Pattern 2: Conditional Import

```python
async def kundli_get(...):
    if some_condition:
        from src.jyotish.dasha_drik import get_nakshatra_lord
    
    def nested():
        get_nakshatra_lord(...)  # ❌ Scoping error
```

**Why It Fails**: Even if the import is conditional, Python's compiler sees the name and treats it as local for the entire function.

### ❌ Anti-Pattern 3: Try/Except Import

```python
async def kundli_get(...):
    try:
        from src.jyotish.dasha_drik import get_nakshatra_lord
    except ImportError:
        get_nakshatra_lord = None
    
    def nested():
        get_nakshatra_lord(...)  # ❌ Scoping error
```

**Why It Fails**: Python sees `get_nakshatra_lord = None` and treats it as a local variable, causing scoping issues.

### ❌ Anti-Pattern 4: Reassignment

```python
async def kundli_get(...):
    get_nakshatra_lord = some_other_function  # ❌ Reassignment
    
    def nested():
        get_nakshatra_lord(...)  # ❌ Scoping error
```

**Why It Fails**: Any assignment to `get_nakshatra_lord` makes Python treat it as local.

---

## ✅ Correct Patterns

### ✅ Pattern 1: Module-Level Import + Direct Use (Outer Function)

```python
# Module level
from src.jyotish.dasha_drik import get_nakshatra_lord

async def kundli_get(...):
    # ✅ CORRECT: Direct use in outer function
    result = get_nakshatra_lord(index)
```

### ✅ Pattern 2: Module-Level Import + Closure Binding (Nested Function)

```python
# Module level
from src.jyotish.dasha_drik import get_nakshatra_lord

async def kundli_get(...):
    # ✅ CORRECT: Explicit closure binding
    _get_nakshatra_lord_fn = get_nakshatra_lord
    
    def nested():
        # ✅ CORRECT: Use closure variable
        result = _get_nakshatra_lord_fn(index)
```

### ✅ Pattern 3: Pass as Parameter (Alternative)

```python
# Module level
from src.jyotish.dasha_drik import get_nakshatra_lord

async def kundli_get(...):
    def nested(nakshatra_lord_fn=get_nakshatra_lord):
        # ✅ CORRECT: Use parameter (default value captures from closure)
        result = nakshatra_lord_fn(index)
```

---

## 🧪 Testing the Fix

### Before Fix

**Request**: `GET /api/v1/kundli?dob=2006-02-03&time=22:30&lat=12.9767936&lon=77.590082&timezone=Asia/Kolkata`

**Response**: HTTP 500
```json
{
  "detail": "Error calculating kundli: cannot access local variable 'get_nakshatra_lord' where it is not associated with a value"
}
```

### After Fix

**Request**: Same as above

**Response**: HTTP 200
```json
{
  "D1": {
    "Ascendant": {
      "nakshatra": "Uttara Phalguni",
      "nakshatra_index": 11,
      "nakshatra_lord": "Sun",  // ✅ Now present
      ...
    },
    "Planets": {
      "Sun": {
        "nakshatra": "Rohini",
        "nakshatra_index": 3,
        "nakshatra_lord": "Moon",  // ✅ Now present
        ...
      },
      ...
    }
  },
  "D2": {
    "Ascendant": {
      "nakshatra": "Uttara Phalguni",  // ✅ Same as D1
      "nakshatra_lord": "Sun",  // ✅ Same as D1
      ...
    },
    ...
  },
  ...
}
```

---

## 📝 Deployment History

- **Revision**: `guru-api-00083-x7h`
- **Region**: `asia-south1`
- **Service URL**: `https://guru-api-660206747784.asia-south1.run.app`
- **Status**: ✅ Serving 100% of traffic
- **Date**: 2026-01-XX

---

## 🔒 Future Maintenance Guidelines

### For AI Agents (ChatGPT, Claude, etc.)

**CRITICAL RULES**:

1. **NEVER** import `get_nakshatra_lord` inside `kundli_get()` or any nested function
2. **NEVER** reassign `get_nakshatra_lord` anywhere in the file
3. **NEVER** remove the explicit closure binding `_get_nakshatra_lord_fn = get_nakshatra_lord`
4. **NEVER** change nested function to use `get_nakshatra_lord` directly (must use `_get_nakshatra_lord_fn`)
5. **ALWAYS** keep module-level import at top of file
6. **ALWAYS** keep assert guard in `kundli_get()`

**If You Need to Modify Nakshatra Logic**:

- ✅ Modify the **calls** to `get_nakshatra_lord()` or `_get_nakshatra_lord_fn()`
- ✅ Modify the **parameters** passed to these functions
- ✅ Modify the **response structure** that stores the results
- ❌ **DO NOT** modify how `get_nakshatra_lord` is imported or accessed

### For Human Developers

**If You See This Error Again**:

1. Check if `get_nakshatra_lord` is imported at module level (should be line ~32)
2. Check if there's any inner import of `get_nakshatra_lord` (should be NONE)
3. Check if `_get_nakshatra_lord_fn = get_nakshatra_lord` exists before nested function (should be line ~650)
4. Check if nested function uses `_get_nakshatra_lord_fn` not `get_nakshatra_lord` (should be lines 751, 774)
5. Check if assert guard exists in `kundli_get()` (should be line ~356)

**Quick Fix Checklist**:

- [ ] Module-level import exists
- [ ] No inner imports of `get_nakshatra_lord`
- [ ] Closure binding exists: `_get_nakshatra_lord_fn = get_nakshatra_lord`
- [ ] Nested function uses `_get_nakshatra_lord_fn`
- [ ] Assert guard exists
- [ ] Backend restarted
- [ ] Cloud Run redeployed (if production)

---

## 📚 Related Python Concepts

### Python Scoping Rules (LEGB)

- **L**ocal: Variables assigned inside a function
- **E**nclosing: Variables in enclosing (nested) functions
- **G**lobal: Variables at module level
- **B**uilt-in: Python's built-in functions

### Closure Mechanism

A closure is a function that "remembers" variables from its enclosing scope, even after the outer function has finished executing.

```python
def outer(x):
    def inner():
        return x  # x is captured from outer()'s scope
    return inner

closure = outer(10)
print(closure())  # Prints: 10
```

### Compile-Time vs Runtime

Python's scoping decisions are made at **compile time** (when the `.py` file is parsed), not at **runtime** (when the code executes). This is why conditional imports or try/except blocks don't help with scoping issues.

---

## ✅ Summary

**Problem**: Python scoping rules caused nested function to treat `get_nakshatra_lord` as a local variable, causing "cannot access local variable" error.

**Solution**: 
1. Module-level import (single source of truth)
2. Assert guard (early detection)
3. Explicit closure binding (`_get_nakshatra_lord_fn = get_nakshatra_lord`)
4. Use closure variable in nested function

**Result**: ✅ Error fixed, API returns 200, Nakshatra Lord visible in D1-D60.

**Prevention**: Documentation and code comments prevent future violations.

---

**Last Updated**: 2026-01-XX  
**Fixed By**: AI Assistant (Auto)  
**Verified**: ✅ Production deployment successful
