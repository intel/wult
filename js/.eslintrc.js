module.exports = {
  env: {
    browser: true,
    es2021: true,
    commonjs: true
  },
  parser: '@babel/eslint-parser',
  extends: [
    'standard',
    'plugin:wc/recommended',
    'plugin:lit/recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
  },
  settings: {
    wc: {
      elementBaseClasses: ['LitElement']
    }
  }
}
