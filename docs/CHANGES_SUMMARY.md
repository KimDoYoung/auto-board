# Element/Element_Type Implementation Summary

## Overview
Implemented proper two-level hierarchy for form element type specification:
- **element**: The HTML element type (input, select, textarea, checkbox, etc.)
- **element_type**: The specific type attribute for that element (text, date, number for input; single for select; toggle for checkbox; etc.)

## Changes Made

### 1. step3_create_edit.js - Configuration Mappings

#### Added Element and Element Type Labels
```javascript
const elementLabels = {
    'input': '입력필드',
    'textarea': '텍스트영역',
    'select': '선택상자',
    'checkbox': '체크박스',
    'html_editor': 'HTML 에디터',
    'file': '파일',
    'range': '범위선택'
};

const elementTypeValueLabels = {
    'text': '텍스트',
    'date': '날짜선택',
    'number': '숫자',
    'email': '이메일',
    'tel': '전화번호',
    'time': '시간',
    'plain': '일반텍스트',
    'single': '단일선택',
    'toggle': '토글',
    'slider': '슬라이더',
    'file': '파일',
    'html': 'HTML'
};
```

#### Fixed populateElementTypes() Function
**Before**: Used non-existent `elementTypesByDataType` mapping
**After**: Uses correct `elementsByDataType` mapping
```javascript
// Correct version:
populateElementTypes(selectElement, dataType) {
    selectElement.innerHTML = '';
    const allowedElements = elementsByDataType[dataType] || [];

    allowedElements.forEach(element => {
        const option = document.createElement('option');
        option.value = element;
        option.textContent = elementLabels[element] || element;
        selectElement.appendChild(option);
    });
}
```

#### Fixed addField() Default Element Selection
**Before**: Incorrectly used `defaultElementTypeByDataType` (which contains element_type values like 'date')
**After**: Uses correct `defaultElementByDataType` (which contains element values like 'input')
```javascript
// Before (WRONG):
const defaultElementType = defaultElementTypeByDataType[columnInfo.data_type] || ...;
selectElement.value = defaultElementType; // Would set 'date' instead of 'input'!

// After (CORRECT):
const defaultElement = defaultElementByDataType[columnInfo.data_type] || ...;
selectElement.value = defaultElement; // Sets 'input' ✓
```

#### Fixed getFormData() element_type Assignment
**Before**: `element_type: element` (treating them as the same)
**After**: Properly derives element_type from data type mapping with fallback
```javascript
// Before (WRONG):
element_type: element, // Would set 'input' when we need 'date' for ymd!

// After (CORRECT):
element_type: defaultElementTypeByDataType[dataType] || defaultElementTypeByElement[element] || 'text',
// For ymd: element='input', element_type='date' ✓
```

#### Fixed HTML Editor element_type Value
**Before**: `element_type: 'html_editor'`
**After**: `element_type: 'html'` (matches mapping structure)

### 2. step3.html - Edit Mode Compatibility

Updated HTML Editor detection to use correct element_type value:
```javascript
// Before:
if (fieldData.element === 'html_editor' && fieldData.element_type === 'html_editor') {

// After:
if (fieldData.element === 'html_editor' && fieldData.element_type === 'html') {
```

## Data Flow Example: YMD Field

### Creation (Step 3)
```json
{
  "name": "생일",
  "label": "생일",
  "data_type": "ymd",
  "element": "input",      // ← HTML element type
  "element_type": "date",  // ← HTML input type attribute
  "required": true,
  "width": "100%",
  "order": 1
}
```

### Rendering (Step 4 onwards)
```html
<input type="date" ... />
<!-- Translates to: <input type="element_type" /> -->
```

## Mapping Structure

```
Data Type (ymd)
    ↓
elementsByDataType['ymd'] = ['input']
    ↓
defaultElementByDataType['ymd'] = 'input'  (What element to show)
    ↓
elementTypesByElement['input'] = ['text', 'date', 'number', ...]
    ↓
defaultElementTypeByDataType['ymd'] = 'date'  (What type attribute to use)
    ↓
Final: <input type="date" />
```

## Backward Compatibility

- Edit mode correctly handles fields with proper element/element_type structure
- element_type is auto-derived from mappings (doesn't need to be stored separately)
- Form editing maintains consistency through re-derives on form submission

## Testing Checklist

- [ ] Create new board with ymd column
- [ ] Verify Step 3 shows "입력필드" (input) as element option
- [ ] Submit Step 3 and check console logs show:
  - element: "input"
  - element_type: "date"
- [ ] Verify database stores correct JSON structure
- [ ] Test editing the same form and re-submitting
- [ ] Check Step 4 view rendering handles element/element_type correctly
- [ ] Create records and verify date input works

## Files Modified

1. **app/static/js/wizard/step3_create_edit.js**
   - Fixed mappings and labels
   - Fixed populateElementTypes()
   - Fixed addField() default element selection
   - Fixed getFormData() element_type assignment
   - Fixed HTML Editor element_type value

2. **app/templates/board/wizard/step3.html**
   - Fixed HTML Editor detection for edit mode
