/**
 * Records Manager
 * Handles logic for Create, Edit, View, and List pages for Auto-Board records.
 */

const Records = {
    /**
     * Common Utilities
     */
    Utils: {
        // Helper to sync Quill content to hidden input
        syncQuillToInput: function (editors) {
            for (const [fieldName, editor] of Object.entries(editors)) {
                const hiddenInput = document.getElementById('hidden-' + fieldName);
                if (hiddenInput) {
                    // Check if editor is empty (Quill leaves <p><br></p>)
                    if (editor.getText().trim().length === 0 && editor.root.innerHTML === '<p><br></p>') {
                        hiddenInput.value = '';
                    } else {
                        hiddenInput.value = editor.root.innerHTML;
                    }
                }
            }
        },

        // Helper to handle form submission with JSON body
        submitJsonForm: async function (url, method, data, successMessage) {
            try {
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    const result = await response.json();
                    alert(successMessage);
                    window.location.href = result.redirect;
                } else {
                    alert('저장 실패: ' + response.statusText);
                }
            } catch (error) {
                alert('오류가 발생했습니다: ' + error);
            }
        },

        // Helper for deletion
        deleteRecord: function (boardId, recordId, redirectUrl) {
            if (confirm('이 기록을 삭제하시겠습니까?')) {
                fetch(`/records/api/${boardId}/${recordId}`, {
                    method: 'DELETE'
                })
                    .then(response => {
                        if (response.ok) {
                            alert('기록이 삭제되었습니다.');
                            if (redirectUrl === 'reload') {
                                location.reload();
                            } else {
                                window.location.href = redirectUrl;
                            }
                        } else {
                            alert('삭제 실패: ' + response.statusText);
                        }
                    })
                    .catch(error => {
                        alert('오류가 발생했습니다: ' + error);
                    });
            }
        }
    },

    /**
     * Module: Create
     * Handles logic for create.html
     */
    Create: {
        editors: {},
        editorConfig: {
            theme: 'snow',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ 'color': [] }, { 'background': [] }],
                    [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                    ['link', 'image', 'clean']
                ]
            }
        },

        init: function (boardId, fieldsConfig) {
            // Initialize Quill Editors for 'html_editor' fields
            if (fieldsConfig && Array.isArray(fieldsConfig)) {
                fieldsConfig.forEach(field => {
                    if (field.element_type === 'html_editor') {
                        this.editors[field.name] = new Quill('#editor-' + field.name, this.editorConfig);
                    }
                });
            }

            // Bind Form Submit
            const form = document.getElementById('createForm');
            if (form) {
                form.addEventListener('submit', (e) => this.handleSubmit(e, boardId));
            }
        },

        handleSubmit: async function (e, boardId) {
            e.preventDefault();

            // Sync editors
            Records.Utils.syncQuillToInput(this.editors);

            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);

            // Remove 'files' from JSON data as we don't support it in JSON API yet
            delete data.files;

            await Records.Utils.submitJsonForm(
                `/records/api/${boardId}/`,
                'POST',
                data,
                '기록이 생성되었습니다.'
            );
        }
    },

    /**
     * Module: Edit
     * Handles logic for edit.html
     */
    Edit: {
        init: function (boardId, recordId) {
            const form = document.getElementById('editForm');
            if (form) {
                form.addEventListener('submit', (e) => this.handleSubmit(e, boardId, recordId));
            }
        },

        handleSubmit: async function (e, boardId, recordId) {
            e.preventDefault();

            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);

            await Records.Utils.submitJsonForm(
                `/records/api/${boardId}/${recordId}`,
                'PUT',
                data,
                '기록이 수정되었습니다.'
            );
        }
    },

    /**
     * Module: View & List
     * Handles shared logic like deletion for view.html and list.html
     */
    Actions: {
        delete: function (boardId, recordId, fromList = false) {
            // If deleting from list, reload page. If from view, redirect to list.
            const redirectUrl = fromList ? 'reload' : `/records/${boardId}/`;
            Records.Utils.deleteRecord(boardId, recordId, redirectUrl);
        }
    }
};
