// Variables from Jinja2 template are defined in the HTML inline script block
// Copy them to local scope for use in this module
const allColumns = window.allColumns || [];
const createEditConfig = window.createEditConfig || null;
const boardData = window.boardData || {};
const boardId = window.boardId || 0;

// 데이터 타입 한글 변환
const dataTypeLabels = {
    'string': '문자열',
    'text': '문장',
    'integer': '정수',
    'float': '실수(소수점포함)',
    'boolean': '참/거짓',
    'ymd': '날짜',
    'datetime': '날짜시간'
};

// element_type 설정 (constants/element_type.py와 동기화)
const elementTypesConfig = {
    'input-text': { label: '문자열', htmlType: 'text' },
    'input-html': { label: '문장', htmlType: null },
    'input-date': { label: '날짜', htmlType: 'date' },
    'input-integer': { label: '정수', htmlType: 'number' },
    'input-real': { label: '실수', htmlType: 'number' },
    'input-email': { label: '이메일', htmlType: 'email' },
    'radio': { label: '라디오 버튼', htmlType: 'radio' },
    'checkbox-multi': { label: '체크박스 (다중)', htmlType: 'checkbox' },
    'checkbox': { label: '체크박스', htmlType: 'checkbox' }
};

// 데이터 타입별 권장 element_type
const elementTypeByDataType = {
    'string': 'input-text',
    'text': 'input-html',
    'integer': 'input-integer',
    'real': 'input-real',
    'boolean': 'checkbox',
    'ymd': 'input-date',
    'datetime': 'input-date'
};

