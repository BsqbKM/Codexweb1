module.exports = {
  parser: "@typescript-eslint/parser",
  extends: ["eslint:recommended", "plugin:react/recommended", "plugin:react/jsx-runtime", "prettier"],
  plugins: ["react", "@typescript-eslint"],
  env: {
    browser: true,
    es2021: true
  },
  settings: {
    react: {
      version: "detect"
    }
  },
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module"
  },
  rules: {}
};
