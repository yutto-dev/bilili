module.exports = {
  env: {
    browser: true,
    es6: true,
    node: true
  },
  extends: [
    "plugin:vue/base",
    "plugin:vue/essential",
    "plugin:vue/strongly-recommended",
    "plugin:vue/recommended"
  ],
  globals: {
    Atomics: "readonly",
    SharedArrayBuffer: "readonly"
  },
  parserOptions: {
    ecmaVersion: 2018,
    sourceType: "module"
  },
  plugins: ["vue"],
  rules: {
    semi: [2, "never"],
    "no-console": process.env.NODE_ENV === "production" ? "error" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",
    "vue/no-v-html": "off",
    "vue/array-bracket-spacing": "error",
    "vue/arrow-spacing": "error",
    "vue/block-spacing": "error",
    "vue/camelcase": "error",
    "vue/comma-dangle": "error",
    "vue/component-name-in-template-casing": [
      "error",
      "kebab-case",
      {
        registeredComponentsOnly: true,
        ignores: []
      }
    ],
    "vue/eqeqeq": "error",
    "vue/key-spacing": "error",
    "vue/match-component-file-name": [
      "error",
      {
        extensions: ["jsx"],
        shouldMatchCase: false
      }
    ],
    "vue/no-restricted-syntax": "error",
    "vue/object-curly-spacing": "error",
    "vue/require-direct-export": "error",
    "vue/space-infix-ops": "error",
    "vue/space-unary-ops": "error",
    "vue/v-on-function-call": ["error", "never"]
  }
};
