// @ts-check
import antfu from '@antfu/eslint-config'
import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt(
    antfu({
        rules: {
            'node/prefer-global/process': ['off'],
            'node/prefer-global/buffer': ['off'],
        },
        stylistic: {
            indent: 4, // 4, or 'tab'
            quotes: 'single', // or 'double'
        },
    }),
)
