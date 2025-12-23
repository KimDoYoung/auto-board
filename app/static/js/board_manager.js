const boardManager = {
    rowCount: 0,
    createdBoardId: null,

    init: function () {
        // Add default columns if table is empty
        if (document.querySelector('#columnsTable tbody').children.length === 0) {
            // Default: Title
            this.addColumnRow({ label: '제목', name: 'title', type: 'string', required: true });
            // Default: Content
            this.addColumnRow({ label: '내용', name: 'content', type: 'text', required: false });
        }
    },

    addColumnRow: function (data = null) {
        this.rowCount++;
        const tbody = document.querySelector('#columnsTable tbody');
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50 group border-b last:border-0';

        const label = data ? data.label : '';
        const name = data ? data.name : '';
        const type = data ? data.type : 'string';
        const required = data ? data.required : false;

        tr.innerHTML = `
            <td class="py-3 px-2 text-center text-gray-400">${this.rowCount}</td>
            <td class="py-3 px-2"><input type="text" name="label" value="${label}" class="w-full px-2 py-1 border rounded focus:ring-1 focus:ring-indigo-500 outline-none" placeholder="제목"></td>
            <td class="py-3 px-2"><input type="text" name="name" value="${name}" class="w-full px-2 py-1 border rounded focus:ring-1 focus:ring-indigo-500 outline-none" placeholder="title"></td>
            <td class="py-3 px-2">
                <select name="type" class="w-full px-2 py-1 border rounded outline-none bg-white">
                    <option value="string" ${type === 'string' ? 'selected' : ''}>String (단문)</option>
                    <option value="text" ${type === 'text' ? 'selected' : ''}>Text (장문)</option>
                    <option value="integer" ${type === 'integer' ? 'selected' : ''}>Integer (정수)</option>
                    <option value="float" ${type === 'float' ? 'selected' : ''}>Float (실수)</option>
                    <option value="boolean" ${type === 'boolean' ? 'selected' : ''}>Boolean (Y/N)</option>
                    <option value="datetime" ${type === 'datetime' ? 'selected' : ''}>Date/Time</option>
                    <option value="ymd" ${type === 'ymd' ? 'selected' : ''}>YMD (날짜)</option>
                </select>
            </td>
            <td class="py-3 px-2 text-center">
                <input type="checkbox" name="required" ${required ? 'checked' : ''} class="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500">
            </td>
            <td class="py-3 px-2 text-center">
                <button onclick="this.closest('tr').remove()" class="text-gray-400 hover:text-red-500 p-1 rounded hover:bg-red-50 transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
            </td>
            <td class="py-3 px-2 text-center">
                <div class="flex justify-center gap-1">
                    <button class="text-gray-400 hover:text-indigo-600 p-1" onclick="boardManager.moveRow(this, -1)">▲</button>
                    <button class="text-gray-400 hover:text-indigo-600 p-1" onclick="boardManager.moveRow(this, 1)">▼</button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    },

    moveRow: function (btn, direction) {
        const row = btn.closest('tr');
        const tbody = row.parentNode;
        if (direction === -1 && row.previousElementSibling) {
            tbody.insertBefore(row, row.previousElementSibling);
        } else if (direction === 1 && row.nextElementSibling) {
            tbody.insertBefore(row.nextElementSibling, row);
        }
    },

    collectData: function () {
        const name = document.getElementById('boardName').value;
        const physical_table_name = document.getElementById('tableName').value;
        const note = document.getElementById('boardNote').value;

        if (!name || !physical_table_name) {
            alert('기록물 이름과 물리 테이블 이름은 필수입니다.');
            return null;
        }

        const fields = [];
        document.querySelectorAll('#columnsTable tbody tr').forEach(tr => {
            fields.push({
                label: tr.querySelector('input[name="label"]').value,
                name: tr.querySelector('input[name="name"]').value,
                data_type: tr.querySelector('select[name="type"]').value,
                required: tr.querySelector('input[name="required"]').checked
            });
        });

        // Validation for fields
        for (let f of fields) {
            if (!f.label || !f.name) {
                alert('모든 컬럼의 라벨과 이름을 입력해주세요.');
                return null;
            }
        }

        return {
            board: {
                name: name,
                physical_table_name: physical_table_name,
                note: note
            },
            columns: {
                fields: fields
            }
        };
    },

    createBoard: function () {
        const data = this.collectData();
        if (!data) return;

        fetch('/boards/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
            .then(async response => {
                if (!response.ok) {
                    const errorText = await response.text();
                    console.error("Server Error:", response.status, errorText);
                    throw new Error(`Network response was not ok: ${response.status} ${errorText}`);
                }
                return response.json();
            })
            .then(result => {
                if (result.message === "success") {
                    this.createdBoardId = result.board_id;
                    alert('기록물이 성공적으로 생성되었습니다! (ID: ' + this.createdBoardId + ')');
                    this.onCreationSuccess();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('생성 중 오류가 발생했습니다.');
            });
    },

    onCreationSuccess: function () {
        // Disable inputs
        document.getElementById('boardName').disabled = true;
        document.getElementById('tableName').disabled = true;
        document.getElementById('boardNote').disabled = true;

        // Show View Config Section
        const viewSection = document.getElementById('viewConfigSection');
        viewSection.classList.remove('hidden');

        // Fetch fresh columns logic could go here to populate config UIs
        this.fetchColumns(this.createdBoardId);
    },

    fetchColumns: function (boardId) {
        fetch(`/boards/${boardId}/columns`)
            .then(res => res.json())
            .then(data => {
                console.log("Fetched columns:", data);
                // Here you would populate the List/Edit/View config UIs with these columns
            });
    },

    toggleConfig: function (type) {
        ['list', 'edit', 'view'].forEach(t => {
            document.getElementById(`${t}_div`).classList.add('hidden');
        });
        document.getElementById(`${type}_div`).classList.remove('hidden');
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    boardManager.init();
});
