const {
    validateField,
    validateBoardBasics,
    validateFields,
    checkDuplicateNames,
    buildBoardData,
    validateCreateBoardResponse
} = require('../app/static/js/board_manager_logic.js');

describe('Board Manager Logic', () => {
    // ===== validateField Tests =====
    describe('validateField', () => {
        it('should validate a correct field', () => {
            const field = {
                label: '제목',
                name: 'title',
                data_type: 'string',
                required: true
            };
            const result = validateField(field);
            expect(result.valid).toBe(true);
            expect(result.error).toBe(null);
        });

        it('should reject field with empty label', () => {
            const field = {
                label: '',
                name: 'title',
                data_type: 'string',
                required: true
            };
            const result = validateField(field);
            expect(result.valid).toBe(false);
            expect(result.error).toBe('Column label is required');
        });

        it('should reject field with whitespace-only label', () => {
            const field = {
                label: '   ',
                name: 'title',
                data_type: 'string',
                required: true
            };
            const result = validateField(field);
            expect(result.valid).toBe(false);
            expect(result.error).toBe('Column label is required');
        });

        it('should reject field with empty name', () => {
            const field = {
                label: '제목',
                name: '',
                data_type: 'string',
                required: true
            };
            const result = validateField(field);
            expect(result.valid).toBe(false);
            expect(result.error).toBe('Column name is required');
        });

        it('should reject field with missing data_type', () => {
            const field = {
                label: '제목',
                name: 'title',
                data_type: '',
                required: true
            };
            const result = validateField(field);
            expect(result.valid).toBe(false);
            expect(result.error).toBe('Column data type is required');
        });
    });

    // ===== validateBoardBasics Tests =====
    describe('validateBoardBasics', () => {
        it('should validate correct board basics', () => {
            const result = validateBoardBasics('보드이름', 'table_1');
            expect(result.valid).toBe(true);
            expect(result.error).toBe(null);
        });

        it('should reject empty board name', () => {
            const result = validateBoardBasics('', 'table_1');
            expect(result.valid).toBe(false);
            expect(result.error).toBe('기록물 이름은 필수입니다.');
        });

        it('should reject empty table name', () => {
            const result = validateBoardBasics('보드이름', '');
            expect(result.valid).toBe(false);
            expect(result.error).toBe('물리 테이블 이름은 필수입니다.');
        });

        it('should reject whitespace-only board name', () => {
            const result = validateBoardBasics('  ', 'table_1');
            expect(result.valid).toBe(false);
            expect(result.error).toBe('기록물 이름은 필수입니다.');
        });
    });

    // ===== validateFields Tests =====
    describe('validateFields', () => {
        it('should validate multiple correct fields', () => {
            const fields = [
                { label: '제목', name: 'title', data_type: 'string', required: true },
                { label: '내용', name: 'content', data_type: 'text', required: false }
            ];
            const result = validateFields(fields);
            expect(result.valid).toBe(true);
            expect(result.error).toBe(null);
        });

        it('should reject non-array fields', () => {
            const result = validateFields('not an array');
            expect(result.valid).toBe(false);
            expect(result.error).toBe('Fields must be an array');
        });

        it('should reject empty array', () => {
            const result = validateFields([]);
            expect(result.valid).toBe(false);
            expect(result.error).toBe('At least one field is required');
        });

        it('should reject fields with invalid field', () => {
            const fields = [
                { label: '제목', name: 'title', data_type: 'string', required: true },
                { label: '', name: 'invalid', data_type: 'string', required: false }
            ];
            const result = validateFields(fields);
            expect(result.valid).toBe(false);
            expect(result.error).toBe('Column label is required');
        });
    });

    // ===== checkDuplicateNames Tests =====
    describe('checkDuplicateNames', () => {
        it('should detect no duplicates in unique names', () => {
            const fields = [
                { name: 'title' },
                { name: 'content' },
                { name: 'author' }
            ];
            const result = checkDuplicateNames(fields);
            expect(result.hasDuplicates).toBe(false);
            expect(result.duplicates).toEqual([]);
        });

        it('should detect duplicate names', () => {
            const fields = [
                { name: 'title' },
                { name: 'content' },
                { name: 'title' }
            ];
            const result = checkDuplicateNames(fields);
            expect(result.hasDuplicates).toBe(true);
            expect(result.duplicates).toContain('title');
        });

        it('should be case-insensitive when checking duplicates', () => {
            const fields = [
                { name: 'Title' },
                { name: 'content' },
                { name: 'TITLE' }
            ];
            const result = checkDuplicateNames(fields);
            expect(result.hasDuplicates).toBe(true);
            expect(result.duplicates).toContain('title');
        });

        it('should detect multiple duplicate groups', () => {
            const fields = [
                { name: 'title' },
                { name: 'content' },
                { name: 'title' },
                { name: 'content' }
            ];
            const result = checkDuplicateNames(fields);
            expect(result.hasDuplicates).toBe(true);
            expect(result.duplicates).toContain('title');
            expect(result.duplicates).toContain('content');
        });
    });

    // ===== buildBoardData Tests =====
    describe('buildBoardData', () => {
        it('should build valid board data', () => {
            const params = {
                boardName: '일기',
                tableName: 'diary_table',
                note: '개인 일기장',
                fields: [
                    { label: '제목', name: 'title', data_type: 'string', required: true },
                    { label: '내용', name: 'content', data_type: 'text', required: false }
                ]
            };
            const result = buildBoardData(params);
            expect(result.success).toBe(true);
            expect(result.error).toBe(null);
            expect(result.data.board.name).toBe('일기');
            expect(result.data.board.physical_table_name).toBe('diary_table');
            expect(result.data.columns.fields).toHaveLength(2);
        });

        it('should reject data with missing board name', () => {
            const params = {
                boardName: '',
                tableName: 'diary_table',
                note: '개인 일기장',
                fields: [
                    { label: '제목', name: 'title', data_type: 'string', required: true }
                ]
            };
            const result = buildBoardData(params);
            expect(result.success).toBe(false);
            expect(result.error).toBe('기록물 이름은 필수입니다.');
        });

        it('should reject data with invalid fields', () => {
            const params = {
                boardName: '일기',
                tableName: 'diary_table',
                note: '개인 일기장',
                fields: [
                    { label: '', name: 'title', data_type: 'string', required: true }
                ]
            };
            const result = buildBoardData(params);
            expect(result.success).toBe(false);
            expect(result.error).toBe('Column label is required');
        });

        it('should reject data with duplicate field names', () => {
            const params = {
                boardName: '일기',
                tableName: 'diary_table',
                note: '개인 일기장',
                fields: [
                    { label: '제목', name: 'title', data_type: 'string', required: true },
                    { label: '다른제목', name: 'title', data_type: 'text', required: false }
                ]
            };
            const result = buildBoardData(params);
            expect(result.success).toBe(false);
            expect(result.error).toContain('Duplicate column names');
            expect(result.error).toContain('title');
        });

        it('should trim whitespace from board data', () => {
            const params = {
                boardName: '  일기  ',
                tableName: '  diary_table  ',
                note: '  개인 일기장  ',
                fields: [
                    { label: '제목', name: 'title', data_type: 'string', required: true }
                ]
            };
            const result = buildBoardData(params);
            expect(result.success).toBe(true);
            expect(result.data.board.name).toBe('일기');
            expect(result.data.board.physical_table_name).toBe('diary_table');
            expect(result.data.board.note).toBe('개인 일기장');
        });
    });

    // ===== validateCreateBoardResponse Tests =====
    describe('validateCreateBoardResponse', () => {
        it('should validate correct response', () => {
            const response = {
                message: 'success',
                board_id: 1
            };
            const result = validateCreateBoardResponse(response);
            expect(result.success).toBe(true);
            expect(result.boardId).toBe(1);
            expect(result.error).toBe(null);
        });

        it('should reject null response', () => {
            const result = validateCreateBoardResponse(null);
            expect(result.success).toBe(false);
            expect(result.error).toBe('Invalid response format');
        });

        it('should reject response with wrong message', () => {
            const response = {
                message: 'error',
                error_details: 'Database error'
            };
            const result = validateCreateBoardResponse(response);
            expect(result.success).toBe(false);
            expect(result.error).toBe('error');
        });

        it('should reject response without board_id', () => {
            const response = {
                message: 'success'
            };
            const result = validateCreateBoardResponse(response);
            expect(result.success).toBe(false);
            expect(result.error).toBe('Invalid board_id in response');
        });

        it('should reject response with invalid board_id type', () => {
            const response = {
                message: 'success',
                board_id: 'not-a-number'
            };
            const result = validateCreateBoardResponse(response);
            expect(result.success).toBe(false);
            expect(result.error).toBe('Invalid board_id in response');
        });
    });
});
