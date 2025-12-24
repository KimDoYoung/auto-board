module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/tests_js/**/*.test.js'],
  transform: {},
  collectCoverageFrom: [
    'app/static/js/**/*.js',
    '!app/static/js/**/*.test.js',
  ],
};
