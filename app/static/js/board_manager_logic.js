/**
 * Pure logic functions for board management (testable, no DOM dependency)
 */

/**
 * Validate column field
 * @param {Object} field - Field to validate { label, name, data_type, required }
 * @returns {Object} { valid: boolean, error: string }
 */
function validateField(field) {
    if (!field.label || !field.label.trim()) {
        return { valid: false, error: 'Column label is required' };
    }
    if (!field.name || !field.name.trim()) {
        return { valid: false, error: 'Column name is required' };
    }
    if (!field.data_type) {
        return { valid: false, error: 'Column data type is required' };
    }
    return { valid: true, error: null };
}

/**
 * Validate board name and table name
 * @param {string} boardName - Board name
 * @param {string} tableName - Physical table name
 * @returns {Object} { valid: boolean, error: string }
 */
function validateBoardBasics(boardName, tableName) {
    if (!boardName || !boardName.trim()) {
        return { valid: false, error: '기록물 이름은 필수입니다.' };
    }
    if (!tableName || !tableName.trim()) {
        return { valid: false, error: '물리 테이블 이름은 필수입니다.' };
    }
    return { valid: true, error: null };
}

/**
 * Validate all fields
 * @param {Array} fields - Array of fields
 * @returns {Object} { valid: boolean, error: string }
 */
function validateFields(fields) {
    if (!Array.isArray(fields)) {
        return { valid: false, error: 'Fields must be an array' };
    }
    if (fields.length === 0) {
        return { valid: false, error: 'At least one field is required' };
    }

    for (let field of fields) {
        const validation = validateField(field);
        if (!validation.valid) {
            return validation;
        }
    }

    return { valid: true, error: null };
}

/**
 * Check for duplicate column names
 * @param {Array} fields - Array of fields
 * @returns {Object} { hasDuplicates: boolean, duplicates: string[] }
 */
function checkDuplicateNames(fields) {
    const names = fields.map(f => f.name.trim().toLowerCase());
    const seen = new Set();
    const duplicates = [];

    for (let name of names) {
        if (seen.has(name)) {
            if (!duplicates.includes(name)) {
                duplicates.push(name);
            }
        } else {
            seen.add(name);
        }
    }

    return {
        hasDuplicates: duplicates.length > 0,
        duplicates: duplicates
    };
}

/**
 * Build board creation data
 * @param {Object} params - { boardName, tableName, note, fields }
 * @returns {Object|null} Board creation data or null if invalid
 */
function buildBoardData(params) {
    const { boardName, tableName, note, fields } = params;

    // Validate basics
    const basicsValidation = validateBoardBasics(boardName, tableName);
    if (!basicsValidation.valid) {
        return { success: false, error: basicsValidation.error };
    }

    // Validate fields
    const fieldsValidation = validateFields(fields);
    if (!fieldsValidation.valid) {
        return { success: false, error: fieldsValidation.error };
    }

    // Check duplicates
    const duplicates = checkDuplicateNames(fields);
    if (duplicates.hasDuplicates) {
        return {
            success: false,
            error: `Duplicate column names: ${duplicates.duplicates.join(', ')}`
        };
    }

    return {
        success: true,
        error: null,
        data: {
            board: {
                name: boardName.trim(),
                physical_table_name: tableName.trim(),
                note: note.trim()
            },
            columns: {
                fields: fields
            }
        }
    };
}

/**
 * Validate API response
 * @param {Object} response - Response object
 * @returns {Object} { success: boolean, boardId: number|null, error: string|null }
 */
function validateCreateBoardResponse(response) {
    if (!response || typeof response !== 'object') {
        return { success: false, boardId: null, error: 'Invalid response format' };
    }
    if (response.message !== 'success') {
        return { success: false, boardId: null, error: response.message || 'Unknown error' };
    }
    if (!response.board_id || typeof response.board_id !== 'number') {
        return { success: false, boardId: null, error: 'Invalid board_id in response' };
    }
    return { success: true, boardId: response.board_id, error: null };
}

// Export for CommonJS
module.exports = {
    validateField,
    validateBoardBasics,
    validateFields,
    checkDuplicateNames,
    buildBoardData,
    validateCreateBoardResponse
};
