const wizardStep1 = {
    columnCount: 0,
    boardId: null,

    addColumn(data = null, isExisting = false) {
        this.columnCount++;
        const tbody = document.getElementById('columnsBody');
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';
        row.dataset.columnIndex = this.columnCount;
        row.dataset.isExisting = isExisting; // 기존 항목인지 표시

        // 데이터가 있으면 기존 값으로 채우기
        const label = data ? data.label : '';
        const dataType = data ? data.data_type : 'string';
        const comment = data ? (data.comment || '') : '';

        // 기존 항목이면 입력 비활성화
        const inputDisabled = isExisting ? 'disabled' : '';
        const selectDisabled = isExisting ? 'disabled' : '';

        // 기존 항목이 아닐 때만 삭제/이동 버튼 표시
        const actionButtons = isExisting ? '' : `
                <button type="button" onclick="wizardStep1.moveColumnUp(${this.columnCount})" class="px-2 py-1 text-indigo-600 hover:text-indigo-700 font-semibold text-sm hover:bg-indigo-50 rounded" title="위로">↑</button>
                <button type="button" onclick="wizardStep1.moveColumnDown(${this.columnCount})" class="px-2 py-1 text-indigo-600 hover:text-indigo-700 font-semibold text-sm hover:bg-indigo-50 rounded" title="아래로">↓</button>
                <button type="button" onclick="wizardStep1.removeColumn(${this.columnCount})" class="px-2 py-1 text-red-600 hover:text-red-700 font-semibold text-sm hover:bg-red-50 rounded" title="삭제">✕</button>
        `;

        row.innerHTML = `
            <td class="py-3 px-4 text-gray-500">${this.columnCount}</td>
            <td class="py-3 px-4">
                <input type="text" class="col-label w-full px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 outline-none" placeholder="예: 제목" value="${label}" ${inputDisabled}>
            </td>
            <td class="py-3 px-4">
                <select class="col-type w-full px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 outline-none text-sm" ${selectDisabled}>
                    <option value="string" ${dataType === 'string' ? 'selected' : ''}>문자열</option>
                    <option value="text" ${dataType === 'text' ? 'selected' : ''}>문장</option>
                    <option value="integer" ${dataType === 'integer' ? 'selected' : ''}>정수</option>
                    <option value="float" ${dataType === 'float' ? 'selected' : ''}>실수(소수점포함)</option>
                    <option value="boolean" ${dataType === 'boolean' ? 'selected' : ''}>참/거짓</option>
                    <option value="ymd" ${dataType === 'ymd' ? 'selected' : ''}>날짜</option>
                    <option value="datetime" ${dataType === 'datetime' ? 'selected' : ''}>날짜시간</option>
                </select>
            </td>
            <td class="py-3 px-4">
                <input type="text" class="col-comment w-full px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 outline-none" placeholder="예: 기준일자" value="${comment}" ${inputDisabled}>
            </td>
            <td class="py-3 px-4 text-center space-x-1 flex justify-center">
                ${actionButtons}
            </td>
        `;
        tbody.appendChild(row);
    },

    removeColumn(index) {
        const row = document.querySelector(`tr[data-column-index="${index}"]`);
        if (row) {
            row.remove();
        }
    },

    moveColumnUp(index) {
        const row = document.querySelector(`tr[data-column-index="${index}"]`);
        if (row && row.previousElementSibling) {
            row.parentNode.insertBefore(row, row.previousElementSibling);
        }
    },

    moveColumnDown(index) {
        const row = document.querySelector(`tr[data-column-index="${index}"]`);
        if (row && row.nextElementSibling) {
            row.parentNode.insertBefore(row.nextElementSibling, row);
        }
    },

    getFormData() {
        const boardName = document.getElementById('boardName').value.trim();
        const boardNote = document.getElementById('boardNote').value.trim();
        const isFileAttach = document.getElementById('isFileAttach').checked;

        if (!boardName) {
            alert('기록물 이름을 입력하세요.');
            return null;
        }

        const columns = [];
        document.querySelectorAll('#columnsBody tr').forEach(row => {
            const label = row.querySelector('.col-label').value.trim();
            const dataType = row.querySelector('.col-type').value;
            const comment = row.querySelector('.col-comment').value.trim();

            if (!label) {
                throw new Error('모든 항목의 라벨을 입력하세요.');
            }

            const columnData = {
                label,
                data_type: dataType
            };

            // comment는 선택사항이므로 있을 때만 추가
            if (comment) {
                columnData.comment = comment;
            }

            columns.push(columnData);
        });

        if (columns.length === 0) {
            alert('최소 1개 이상의 항목을 추가하세요.');
            return null;
        }

        const result = {
            name: boardName,
            note: boardNote,
            is_file_attach: isFileAttach,
            columns: columns
        };

        // 수정 모드인 경우 board_id 포함
        if (this.boardId) {
            result.board_id = this.boardId;
        }

        return result;
    },

    async submit() {
        try {
            const formData = this.getFormData();
            if (!formData) return;

            console.log('Submitting form data:', formData);

            const response = await fetch('/boards/new/step1', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);

            const responseText = await response.text();
            console.log('Response text:', responseText);

            let data;
            try {
                data = JSON.parse(responseText);
            } catch (parseError) {
                console.error('JSON parse error:', parseError);
                console.error('Response was:', responseText);
                alert('서버 응답 처리 오류: ' + responseText.substring(0, 200));
                return;
            }

            if (!response.ok) {
                alert('오류: ' + (data.detail || data.message || '알 수 없는 오류'));
                return;
            }

            window.location.href = data.redirect;
        } catch (error) {
            console.error('Fetch error:', error);
            alert('오류: ' + error.message);
        }
    }
};
