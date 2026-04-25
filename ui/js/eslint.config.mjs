import js from '@eslint/js';
import { fixupPluginRules } from '@eslint/compat';
import tsPlugin from '@typescript-eslint/eslint-plugin';
import reactPlugin from 'eslint-plugin-react';
import importPlugin from 'eslint-plugin-import';
import storybookPlugin from 'eslint-plugin-storybook';
import globals from 'globals';

export default [
  {
    ignores: [
      'app.config.js',
      'babel.config.js',
      'jest.config.js',
      'metro.config.js',
      'src/jestSetup.js',
      '**/__mocks__/**/*.js',
      'storybook-static',
      '.expo',
    ],
  },
  js.configs.recommended,
  ...tsPlugin.configs['flat/recommended'],
  {
    plugins: { react: fixupPluginRules(reactPlugin) },
    rules: reactPlugin.configs.recommended.rules,
  },
  ...storybookPlugin.configs['flat/recommended'],
  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2021,
      },
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    plugins: {
      import: importPlugin,
    },
    rules: {
      'import/order': 'error',
      'react/react-in-jsx-scope': 'off',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
    settings: {
      react: { version: 'detect' },
    },
  },
  {
    files: ['.storybook/snapshot-serializer.js'],
    languageOptions: {
      sourceType: 'commonjs',
      globals: { ...globals.node },
    },
    rules: {
      '@typescript-eslint/no-require-imports': 'off',
    },
  },
];
