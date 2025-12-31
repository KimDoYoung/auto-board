// Variables from Jinja2 template are defined in the HTML inline script block
// Copy them to local scope for use in this module
const allColumns = window.allColumns || [];
const listConfig = window.listConfig || null;
const boardId = window.boardId || 0;

const wizardStep2 = {
    getFormData() {
        const displayColumns = Array.from(document.querySelectorAll('.display-column:checked'))
            .map(el => {
                const columnInfo = allColumns.find(col => col.name === el.value);
                return {
                    name: el.value,
                    label: columnInfo.label,
                    width: "auto",
                    align: "left",
                    sortable: true
                };
            });

        const simpleFields = Array.from(document.querySelectorAll('.search-simple-column:checked'))
            .map(el => el.value);

        return {
            list_config: {
                view_mode: document.querySelector('input[name="viewMode"]:checked').value,
                columns: displayColumns,
                pagination: {
                    enabled: document.getElementById('paginationEnabled').checked,
                    page_size: parseInt(document.getElementById('pageSize').value),
                    page_size_options: [10, 20, 50, 100]
                },
                default_sort: [
                    {
                        column: document.getElementById('sortColumn').value,
                        order: document.getElementById('sortOrder').value
                    }
                ],
                search: {
                    enabled: document.getElementById('searchEnabled').checked,
                    mode: "simple",
                    simple_fields: simpleFields,
                    show_toggle: true
                },
                actions: {
                    show_edit: true,
                    show_delete: true,
                    show_detail: true
                }
            }
        };
    },

    async submit() {
        try {
            const formData = this.getFormData();

            if (formData.list_config.columns.length === 0) {
                alert('최소 1개 이상의 표시 항목을 선택하세요.');
                return;
            }

            console.log('Submitting form data:', formData);

            const response = await fetch(`/boards/new/step2/${boardId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (!response.ok) {
                alert('오류: ' + (data.detail || '알 수 없는 오류'));
                return;
            }

            window.location.href = data.redirect;
        } catch (error) {
            console.error('Error:', error);
            alert('오류: ' + error.message);
        }
    }
};

// Setup toggle handlers
document.getElementById('paginationEnabled').addEventListener('change', (e) => {
    const element = document.getElementById('paginationSettings');
    if (!e.target.checked) {
        element.classList.add('opacity-50', 'pointer-events-none');
    } else {
        element.classList.remove('opacity-50', 'pointer-events-none');
    }
});

document.getElementById('searchEnabled').addEventListener('change', (e) => {
    const element = document.getElementById('searchSettings');
    if (!e.target.checked) {
        element.classList.add('opacity-50', 'pointer-events-none');
    } else {
        element.classList.remove('opacity-50', 'pointer-events-none');
    }
});

// Initialize with existing config if available
// Disabled - initialization now handled by step2.html DOMContentLoaded
/*
document.addEventListener('DOMContentLoaded', () => {
    if (listConfig) {
        // [1] 표시 방식 설정
        document.querySelector(`input[name="viewMode"][value="${listConfig.view_mode}"]`).checked = true;

        // [2] 표시 항목 선택
        const displayColumns = listConfig.columns || listConfig.display_columns || [];
        const displayColumnNames = displayColumns.map(col => col.name);
        document.querySelectorAll('.display-column').forEach(checkbox => {
            checkbox.checked = displayColumnNames.includes(checkbox.value);
        });

        // [3] 페이지네이션 설정
        if (listConfig.pagination) {
            document.getElementById('paginationEnabled').checked = listConfig.pagination.enabled;
            if (listConfig.pagination.page_size) {
                document.getElementById('pageSize').value = listConfig.pagination.page_size;
            }
        }

        // [4] 기본 정렬 설정
        if (listConfig.default_sort && listConfig.default_sort.length > 0) {
            const firstSort = listConfig.default_sort[0];
            document.getElementById('sortColumn').value = firstSort.column;
            document.getElementById('sortOrder').value = firstSort.order;
        }

        // [5] 검색 설정
        if (listConfig.search) {
            document.getElementById('searchEnabled').checked = listConfig.search.enabled;
            if (listConfig.search.simple_fields) {
                const searchFields = listConfig.search.simple_fields;
                document.querySelectorAll('.search-simple-column').forEach(checkbox => {
                    checkbox.checked = searchFields.includes(checkbox.value);
                });
            }
        }

        // 토글 상태 동기화
        const paginationElement = document.getElementById('paginationSettings');
        if (!document.getElementById('paginationEnabled').checked) {
            paginationElement.classList.add('opacity-50', 'pointer-events-none');
        } else {
            paginationElement.classList.remove('opacity-50', 'pointer-events-none');
        }

        const searchElement = document.getElementById('searchSettings');
        if (!document.getElementById('searchEnabled').checked) {
            searchElement.classList.add('opacity-50', 'pointer-events-none');
        } else {
            searchElement.classList.remove('opacity-50', 'pointer-events-none');
        }
    }
});
*/
