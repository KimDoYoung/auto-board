// Variables from Jinja2 template are defined in the HTML inline script block
// Copy them to local scope for use in this module
const columnsData = window.columnsData || [];
const viewConfig = window.viewConfig || null;
const boardData = window.boardData || {};
const boardId = window.boardId || 0;

console.log('\n' + '='.repeat(60));
console.log('[STEP4-INIT-0] Step 4 초기화 시작');
console.log('='.repeat(60));
console.log('[STEP4-INIT-0-1] Board 정보:', boardData);
console.log('[STEP4-INIT-0-2] 컬럼 데이터:', columnsData);
console.log('[STEP4-INIT-0-3] 기존 view config:', viewConfig);

const wizardStep4 = {
    sectionCount: 0,
    fieldCount: {},
    columns: columnsData,
    isEditMode: false,

    init() {
        console.log('\n[STEP4-INIT-1] init() 실행 중...');

        // 기존 설정이 있는지 확인 (edit mode)
        const columnsToLoad = viewConfig && (viewConfig.columns || viewConfig.display_fields) || null;
        if (columnsToLoad && columnsToLoad.length > 0) {
            console.log('[STEP4-INIT-2] EDIT MODE 감지 - 기존 view 설정 로드');
            this.isEditMode = true;
            this.loadExistingConfig();
        } else {
            console.log('[STEP4-INIT-2] CREATE MODE - 새로운 설정 생성');
            this.isEditMode = false;
            // Initialize with default section
            this.addSection();
            this.populateFieldsFromColumns();
        }

        console.log('[STEP4-INIT-3] ✓ 초기화 완료');
    },

    loadExistingConfig() {
        console.log('[STEP4-INIT-2-1] 기존 view 설정 로드 시작');

        // 섹션별로 필드를 그룹화
        const displayFields = viewConfig.columns || viewConfig.display_fields || [];
        const sectionMap = {};
        displayFields.forEach(field => {
            const section = field.section || 'default';
            if (!sectionMap[section]) {
                sectionMap[section] = {
                    fields: []
                };
            }
            sectionMap[section].fields.push(field);
            console.log(`[STEP4-INIT-2-1-${Object.keys(sectionMap).length}] 필드 로드: ${field.name} (섹션: ${section})`);
        });

        // 각 섹션 추가
        Object.entries(sectionMap).forEach(([sectionId, sectionData]) => {
            console.log(`[STEP4-INIT-2-2] 섹션 추가: ${sectionId || 'default'}`);
            this.addSection();

            // 섹션의 필드들 추가
            sectionData.fields.forEach((fieldData, fieldIdx) => {
                console.log(`[STEP4-INIT-2-3-${fieldIdx}] 필드 UI 생성: ${fieldData.name}`);
                this.addField(this.sectionCount, fieldData);

                const fieldsContainer = document.querySelector(`[data-section-fields="${this.sectionCount}"]`);
                const fieldEl = fieldsContainer.lastElementChild;

                if (fieldEl) {
                    // 기본 필드 설정
                    const nameSelect = fieldEl.querySelector('.field-name');
                    if (nameSelect) {
                        nameSelect.value = fieldData.name;
                        console.log(`[STEP4-INIT-2-3-${fieldIdx}] ✓ 필드명: ${fieldData.name}`);
                    }

                    const labelInput = fieldEl.querySelector('.field-label');
                    if (labelInput) {
                        labelInput.value = fieldData.label || fieldData.name;
                        console.log(`[STEP4-INIT-2-3-${fieldIdx}] ✓ 라벨: ${fieldData.label}`);
                    }

                    const displayTypeSelect = fieldEl.querySelector('.field-display-type');
                    if (displayTypeSelect) {
                        displayTypeSelect.value = fieldData.display_type;
                        console.log(`[STEP4-INIT-2-3-${fieldIdx}] ✓ 표시타입: ${fieldData.display_type}`);
                        // 조건부 옵션 생성
                        displayTypeSelect.dispatchEvent(new Event('change'));
                    }

                    // 선택적 필드 복원
                    if (fieldData.width) {
                        fieldEl.querySelector('.field-width').value = fieldData.width;
                        console.log(`[STEP4-INIT-2-3-${fieldIdx}] ✓ 너비: ${fieldData.width}`);
                    }

                    if (fieldData.inline_group) {
                        fieldEl.querySelector('.field-inline-group').value = fieldData.inline_group;
                        console.log(`[STEP4-INIT-2-3-${fieldIdx}] ✓ 인라인그룹: ${fieldData.inline_group}`);
                    }

                    if (fieldData.full_width) {
                        fieldEl.querySelector('.field-full-width').checked = true;
                        console.log(`[STEP4-INIT-2-3-${fieldIdx}] ✓ 전체너비: true`);
                    }

                    if (fieldData.hide_label) {
                        fieldEl.querySelector('.field-hide-label').checked = true;
                        console.log(`[STEP4-INIT-2-3-${fieldIdx}] ✓ 라벨숨기기: true`);
                    }

                    if (fieldData.style_class) {
                        fieldEl.querySelector('.field-style-class').value = fieldData.style_class;
                        console.log(`[STEP4-INIT-2-3-${fieldIdx}] ✓ 스타일: ${fieldData.style_class}`);
                    }

                    // Display type 별 옵션 복원
                    this.restoreDisplayTypeOptions(fieldEl, fieldData);
                }
            });
        });

        console.log('[STEP4-INIT-2-4] ✓ 기존 설정 모두 로드 완료');
    },

    restoreDisplayTypeOptions(fieldEl, fieldData) {
        const displayType = fieldData.display_type;
        const optionsContainer = fieldEl.querySelector('[id^="displayTypeOptions_"]');
        if (!optionsContainer) return;

        console.log(`[STEP4-INIT-OPT] ${fieldData.name}의 옵션 복원 (타입: ${displayType})`);

        if (displayType === 'date' && fieldData.format) {
            const formatInput = optionsContainer.querySelector('.field-format');
            if (formatInput) {
                formatInput.value = fieldData.format;
                console.log(`[STEP4-INIT-OPT]   - format: ${fieldData.format}`);
            }
        } else if (displayType === 'datetime') {
            if (fieldData.format) {
                const formatInput = optionsContainer.querySelector('.field-format');
                if (formatInput) {
                    formatInput.value = fieldData.format;
                    console.log(`[STEP4-INIT-OPT]   - format: ${fieldData.format}`);
                }
            }
            if (fieldData.relative) {
                const relativeCheckbox = optionsContainer.querySelector('.field-relative');
                if (relativeCheckbox) {
                    relativeCheckbox.checked = true;
                    console.log(`[STEP4-INIT-OPT]   - relative: true`);
                }
            }
        } else if (displayType === 'stars') {
            if (fieldData.max_stars) {
                const maxStarsInput = optionsContainer.querySelector('.field-max-stars');
                if (maxStarsInput) {
                    maxStarsInput.value = fieldData.max_stars;
                    console.log(`[STEP4-INIT-OPT]   - max_stars: ${fieldData.max_stars}`);
                }
            }
            if (fieldData.show_number) {
                const showNumberCheckbox = optionsContainer.querySelector('.field-show-number');
                if (showNumberCheckbox) {
                    showNumberCheckbox.checked = true;
                    console.log(`[STEP4-INIT-OPT]   - show_number: true`);
                }
            }
        } else if (displayType === 'currency') {
            if (fieldData.currency_code) {
                const currencyInput = optionsContainer.querySelector('.field-currency-code');
                if (currencyInput) {
                    currencyInput.value = fieldData.currency_code;
                    console.log(`[STEP4-INIT-OPT]   - currency_code: ${fieldData.currency_code}`);
                }
            }
            if (fieldData.decimal_places !== undefined) {
                const decimalInput = optionsContainer.querySelector('.field-decimal-places');
                if (decimalInput) {
                    decimalInput.value = fieldData.decimal_places;
                    console.log(`[STEP4-INIT-OPT]   - decimal_places: ${fieldData.decimal_places}`);
                }
            }
            if (fieldData.thousands_separator) {
                const separatorCheckbox = optionsContainer.querySelector('.field-thousands-separator');
                if (separatorCheckbox) {
                    separatorCheckbox.checked = true;
                    console.log(`[STEP4-INIT-OPT]   - thousands_separator: true`);
                }
            }
        } else if (displayType === 'boolean') {
            if (fieldData.true_text) {
                const trueTextInput = optionsContainer.querySelector('.field-true-text');
                if (trueTextInput) {
                    trueTextInput.value = fieldData.true_text;
                    console.log(`[STEP4-INIT-OPT]   - true_text: ${fieldData.true_text}`);
                }
            }
            if (fieldData.false_text) {
                const falseTextInput = optionsContainer.querySelector('.field-false-text');
                if (falseTextInput) {
                    falseTextInput.value = fieldData.false_text;
                    console.log(`[STEP4-INIT-OPT]   - false_text: ${fieldData.false_text}`);
                }
            }
            if (fieldData.true_class) {
                const trueClassInput = optionsContainer.querySelector('.field-true-class');
                if (trueClassInput) {
                    trueClassInput.value = fieldData.true_class;
                    console.log(`[STEP4-INIT-OPT]   - true_class: ${fieldData.true_class}`);
                }
            }
            if (fieldData.false_class) {
                const falseClassInput = optionsContainer.querySelector('.field-false-class');
                if (falseClassInput) {
                    falseClassInput.value = fieldData.false_class;
                    console.log(`[STEP4-INIT-OPT]   - false_class: ${fieldData.false_class}`);
                }
            }
            if (fieldData.show_icon) {
                const showIconCheckbox = optionsContainer.querySelector('.field-show-icon');
                if (showIconCheckbox) {
                    showIconCheckbox.checked = true;
                    console.log(`[STEP4-INIT-OPT]   - show_icon: true`);
                }
            }
        } else if (displayType === 'badge' && fieldData.badge_color_map) {
            const colorMapTextarea = optionsContainer.querySelector('.field-badge-color-map');
            if (colorMapTextarea) {
                colorMapTextarea.value = JSON.stringify(fieldData.badge_color_map, null, 2);
                console.log(`[STEP4-INIT-OPT]   - badge_color_map: ${JSON.stringify(fieldData.badge_color_map)}`);
            }
        } else if (displayType === 'html' && fieldData.sanitize) {
            const sanitizeCheckbox = optionsContainer.querySelector('.field-sanitize');
            if (sanitizeCheckbox) {
                sanitizeCheckbox.checked = true;
                console.log(`[STEP4-INIT-OPT]   - sanitize: true`);
            }
        } else if (displayType === 'list') {
            if (fieldData.display_as) {
                const displayAsSelect = optionsContainer.querySelector('.field-display-as');
                if (displayAsSelect) {
                    displayAsSelect.value = fieldData.display_as;
                    console.log(`[STEP4-INIT-OPT]   - display_as: ${fieldData.display_as}`);
                }
            }
            if (fieldData.separator) {
                const separatorInput = optionsContainer.querySelector('.field-separator');
                if (separatorInput) {
                    separatorInput.value = fieldData.separator;
                    console.log(`[STEP4-INIT-OPT]   - separator: ${fieldData.separator}`);
                }
            }
            if (fieldData.hide_if_empty) {
                const hideIfEmptyCheckbox = optionsContainer.querySelector('.field-hide-if-empty');
                if (hideIfEmptyCheckbox) {
                    hideIfEmptyCheckbox.checked = true;
                    console.log(`[STEP4-INIT-OPT]   - hide_if_empty: true`);
                }
            }
        } else if (displayType === 'file_link') {
            if (fieldData.show_size) {
                const showSizeCheckbox = optionsContainer.querySelector('.field-show-size');
                if (showSizeCheckbox) {
                    showSizeCheckbox.checked = true;
                    console.log(`[STEP4-INIT-OPT]   - show_size: true`);
                }
            }
            if (fieldData.show_icon) {
                const showIconCheckbox = optionsContainer.querySelector('.field-show-icon');
                if (showIconCheckbox) {
                    showIconCheckbox.checked = true;
                    console.log(`[STEP4-INIT-OPT]   - show_icon: true`);
                }
            }
            if (fieldData.download) {
                const downloadCheckbox = optionsContainer.querySelector('.field-download');
                if (downloadCheckbox) {
                    downloadCheckbox.checked = true;
                    console.log(`[STEP4-INIT-OPT]   - download: true`);
                }
            }
        }
    },

    populateFieldsFromColumns() {
        console.log('[STEP4-INIT-3-1] populateFieldsFromColumns 시작');

        if (this.columns && this.columns.length > 0) {
            const fieldsContainer = document.querySelector('[data-section-fields="1"]');
            console.log(`[STEP4-INIT-3-2] 총 ${this.columns.length}개 컬럼 발견`);

            this.columns.forEach((col, idx) => {
                console.log(`[STEP4-INIT-3-3-${idx}] 필드 추가: ${col.name} (${col.label})`);
                this.addField(1, col);
            });

            console.log('[STEP4-INIT-3-4] ✓ populateFieldsFromColumns 완료');
        }
    },

    getDefaultDisplayType(dataType) {
        const mapping = {
            'ymd': 'date',
            'datetime': 'datetime',
            'integer': 'text',
            'float': 'currency',
            'boolean': 'boolean',
            'text': 'html',
            'string': 'text'
        };
        return mapping[dataType] || 'text';
    },

    addSection() {
        this.sectionCount++;
        const container = document.getElementById('fieldsContainer');

        const section = document.createElement('div');
        section.className = 'bg-gray-50 rounded-lg p-6 space-y-4 border border-gray-200';
        section.dataset.sectionIndex = this.sectionCount;

        section.innerHTML = `
            <div class="space-y-3" data-section-fields="${this.sectionCount}">
                <!-- Fields will be added here -->
            </div>

            <button type="button" onclick="wizardStep4.addField(${this.sectionCount})"
                class="text-indigo-600 hover:text-indigo-700 font-medium text-sm flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                필드 추가
            </button>
        `;

        container.appendChild(section);
        this.fieldCount[this.sectionCount] = 0;
    },

    addField(sectionIndex, columnData = null) {
        console.log(`[STEP4-FIELD] addField 호출됨:`, {sectionIndex, columnData});

        // [1] columnData에 data_type이 없으면 columnsData에서 찾아서 보강
        if (columnData && !columnData.data_type && columnData.name) {
            const colFromColumns = columnsData.find(col => col.name === columnData.name);
            if (colFromColumns) {
                columnData = { ...columnData, data_type: colFromColumns.data_type };
                console.log(`[STEP4-FIELD-ENRICH] data_type 보강됨: ${columnData.name} -> ${colFromColumns.data_type}`);
            }
        }

        this.fieldCount[sectionIndex]++;
        const fieldsContainer = document.querySelector(`[data-section-fields="${sectionIndex}"]`);

        const fieldIndex = this.fieldCount[sectionIndex];
        const fieldId = `field_${sectionIndex}_${fieldIndex}`;

        const field = document.createElement('div');
        field.className = 'field-card';
        field.dataset.fieldIndex = fieldIndex;
        field.dataset.sectionIndex = sectionIndex;
        field.dataset.fieldName = columnData ? columnData.name : '';

        // 데이터 타입에 따라 기본 display_type 설정
        const defaultDisplayType = columnData ? this.getDefaultDisplayType(columnData.data_type) : 'text';
        console.log(`[STEP4-FIELD-TYPE] 필드명: ${columnData?.name || 'unknown'}, data_type: ${columnData?.data_type || 'unknown'}, defaultDisplayType: ${defaultDisplayType}`);

        field.innerHTML = `
            <!-- 필드 이름 (숨겨진) -->
            <input type="hidden" class="field-name" value="${columnData ? columnData.name : ''}">

            <!-- 필드 카드 헤더 -->
            <div class="flex justify-between items-start gap-3 mb-4 pb-3 border-b">
                <div class="flex-1">
                    <div class="flex items-center gap-2">
                        <span class="text-lg font-bold text-gray-800">${columnData ? columnData.label : '필드'}</span>
                        <span class="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded">${columnData ? columnData.data_type : 'unknown'}</span>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">필드명: <code>${columnData ? columnData.name : '-'}</code></p>
                </div>
                <div class="flex gap-2">
                    <button type="button" onclick="wizardStep4.removeField(this)"
                        class="px-3 py-1 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition">
                        ✕ 제거
                    </button>
                </div>
            </div>

            <!-- Row 1: 기본 표시 설정 -->
            <div class="grid grid-cols-3 gap-4 mb-4">
                <div>
                    <label class="block text-gray-700 font-medium text-sm mb-2">표시 타입</label>
                    <select class="field-display-type w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                        onchange="wizardStep4.updateDisplayTypeOptions(this)">
                        <option value="text">text (텍스트)</option>
                        <option value="date">date (날짜)</option>
                        <option value="datetime">datetime (날짜시간)</option>
                        <option value="stars">stars (별점)</option>
                        <option value="currency">currency (통화)</option>
                        <option value="boolean">boolean (참/거짓)</option>
                        <option value="badge">badge (배지)</option>
                        <option value="html">html (HTML)</option>
                        <option value="list">list (목록)</option>
                        <option value="file_link">file_link (파일링크)</option>
                    </select>
                </div>

                <div>
                    <label class="block text-gray-700 font-medium text-sm mb-2">너비</label>
                    <input type="text" class="field-width w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                        placeholder="예: 30%, auto, 100%">
                </div>

                <div>
                    <label class="block text-gray-700 font-medium text-sm mb-2">라벨 텍스트</label>
                    <input type="text" class="field-label w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                        placeholder="표시할 라벨" value="${columnData ? (columnData.label || columnData.name) : ''}">
                </div>
            </div>

            <!-- Row 2: 레이아웃 옵션 -->
            <div class="grid grid-cols-3 gap-4 mb-4">
                <div>
                    <label class="block text-gray-700 font-medium text-sm mb-2">인라인 그룹</label>
                    <input type="text" class="field-inline-group w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                        placeholder="예: header, meta, footer">
                </div>

                <div class="flex items-end gap-4">
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" class="field-full-width w-4 h-4 text-indigo-600 rounded">
                        <span class="text-gray-700 text-sm font-medium">전체 너비</span>
                    </label>
                </div>

                <div class="flex items-end gap-4">
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" class="field-hide-label w-4 h-4 text-indigo-600 rounded">
                        <span class="text-gray-700 text-sm font-medium">라벨 숨기기</span>
                    </label>
                </div>
            </div>

            <!-- Row 3: 스타일 설정 -->
            <div class="mb-4">
                <label class="block text-gray-700 font-medium text-sm mb-2">스타일 클래스</label>
                <select class="field-style-class w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm">
                    <option value="">선택 안 함</option>
                    <option value="field-title">field-title (큰 제목)</option>
                    <option value="field-subtitle">field-subtitle (중간 제목)</option>
                    <option value="field-heading">field-heading (소제목)</option>
                    <option value="field-normal">field-normal (일반 텍스트)</option>
                    <option value="field-small">field-small (작은 텍스트)</option>
                    <option value="field-tiny">field-tiny (매우 작은 텍스트)</option>
                    <option value="field-highlight">field-highlight (강조)</option>
                    <option value="field-important">field-important (중요)</option>
                    <option value="field-info">field-info (정보)</option>
                    <option value="field-success">field-success (성공)</option>
                    <option value="field-warning">field-warning (경고)</option>
                    <option value="field-danger">field-danger (위험)</option>
                    <option value="field-card">field-card (카드)</option>
                    <option value="field-divider">field-divider (구분선)</option>
                </select>
            </div>

            <!-- Display type별 옵션 -->
            <div id="displayTypeOptions_${sectionIndex}_${fieldIndex}" class="space-y-3 mb-4 p-3 bg-gray-50 rounded-lg">
                <!-- Display type specific options will be added here -->
            </div>
        `;

        fieldsContainer.appendChild(field);

        // 기본 display type 설정
        const displayTypeSelect = field.querySelector('.field-display-type');
        displayTypeSelect.value = defaultDisplayType;
        displayTypeSelect.dispatchEvent(new Event('change'));

        console.log(`[STEP4-INIT-ADD-FIELD] 필드 추가됨: ${columnData ? columnData.name : 'unknown'} (index: ${fieldIndex})`);
    },

    updateDisplayTypeOptions(selectElement) {
        const displayType = selectElement.value;
        const fieldCard = selectElement.closest('.field-card');
        const sectionIndex = fieldCard.dataset.sectionIndex;
        const fieldIndex = fieldCard.dataset.fieldIndex;
        const optionsContainer = document.getElementById(`displayTypeOptions_${sectionIndex}_${fieldIndex}`);

        if (!optionsContainer) return;

        optionsContainer.innerHTML = '';

        if (displayType === 'date') {
            optionsContainer.innerHTML = `
                <div>
                    <label class="block text-gray-700 font-medium text-xs mb-1">날짜 포맷</label>
                    <input type="text" class="field-format w-full px-3 py-2 border border-gray-300 rounded text-sm"
                        placeholder="예: YYYY년 MM월 DD일" value="YYYY-MM-DD">
                </div>
            `;
        } else if (displayType === 'datetime') {
            optionsContainer.innerHTML = `
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">날짜시간 포맷</label>
                        <input type="text" class="field-format w-full px-3 py-2 border border-gray-300 rounded text-sm"
                            placeholder="예: YYYY-MM-DD HH:mm" value="YYYY-MM-DD HH:mm">
                    </div>
                    <div>
                        <label class="flex items-center gap-2 cursor-pointer mt-6">
                            <input type="checkbox" class="field-relative w-4 h-4 text-indigo-600 rounded">
                            <span class="text-gray-700 text-sm">상대 시간 (2시간 전)</span>
                        </label>
                    </div>
                </div>
            `;
        } else if (displayType === 'stars') {
            optionsContainer.innerHTML = `
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">최대 별점</label>
                        <input type="number" class="field-max-stars w-full px-3 py-2 border border-gray-300 rounded text-sm"
                            placeholder="10" value="10" min="1" max="10">
                    </div>
                    <div>
                        <label class="flex items-center gap-2 cursor-pointer mt-6">
                            <input type="checkbox" class="field-show-number w-4 h-4 text-indigo-600 rounded" checked>
                            <span class="text-gray-700 text-sm">숫자 표시</span>
                        </label>
                    </div>
                </div>
            `;
        } else if (displayType === 'currency') {
            optionsContainer.innerHTML = `
                <div class="grid grid-cols-3 gap-3">
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">통화 코드</label>
                        <input type="text" class="field-currency-code w-full px-3 py-2 border border-gray-300 rounded text-sm"
                            placeholder="KRW" value="KRW">
                    </div>
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">소수점</label>
                        <input type="number" class="field-decimal-places w-full px-3 py-2 border border-gray-300 rounded text-sm"
                            placeholder="0" value="0" min="0" max="3">
                    </div>
                    <div>
                        <label class="flex items-center gap-2 cursor-pointer mt-6">
                            <input type="checkbox" class="field-thousands-separator w-4 h-4 text-indigo-600 rounded" checked>
                            <span class="text-gray-700 text-sm">천단위 표시</span>
                        </label>
                    </div>
                </div>
            `;
        } else if (displayType === 'boolean') {
            optionsContainer.innerHTML = `
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">참 텍스트</label>
                        <input type="text" class="field-true-text w-full px-3 py-2 border border-gray-300 rounded text-sm"
                            placeholder="공개" value="공개">
                    </div>
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">거짓 텍스트</label>
                        <input type="text" class="field-false-text w-full px-3 py-2 border border-gray-300 rounded text-sm"
                            placeholder="비공개" value="비공개">
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">참 색상</label>
                        <input type="text" class="field-true-class w-full px-3 py-2 border border-gray-300 rounded text-sm"
                            placeholder="text-green-600" value="text-green-600">
                    </div>
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">거짓 색상</label>
                        <input type="text" class="field-false-class w-full px-3 py-2 border border-gray-300 rounded text-sm"
                            placeholder="text-gray-600" value="text-gray-600">
                    </div>
                </div>
                <div>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" class="field-show-icon w-4 h-4 text-indigo-600 rounded" checked>
                        <span class="text-gray-700 text-sm">아이콘 표시</span>
                    </label>
                </div>
            `;
        } else if (displayType === 'badge') {
            optionsContainer.innerHTML = `
                <div>
                    <label class="block text-gray-700 font-medium text-xs mb-1">색상 맵 (JSON 형식)</label>
                    <textarea class="field-badge-color-map w-full px-3 py-2 border border-gray-300 rounded text-sm font-mono h-24"
                        placeholder='{"work": "blue", "personal": "green"}'></textarea>
                </div>
            `;
        } else if (displayType === 'html') {
            optionsContainer.innerHTML = `
                <div>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" class="field-sanitize w-4 h-4 text-indigo-600 rounded" checked>
                        <span class="text-gray-700 text-sm">위험한 콘텐츠 제거</span>
                    </label>
                </div>
            `;
        } else if (displayType === 'list') {
            optionsContainer.innerHTML = `
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">표시 방식</label>
                        <select class="field-display-as w-full px-3 py-2 border border-gray-300 rounded text-sm">
                            <option value="badges">배지</option>
                            <option value="comma">쉼표 구분</option>
                            <option value="bullet">글머리</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-700 font-medium text-xs mb-1">구분자</label>
                        <input type="text" class="field-separator w-full px-3 py-2 border border-gray-300 rounded text-sm"
                            placeholder=" " value=" ">
                    </div>
                </div>
                <div>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" class="field-hide-if-empty w-4 h-4 text-indigo-600 rounded" checked>
                        <span class="text-gray-700 text-sm">비어있으면 숨기기</span>
                    </label>
                </div>
            `;
        } else if (displayType === 'file_link') {
            optionsContainer.innerHTML = `
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="checkbox" class="field-show-size w-4 h-4 text-indigo-600 rounded" checked>
                            <span class="text-gray-700 text-sm">파일 크기 표시</span>
                        </label>
                    </div>
                    <div>
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="checkbox" class="field-show-icon w-4 h-4 text-indigo-600 rounded" checked>
                            <span class="text-gray-700 text-sm">아이콘 표시</span>
                        </label>
                    </div>
                </div>
                <div>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" class="field-download w-4 h-4 text-indigo-600 rounded" checked>
                        <span class="text-gray-700 text-sm">다운로드 가능</span>
                    </label>
                </div>
            `;
        }
    },

    removeField(button) {
        button.closest('.field-card').remove();
    },

    getFormData() {
        const displayFields = [];

        document.querySelectorAll('[data-section-index]').forEach(sectionEl => {
            sectionEl.querySelectorAll('.field-card:not(.section-header)').forEach(fieldEl => {
                const fieldNameEl = fieldEl.querySelector('.field-name');
                if (!fieldNameEl) return;

                const fieldName = fieldNameEl.value?.trim();
                if (!fieldName) return;

                const fieldLabelEl = fieldEl.querySelector('.field-label');
                const fieldLabel = fieldLabelEl?.value?.trim() || '';

                const displayTypeEl = fieldEl.querySelector('.field-display-type');
                const displayType = displayTypeEl?.value || 'text';

                const widthEl = fieldEl.querySelector('.field-width');
                const width = widthEl?.value?.trim() || null;

                const inlineGroupEl = fieldEl.querySelector('.field-inline-group');
                const inlineGroup = inlineGroupEl?.value?.trim() || null;

                const fullWidthEl = fieldEl.querySelector('.field-full-width');
                const fullWidth = fullWidthEl?.checked || false;

                const hideLabelEl = fieldEl.querySelector('.field-hide-label');
                const hideLabel = hideLabelEl?.checked || false;

                const styleClassEl = fieldEl.querySelector('.field-style-class');
                const styleClass = styleClassEl?.value || null;

                const order = displayFields.length + 1;

                const field = {
                    name: fieldName,
                    label: fieldLabel || fieldName,
                    display_type: displayType,
                    order: order,
                    ...(width && { width }),
                    ...(inlineGroup && { inline_group: inlineGroup }),
                    ...(fullWidth && { full_width: true }),
                    ...(hideLabel && { hide_label: true }),
                    ...(styleClass && { style_class: styleClass })
                };

                // Add display type specific options
                if (displayType === 'date') {
                    const format = fieldEl.querySelector('.field-format')?.value.trim();
                    if (format) field.format = format;
                } else if (displayType === 'datetime') {
                    const format = fieldEl.querySelector('.field-format')?.value.trim();
                    if (format) field.format = format;
                    const relative = fieldEl.querySelector('.field-relative')?.checked;
                    if (relative) field.relative = true;
                } else if (displayType === 'stars') {
                    const maxStars = fieldEl.querySelector('.field-max-stars')?.value;
                    if (maxStars) field.max_stars = parseInt(maxStars);
                    const showNumber = fieldEl.querySelector('.field-show-number')?.checked;
                    if (showNumber) field.show_number = true;
                } else if (displayType === 'currency') {
                    const currencyCode = fieldEl.querySelector('.field-currency-code')?.value.trim();
                    if (currencyCode) field.currency_code = currencyCode;
                    const decimalPlaces = fieldEl.querySelector('.field-decimal-places')?.value;
                    if (decimalPlaces !== undefined) field.decimal_places = parseInt(decimalPlaces);
                    const separator = fieldEl.querySelector('.field-thousands-separator')?.checked;
                    if (separator) field.thousands_separator = true;
                } else if (displayType === 'boolean') {
                    const trueText = fieldEl.querySelector('.field-true-text')?.value.trim();
                    if (trueText) field.true_text = trueText;
                    const falseText = fieldEl.querySelector('.field-false-text')?.value.trim();
                    if (falseText) field.false_text = falseText;
                    const trueClass = fieldEl.querySelector('.field-true-class')?.value.trim();
                    if (trueClass) field.true_class = trueClass;
                    const falseClass = fieldEl.querySelector('.field-false-class')?.value.trim();
                    if (falseClass) field.false_class = falseClass;
                    const showIcon = fieldEl.querySelector('.field-show-icon')?.checked;
                    if (showIcon) field.show_icon = true;
                } else if (displayType === 'badge') {
                    const colorMap = fieldEl.querySelector('.field-badge-color-map')?.value.trim();
                    if (colorMap) {
                        try {
                            field.badge_color_map = JSON.parse(colorMap);
                        } catch (e) {
                            // Invalid JSON, skip
                        }
                    }
                } else if (displayType === 'html') {
                    const sanitize = fieldEl.querySelector('.field-sanitize')?.checked;
                    if (sanitize) field.sanitize = true;
                } else if (displayType === 'list') {
                    const displayAs = fieldEl.querySelector('.field-display-as')?.value;
                    if (displayAs) field.display_as = displayAs;
                    const separator = fieldEl.querySelector('.field-separator')?.value;
                    if (separator) field.separator = separator;
                    const hideIfEmpty = fieldEl.querySelector('.field-hide-if-empty')?.checked;
                    if (hideIfEmpty) field.hide_if_empty = true;
                } else if (displayType === 'file_link') {
                    const showSize = fieldEl.querySelector('.field-show-size')?.checked;
                    if (showSize) field.show_size = true;
                    const showIcon = fieldEl.querySelector('.field-show-icon')?.checked;
                    if (showIcon) field.show_icon = true;
                    const download = fieldEl.querySelector('.field-download')?.checked;
                    if (download) field.download = true;
                }

                displayFields.push(field);
            });
        });

        return {
            view: {
                columns: displayFields
            }
        };
    },

    async submit() {
        try {
            console.log('\n' + '='.repeat(60));
            console.log('[STEP4-SUBMIT] Step 4 제출 시작');
            console.log('='.repeat(60));

            const formData = this.getFormData();

            console.log('[STEP4-SUBMIT-1] form_data 수집 완료');
            console.log(`[STEP4-SUBMIT-2] 총 ${formData.view.columns.length}개 필드 준비됨`);

            formData.view.columns.forEach((field, idx) => {
                console.log(`[STEP4-SUBMIT-3-${idx}] 필드: ${field.name}`);
                console.log(`         - label: ${field.label}`);
                console.log(`         - display_type: ${field.display_type}`);
                console.log(`         - order: ${field.order}`);
                if (field.width) console.log(`         - width: ${field.width}`);
                if (field.inline_group) console.log(`         - inline_group: ${field.inline_group}`);
                if (field.full_width) console.log(`         - full_width: true`);
                if (field.style_class) console.log(`         - style_class: ${field.style_class}`);
                if (field.section_title) console.log(`         - section_title: ${field.section_title}`);
            });

            console.log('[STEP4-SUBMIT-4] JSON 전송 준비:');
            console.log(JSON.stringify(formData, null, 2));

            console.log(`[STEP4-SUBMIT-5] /boards/new/step4/${boardId}로 POST 요청 중...`);

            const response = await fetch(`/boards/new/step4/${boardId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            console.log(`[STEP4-SUBMIT-6] 응답 상태: ${response.status} ${response.statusText}`);

            const data = await response.json();
            console.log('[STEP4-SUBMIT-7] 응답 데이터:', data);

            if (!response.ok) {
                console.log(`[STEP4-SUBMIT-ERROR] 오류 응답: ${data.detail}`);
                alert('오류: ' + data.detail);
                return;
            }

            console.log('[STEP4-SUBMIT-8] ✓ 제출 성공');
            console.log(`[STEP4-SUBMIT-9] 리다이렉트: ${data.redirect}`);
            console.log('='.repeat(60));
            window.location.href = data.redirect;
        } catch (error) {
            console.error('[STEP4-SUBMIT-ERROR] 예외 발생:', error);
            console.error('[STEP4-SUBMIT-ERROR] 메시지:', error.message);
            console.error('[STEP4-SUBMIT-ERROR] 스택:', error.stack);
            alert('오류: ' + error.message);
        }
    }
};