const wizardStep3 = {
    fieldCount: 0,

    // Element Type 드롭다운 동적 채우기 (element_type.py의 값 사용)
    populateElementTypes(selectElement, dataType) {
        selectElement.innerHTML = '';

        // 데이터 타입별 권장 element_type
        const recommendedType = elementTypeByDataType[dataType];

        // 모든 element_type 표시 (사용자가 선택하게 함)
        Object.entries(elementTypesConfig).forEach(([value, config]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = config.label;
            // 권장 타입은 먼저 표시
            if (value === recommendedType) {
                option.textContent += ' (추천)';
            }
            selectElement.appendChild(option);
        });

        // 권장 타입으로 기본값 설정
        if (recommendedType) {
            selectElement.value = recommendedType;
        }
    },

    addField(columnName) {
        this.fieldCount++;
        const container = document.getElementById('fieldsContainer');

        // 컬럼 정보 찾기
        let columnInfo = allColumns.find(col => col.name === columnName);

        // attachment(파일)는 allColumns에 없으므로 가상 데이터 생성
        if (!columnInfo && columnName === 'attachment') {
            columnInfo = {
                name: 'attachment',
                label: '첨부파일',
                data_type: 'string'
            };
        }

        if (!columnInfo) return;

        const field = document.createElement('div');
        field.className = 'bg-gray-50 rounded-lg p-4 border border-gray-200 space-y-3 cursor-move';
        field.dataset.fieldIndex = this.fieldCount;
        field.dataset.columnName = columnName;

        const fieldIndex = this.fieldCount;
        field.innerHTML = `
            <!-- Header Row: Column Info, Required Checkbox, Control Buttons -->
            <div class="flex justify-between items-start gap-3">
                <div class="flex gap-2 items-center flex-shrink-0 mt-1">
                    <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"></path>
                    </svg>
                </div>
                <div class="flex-1">
                    <div class="flex items-center gap-3">
                        <span class="inline-block px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">${columnInfo.label}</span>
                        <span class="text-xs text-gray-500">(${dataTypeLabels[columnInfo.data_type] || columnInfo.data_type})</span>
                        <label class="flex items-center gap-2 cursor-pointer ml-auto">
                            <input type="checkbox" class="field-required w-4 h-4 text-indigo-600 rounded" checked>
                            <span class="text-gray-700 text-xs font-medium">필수</span>
                        </label>
                    </div>
                    <input type="hidden" class="field-name" value="${columnName}">
                    <input type="hidden" class="field-data-type" value="${columnInfo.data_type}">
                </div>
                <div class="flex gap-2 flex-shrink-0">
                    <button type="button" onclick="wizardStep3.moveFieldUp(${fieldIndex})" class="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 hover:bg-indigo-200 font-bold flex items-center justify-center" title="위로">↑</button>
                    <button type="button" onclick="wizardStep3.moveFieldDown(${fieldIndex})" class="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 hover:bg-indigo-200 font-bold flex items-center justify-center" title="아래로">↓</button>
                    <button type="button" onclick="wizardStep3.removeField(${fieldIndex})" class="w-8 h-8 rounded-full bg-red-100 text-red-600 hover:bg-red-200 font-bold flex items-center justify-center" title="삭제">✕</button>
                </div>
            </div>

            <!-- Row 1: Element Type, Default Value, Min Value, Max Value -->
            <div class="grid gap-3" style="grid-template-columns: 2fr 1.5fr 1fr 1fr;">
                <div>
                    <label class="block text-gray-700 font-medium text-xs mb-1">입력 요소 타입</label>
                    <select class="field-element-type w-full px-3 py-2 border border-gray-300 rounded text-sm" onchange="wizardStep3.updateFieldOptions(${fieldIndex})">
                        <!-- Options will be populated dynamically -->
                    </select>
                </div>
                <div>
                    <label class="block text-gray-700 font-medium text-xs mb-1">기본값</label>
                    <input type="text" class="field-default-value w-full px-3 py-2 border border-gray-300 rounded text-sm" placeholder="">
                </div>
                <div class="field-min-value-container" style="display: none;">
                    <label class="block text-gray-700 font-medium text-xs mb-1">Min</label>
                    <input type="text" class="field-min-value w-full px-3 py-2 border border-gray-300 rounded text-sm" placeholder="">
                </div>
                <div class="field-max-value-container" style="display: none;">
                    <label class="block text-gray-700 font-medium text-xs mb-1">Max</label>
                    <input type="text" class="field-max-value w-full px-3 py-2 border border-gray-300 rounded text-sm" placeholder="">
                </div>
            </div>

            <!-- Row 2: HTML Editor (Conditional - only for input-html) -->
            <div class="field-html-editor-container" style="display: none;">
                <label class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" class="field-use-html-editor w-4 h-4 text-indigo-600 rounded" checked>
                    <span class="text-gray-700 text-sm">HTML 에디터 사용</span>
                </label>
            </div>

            <!-- Select/Radio Options (Hidden by default) -->
            <div class="field-select-options" style="display: none;">
                <label class="block text-gray-700 font-medium text-xs mb-2">선택 옵션</label>
                <div class="space-y-2 mb-2" data-options-list="${fieldIndex}">
                    <!-- Options will be added here -->
                </div>
                <button type="button" onclick="wizardStep3.addSelectOption(${fieldIndex})" class="text-sm text-indigo-600 hover:text-indigo-700 font-medium">
                    + 옵션 추가
                </button>
            </div>

            <!-- Checkbox Default Value (Hidden by default) -->
            <div class="field-checkbox-default" style="display: none;">
                <label class="block text-gray-700 font-medium text-xs mb-2">기본값</label>
                <div class="flex gap-4">
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="checkbox-default-${fieldIndex}" class="field-checkbox-default-value w-4 h-4 text-indigo-600" value="true">
                        <span class="text-gray-700 text-sm">True (체크)</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="checkbox-default-${fieldIndex}" class="field-checkbox-default-value w-4 h-4 text-indigo-600" value="false" checked>
                        <span class="text-gray-700 text-sm">False (미체크)</span>
                    </label>
                </div>
            </div>
        `;

        container.appendChild(field);

        // Element Type 드롭다운 동적 채우기
        const selectElement = field.querySelector('.field-element-type');
        this.populateElementTypes(selectElement, columnInfo.data_type);

        // 조건부 UI 업데이트
        this.updateFieldOptions(fieldIndex);
    },

    moveFieldUp(index) {
        const field = document.querySelector(`[data-field-index="${index}"]`);
        const prev = field.previousElementSibling;
        if (prev) {
            field.parentNode.insertBefore(field, prev);
        }
    },

    moveFieldDown(index) {
        const field = document.querySelector(`[data-field-index="${index}"]`);
        const next = field.nextElementSibling;
        if (next) {
            field.parentNode.insertBefore(next, field);
        }
    },

    removeField(index) {
        const field = document.querySelector(`[data-field-index="${index}"]`);
        if (field) {
            // 필드 삭제
            field.remove();
            // selector 옵션 업데이트
            this.updateSelectorOptions();
        }
    },

    addSelectedField() {
        const selector = document.getElementById('fieldSelector');
        const columnName = selector.value;

        if (!columnName) {
            alert('필드를 선택하세요.');
            return;
        }

        // 이미 추가된 필드인지 확인
        const alreadyAdded = document.querySelector(`[data-column-name="${columnName}"]`);
        if (alreadyAdded) {
            alert('이미 추가된 필드입니다.');
            return;
        }

        this.addField(columnName);
        this.updateSelectorOptions();
        selector.value = '';
    },

    // selector 옵션 업데이트
    updateSelectorOptions() {
        const selector = document.getElementById('fieldSelector');
        const addedFieldNames = Array.from(document.querySelectorAll('[data-column-name]')).map(el => el.dataset.columnName);

        // 모든 옵션을 순회하며 표시/숨김 상태 업데이트
        selector.querySelectorAll('option').forEach(option => {
            if (option.value === '') return; // placeholder 제외
            option.style.display = addedFieldNames.includes(option.value) ? 'none' : 'block';
        });
    },

    updateFieldOptions(index) {
        const field = document.querySelector(`[data-field-index="${index}"]`);
        const elementType = field.querySelector('.field-element-type').value;
        const dataType = field.querySelector('.field-data-type').value;
        const selectOptionsDiv = field.querySelector('.field-select-options');
        const checkboxDefaultDiv = field.querySelector('.field-checkbox-default');
        const htmlEditorContainer = field.querySelector('.field-html-editor-container');
        const minValueContainer = field.querySelector('.field-min-value-container');
        const maxValueContainer = field.querySelector('.field-max-value-container');

        // 모두 숨기기
        selectOptionsDiv.style.display = 'none';
        checkboxDefaultDiv.style.display = 'none';
        htmlEditorContainer.style.display = 'none';

        // Min/Max는 정수, 실수 타입일 때만 표시
        const numericTypes = ['integer', 'real'];
        const showMinMax = numericTypes.includes(dataType);
        minValueContainer.style.display = showMinMax ? 'block' : 'none';
        maxValueContainer.style.display = showMinMax ? 'block' : 'none';

        // HTML 에디터는 input-html 타입일 때만 표시
        if (elementType === 'input-html') {
            htmlEditorContainer.style.display = 'block';
        }

        // 선택지 필요한 타입
        if (elementType === 'radio' || elementType === 'checkbox-multi') {
            selectOptionsDiv.style.display = 'block';
        }
        // 체크박스 기본값
        else if (elementType === 'checkbox') {
            checkboxDefaultDiv.style.display = 'block';
        }
    },

    addSelectOption(index) {
        const field = document.querySelector(`[data-field-index="${index}"]`);
        const optionsList = field.querySelector(`[data-options-list="${index}"]`);
        const optionIndex = optionsList.children.length + 1;

        const optionDiv = document.createElement('div');
        optionDiv.className = 'flex gap-2 items-end';
        optionDiv.dataset.optionIndex = optionIndex;

        optionDiv.innerHTML = `
            <input type="text" placeholder="값" class="select-option-value w-24 px-2 py-1 border border-gray-300 rounded text-xs">
            <input type="text" placeholder="라벨" class="select-option-label flex-1 px-2 py-1 border border-gray-300 rounded text-xs">
            <button type="button" onclick="this.parentElement.remove()" class="text-red-600 hover:text-red-700 text-sm">삭제</button>
        `;

        optionsList.appendChild(optionDiv);
    },

    getFormData() {
        const fields = [];
        console.log('[1] 필드 수집 시작');

        document.querySelectorAll('[data-field-index]').forEach((fieldEl, index) => {
            console.log(`\n[2-${index}] 필드 처리 시작 - fieldIndex: ${fieldEl.dataset.fieldIndex}`);

            const nameEl = fieldEl.querySelector('.field-name');
            if (!nameEl) {
                console.log(`[2-${index}] ❌ field-name 엘리먼트 없음`);
                return;
            }

            const name = nameEl.value;
            if (!name) {
                console.log(`[2-${index}] ❌ 필드명 비어있음`);
                return;
            }
            console.log(`[2-${index}] ✓ 필드명: ${name}`);

            const elementTypeEl = fieldEl.querySelector('.field-element-type');
            if (!elementTypeEl) {
                console.log(`[2-${index}] ❌ field-element-type 엘리먼트 없음`);
                return;
            }

            const elementType = elementTypeEl.value;
            console.log(`[2-${index}] ✓ Element Type: ${elementType}`);

            const dataTypeEl = fieldEl.querySelector('.field-data-type');
            const dataType = dataTypeEl ? dataTypeEl.value : 'unknown';
            console.log(`[2-${index}] ✓ 데이터 타입: ${dataType}`);

            const columnInfo = allColumns.find(col => col.name === name) ||
                             (name === 'attachment' ? { label: '첨부파일' } : null);

            const fieldData = {
                name: name,
                label: columnInfo ? columnInfo.label : name,
                data_type: dataType,
                element_type: elementType,
                required: fieldEl.querySelector('.field-required').checked,
                order: index + 1  // 화면 상 순서대로 order 설정
            };

            console.log(`[2-${index}] 기본 필드:`, {
                name: fieldData.name,
                label: fieldData.label,
                element_type: fieldData.element_type,
                required: fieldData.required,
                data_type: fieldData.data_type
            });

            // 선택적 필드
            const defaultValue = fieldEl.querySelector('.field-default-value').value.trim();
            if (defaultValue) {
                fieldData.default_value = defaultValue;
                console.log(`[2-${index}] ✓ 기본값: ${defaultValue}`);
            }

            const minValueEl = fieldEl.querySelector('.field-min-value');
            const minValue = minValueEl ? minValueEl.value.trim() : '';
            if (minValue) {
                fieldData.min_value = isNaN(minValue) ? minValue : parseFloat(minValue);
                console.log(`[2-${index}] ✓ Min 값: ${fieldData.min_value}`);
            }

            const maxValueEl = fieldEl.querySelector('.field-max-value');
            const maxValue = maxValueEl ? maxValueEl.value.trim() : '';
            if (maxValue) {
                fieldData.max_value = isNaN(maxValue) ? maxValue : parseFloat(maxValue);
                console.log(`[2-${index}] ✓ Max 값: ${fieldData.max_value}`);
            }

            // Radio/Checkbox-Multi 타입: options 수집
            if (elementType === 'radio' || elementType === 'checkbox-multi') {
                console.log(`[2-${index}] ${elementType} 타입 - 옵션 수집 중...`);
                const optionsList = fieldEl.querySelector('[data-options-list]');
                if (optionsList) {
                    const options = [];
                    optionsList.querySelectorAll('[data-option-index]').forEach(optionEl => {
                        const optValue = optionEl.querySelector('.select-option-value').value.trim();
                        const optLabel = optionEl.querySelector('.select-option-label').value.trim();
                        if (optValue && optLabel) {
                            options.push({ value: optValue, label: optLabel });
                            console.log(`[2-${index}]   - 옵션: ${optValue} / ${optLabel}`);
                        }
                    });
                    if (options.length > 0) {
                        fieldData.options = options;
                        console.log(`[2-${index}] ✓ 옵션 ${options.length}개 추가됨`);
                    }
                }
            }

            // Checkbox 타입: default_value를 true/false로 설정
            if (elementType === 'checkbox') {
                console.log(`[2-${index}] Checkbox 타입 - 기본값 확인 중...`);
                const checkboxDefault = fieldEl.querySelector('.field-checkbox-default-value:checked');
                if (checkboxDefault) {
                    fieldData.default_value = checkboxDefault.value === 'true';
                    console.log(`[2-${index}] ✓ Checkbox 기본값: ${fieldData.default_value}`);
                }
            }

            console.log(`[2-${index}] ✅ 최종 필드 데이터:`, fieldData);
            fields.push(fieldData);
        });

        const formData = {
            create_edit: {
                columns: fields
            }
        };

        console.log('\n[3] 최종 제출 데이터:', JSON.stringify(formData, null, 2));
        return formData;
    },

    async submit() {
        try {
            console.log('\n' + '='.repeat(60));
            console.log('[SUBMIT] 제출 시작');
            console.log('='.repeat(60));

            const formData = this.getFormData();

            if (formData.create_edit.columns.length === 0) {
                console.log('[SUBMIT] ❌ 필드가 비어있음 - 제출 중단');
                alert('최소 1개 이상의 필드를 추가하세요.');
                return;
            }

            console.log(`[SUBMIT] ✓ 총 ${formData.create_edit.columns.length}개 필드 준비 완료`);
            console.log(`[SUBMIT] 요청 URL: /boards/new/step3/${boardId}`);
            console.log('[SUBMIT] 요청 메소드: POST');
            console.log('[SUBMIT] 요청 헤더: Content-Type: application/json');

            const response = await fetch(`/boards/new/step3/${boardId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            console.log(`[SUBMIT] 응답 상태: ${response.status} ${response.statusText}`);
            console.log(`[SUBMIT] 응답 Content-Type: ${response.headers.get('content-type')}`);

            const data = await response.json();
            console.log('[SUBMIT] 응답 데이터:', data);

            if (!response.ok) {
                console.log('[SUBMIT] ❌ 오류 응답');
                alert('오류: ' + (data.detail || '알 수 없는 오류'));
                return;
            }

            console.log('[SUBMIT] ✓ 성공');
            console.log('[SUBMIT] 리다이렉트 경로:', data.redirect);
            console.log('='.repeat(60));
            window.location.href = data.redirect;
        } catch (error) {
            console.error('[SUBMIT] ❌ 예외 발생:', error);
            console.error('[SUBMIT] 오류 메시지:', error.message);
            console.error('[SUBMIT] 스택:', error.stack);
            alert('오류: ' + error.message);
        }
    }
};

// Initialization moved to HTML file to avoid duplication
/* Disabled - initialization now handled by step3.html DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
        const option = document.createElement('option');
        option.value = column.name;
        option.textContent = `${column.label} (${column.name})`;
        selector.appendChild(option);
        console.log(`[INIT-1] ${idx + 1}. ${column.label} (${column.name})`);
    });
    console.log(`[INIT-1] ✓ 총 ${allColumns.length}개 컬럼 추가됨`);

    // [1-1] is_file_attach가 true이면 파일 필드를 selector에 추가
    if (boardData && boardData.is_file_attach) {
        console.log('\n[INIT-1-1] is_file_attach = true → 파일 필드 추가');
        const fileOption = document.createElement('option');
        fileOption.value = 'attachment';
        fileOption.textContent = '첨부파일 (attachment)';
        selector.appendChild(fileOption);
        console.log('[INIT-1-1] ✓ 첨부파일 필드 추가됨');
    } else {
        console.log('\n[INIT-1-1] is_file_attach = false 또는 없음');
    }

    // [2] 기존 설정이 있으면 로드 (edit mode)
    console.log('\n[INIT-2] 기존 설정 확인...');
    const fieldsToLoad = createEditConfig && (createEditConfig.columns || createEditConfig.fields) || null;
    if (fieldsToLoad && fieldsToLoad.length > 0) {
        console.log(`[INIT-2] ✓ EDIT MODE - 기존 필드 ${fieldsToLoad.length}개 로드`);
        console.log('[INIT-2] 기존 필드 목록:', fieldsToLoad.map(f => f.name));
        fieldsToLoad.forEach((fieldData, fieldIdx) => {
            console.log(`\n[INIT-2-${fieldIdx}] 필드 로드: ${fieldData.name}`);
            console.log(`[INIT-2-${fieldIdx}] 저장된 데이터:`, fieldData);

            wizardStep3.addField(fieldData.name);
            // 필드별 설정값 적용
            const lastField = document.querySelector('[data-field-index]:last-of-type');
            if (lastField) {
                const elementTypeSelect = lastField.querySelector('.field-element-type');
                const dataType = lastField.querySelector('.field-data-type').value;

                // [1] 엘리먼트 타입 설정 (HTML Editor 처리)
                let elementToSet = fieldData.element;
                let useHtmlEditor = false;

                if (fieldData.element === 'html_editor' && fieldData.element_type === 'html_editor') {
                    elementToSet = 'textarea';
                    useHtmlEditor = true;
                    console.log(`[INIT-2-${fieldIdx}] HTML Editor 감지 - textarea로 변환`);
                }

                // 동적으로 생성된 옵션 중에서 해당 element 선택
                if (elementTypeSelect) {
                    elementTypeSelect.value = elementToSet;
                    console.log(`[INIT-2-${fieldIdx}] ✓ Element 타입 설정: ${elementToSet}`);
                }

                // [2] 기본 필드 설정
                lastField.querySelector('.field-required').checked = fieldData.required || false;
                lastField.querySelector('.field-width').value = fieldData.width || '100%';
                lastField.querySelector('.field-help-text').value = fieldData.help_text || '';
                lastField.querySelector('.field-inline-group').value = fieldData.inline_group || '';
                console.log(`[INIT-2-${fieldIdx}] ✓ 기본 필드 설정 완료`);

                // [3] Min/Max 값 설정
                if (fieldData.min_value !== undefined) {
                    lastField.querySelector('.field-min-value').value = fieldData.min_value;
                    console.log(`[INIT-2-${fieldIdx}] ✓ Min 값: ${fieldData.min_value}`);
                }
                if (fieldData.max_value !== undefined) {
                    lastField.querySelector('.field-max-value').value = fieldData.max_value;
                    console.log(`[INIT-2-${fieldIdx}] ✓ Max 값: ${fieldData.max_value}`);
                }

                // [4] Select 타입: options 복원
                if (fieldData.element === 'select' && fieldData.options) {
                    console.log(`[INIT-2-${fieldIdx}] Select 타입 - ${fieldData.options.length}개 옵션 복원 중...`);
                    const optionsList = lastField.querySelector('[data-options-list]');
                    if (optionsList) {
                        fieldData.options.forEach((opt, optIdx) => {
                            wizardStep3.addSelectOption(lastField.dataset.fieldIndex);
                            const lastOption = optionsList.lastElementChild;
                            if (lastOption) {
                                lastOption.querySelector('.select-option-value').value = opt.value;
                                lastOption.querySelector('.select-option-label').value = opt.label;
                                console.log(`[INIT-2-${fieldIdx}]   - 옵션 ${optIdx + 1}: ${opt.value} / ${opt.label}`);
                            }
                        });
                    }
                }

                // [5] Checkbox 타입: default_value 복원
                if (fieldData.element === 'checkbox' && fieldData.default_value !== undefined) {
                    const defaultValue = fieldData.default_value === true ? 'true' : 'false';
                    const radio = lastField.querySelector(`input[name="checkbox-default-${lastField.dataset.fieldIndex}"][value="${defaultValue}"]`);
                    if (radio) {
                        radio.checked = true;
                        console.log(`[INIT-2-${fieldIdx}] ✓ Checkbox 기본값: ${defaultValue}`);
                    }
                }

                // [6] HTML Editor 사용 여부 복원
                if (useHtmlEditor) {
                    const htmlEditorCheckbox = lastField.querySelector('.field-use-html-editor');
                    if (htmlEditorCheckbox) {
                        htmlEditorCheckbox.checked = true;
                        console.log(`[INIT-2-${fieldIdx}] ✓ HTML Editor 활성화`);
                    }
                }

                // [7] 초기값 설정
                if (fieldData.default_value && fieldData.element !== 'checkbox' && fieldData.element !== 'html_editor') {
                    lastField.querySelector('.field-default-value').value = fieldData.default_value;
                    console.log(`[INIT-2-${fieldIdx}] ✓ 기본값: ${fieldData.default_value}`);
                }

                // [8] 조건부 UI 업데이트 (옵션/체크박스 표시)
                wizardStep3.updateFieldOptions(lastField.dataset.fieldIndex);
                console.log(`[INIT-2-${fieldIdx}] ✓ UI 업데이트 완료`);
            }
        });

        // [3] selector 옵션 업데이트 (추가된 필드들은 숨기기)
        console.log('\n[INIT-3] Selector 옵션 업데이트 중...');
        wizardStep3.updateSelectorOptions();
        console.log('[INIT-3] ✓ 완료');

        console.log('\n[INIT] ✅ EDIT MODE 초기화 완료');
    } else {
        // [2-1] 새로 생성하는 mode - 처음부터 모든 필드를 추가
        console.log('[INIT-2] ✓ CREATE MODE - 모든 필드 추가');
        allColumns.forEach((column, idx) => {
            console.log(`[INIT-2] ${idx + 1}. ${column.label} (${column.name}) 추가 중...`);
            wizardStep3.addField(column.name);
        });
        console.log(`[INIT-2] ✓ 총 ${allColumns.length}개 필드 추가됨`);

        // [2-2] is_file_attach가 true이면 파일 필드도 자동 추가
        if (boardData && boardData.is_file_attach) {
            console.log('\n[INIT-2-2] is_file_attach = true → 파일 필드 자동 추가');
            // 파일 필드용 가상 컬럼 데이터 생성
            const fileFieldData = {
                name: 'attachment',
                label: '첨부파일',
                data_type: 'string',
                required: false
            };

            // 파일 필드를 직접 추가
            wizardStep3.fieldCount++;
            const container = document.getElementById('fieldsContainer');
            const field = document.createElement('div');
            const fieldIndex = wizardStep3.fieldCount;
            console.log('[INIT-2-2] ✓ 첨부파일 필드 추가 중...');

            field.className = 'bg-gray-50 rounded-lg p-4 border border-gray-200 space-y-3 cursor-move';
            field.dataset.fieldIndex = fieldIndex;
            field.dataset.columnName = 'attachment';

            field.innerHTML = `
                <div class="flex justify-between items-start gap-3">
                    <div class="flex gap-2 items-center flex-shrink-0 mt-1">
                        <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"></path>
                        </svg>
                    </div>
                    <div class="flex-1">
                        <span class="inline-block px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">첨부파일 (string)</span>
                        <input type="hidden" class="field-name" value="attachment">
                        <input type="hidden" class="field-data-type" value="string">
                    </div>
                    <div class="flex gap-2 flex-shrink-0">
                        <button type="button" onclick="wizardStep3.moveFieldUp(${fieldIndex})" class="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 hover:bg-indigo-200 font-bold flex items-center justify-center" title="위로">↑</button>
                        <button type="button" onclick="wizardStep3.moveFieldDown(${fieldIndex})" class="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 hover:bg-indigo-200 font-bold flex items-center justify-center" title="아래로">↓</button>
                        <button type="button" onclick="wizardStep3.removeField(${fieldIndex})" class="w-8 h-8 rounded-full bg-red-100 text-red-600 hover:bg-red-200 font-bold flex items-center justify-center" title="삭제">✕</button>
                    </div>
                </div>

                <!-- Row 1: Element Type, Required, Width -->
                <div class="grid grid-cols-3 gap-3">
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">엘리먼트 타입</label>
                        <select class="field-element-type w-full px-3 py-2 border border-gray-300 rounded text-sm" onchange="wizardStep3.updateFieldOptions(${fieldIndex})">
                            <option value="file">파일</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">너비</label>
                        <input type="text" class="field-width w-full px-3 py-2 border border-gray-300 rounded text-sm" placeholder="100%, 50%, 30%, auto" value="100%">
                    </div>
                    <div>
                        <label class="flex items-center gap-2 cursor-pointer" style="margin-top: 24px;">
                            <input type="checkbox" class="field-required w-4 h-4 text-indigo-600 rounded" checked>
                            <span class="text-gray-700 text-sm">필수 입력</span>
                        </label>
                    </div>
                </div>

                <!-- Row 2: Inline Group, Help Text -->
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">인라인 그룹</label>
                        <input type="text" class="field-inline-group w-full px-3 py-2 border border-gray-300 rounded text-sm" placeholder="예: header, meta, options">
                    </div>
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">도움말</label>
                        <input type="text" class="field-help-text w-full px-3 py-2 border border-gray-300 rounded text-sm" placeholder="예: 기록 날짜를 선택하세요">
                    </div>
                </div>

                <!-- Row 3: Default Value, Min Value, Max Value -->
                <div class="grid grid-cols-3 gap-3">
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">기본값</label>
                        <input type="text" class="field-default-value w-full px-3 py-2 border border-gray-300 rounded text-sm" placeholder="예: today, 5">
                    </div>
                    <div class="field-min-max-container" style="display: none;">
                        <label class="block text-gray-700 font-medium text-xs mb-1">Min 값</label>
                        <input type="text" class="field-min-value w-full px-3 py-2 border border-gray-300 rounded text-sm" placeholder="예: 0, 1">
                    </div>
                    <div class="field-min-max-container" style="display: none;">
                        <label class="block text-gray-700 font-medium text-xs mb-1">Max 값</label>
                        <input type="text" class="field-max-value w-full px-3 py-2 border border-gray-300 rounded text-sm" placeholder="예: 100, 10">
                    </div>
                </div>

                <!-- Row 4: HTML Editor (Conditional) -->
                <div class="field-html-editor-container" style="display: none;">
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" class="field-use-html-editor w-4 h-4 text-indigo-600 rounded">
                        <span class="text-gray-700 text-sm">HTML 에디터 사용</span>
                    </label>
                </div>

                <!-- Select Options (Hidden by default) -->
                <div class="field-select-options" style="display: none;">
                    <label class="block text-gray-700 font-medium text-xs mb-2">선택 옵션</label>
                    <div class="space-y-2 mb-2" data-options-list="${fieldIndex}">
                        <!-- Options will be added here -->
                    </div>
                    <button type="button" onclick="wizardStep3.addSelectOption(${fieldIndex})" class="text-sm text-indigo-600 hover:text-indigo-700 font-medium">
                        + 옵션 추가
                    </button>
                </div>

                <!-- Checkbox Default (Hidden by default) -->
                <div class="field-checkbox-default" style="display: none;">
                    <label class="block text-gray-700 font-medium text-xs mb-2">기본값</label>
                    <div class="flex gap-4">
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="radio" name="checkbox-default-${fieldIndex}" class="field-checkbox-default-value w-4 h-4 text-indigo-600" value="true">
                            <span class="text-gray-700 text-sm">True (체크)</span>
                        </label>
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="radio" name="checkbox-default-${fieldIndex}" class="field-checkbox-default-value w-4 h-4 text-indigo-600" value="false" checked>
                            <span class="text-gray-700 text-sm">False (미체크)</span>
                        </label>
                    </div>
                </div>
            `;

            container.appendChild(field);
            wizardStep3.updateSelectorOptions();
            console.log('[INIT-2-2] ✓ 첨부파일 필드 추가 완료');
        } else {
            console.log('[INIT-2-2] is_file_attach = false 또는 없음');
        }
    }

    console.log('\n[INIT] ✅ CREATE MODE 초기화 완료');
    console.log('='.repeat(60));
});
*/
