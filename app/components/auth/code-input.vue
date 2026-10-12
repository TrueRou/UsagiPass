<script setup lang="ts">
const props = withDefaults(defineProps<{
    length?: number
    invalid?: boolean
    disabled?: boolean
    autofocus?: boolean
}>(), {
    length: 6,
})

const model = defineModel<string>({ required: true })

const NON_DIGIT_RE = /\D/g
const inputs = ref<HTMLInputElement[]>([])

function focusAt(i: number) {
    inputs.value[Math.max(0, Math.min(props.length - 1, i))]?.focus()
}

/** 返回写入后的新值（v-model 回写是异步的，调用方不要立即读 model） */
function setAt(i: number, digit: string): string {
    const chars = model.value.split('')
    if (!digit)
        chars.splice(i, 1)
    else if (i >= chars.length)
        chars.push(digit)
    else
        chars[i] = digit
    const next = chars.join('')
    model.value = next
    return next
}

function onInput(i: number, event: Event) {
    const target = event.target as HTMLInputElement
    const digits = target.value.replace(NON_DIGIT_RE, '')
    if (!digits) {
        setAt(i, '')
        target.value = ''
        return
    }
    if (digits.length > 1) {
        const next = (model.value.slice(0, i) + digits).slice(0, props.length)
        model.value = next
        focusAt(next.length)
        return
    }
    const pos = Math.min(i, model.value.length)
    const next = setAt(i, digits)
    // 点到靠后空格输入时数字会补到首个空位，需同步当前格显示
    target.value = next[i] ?? ''
    focusAt(pos + 1)
}

function onKeydown(i: number, event: KeyboardEvent) {
    if (event.key === 'Backspace' && !model.value[i] && i > 0) {
        event.preventDefault()
        setAt(i - 1, '')
        focusAt(i - 1)
    }
    else if (event.key === 'ArrowLeft') {
        focusAt(i - 1)
    }
    else if (event.key === 'ArrowRight') {
        focusAt(i + 1)
    }
}

function onPaste(event: ClipboardEvent) {
    const digits = (event.clipboardData?.getData('text') ?? '').replace(NON_DIGIT_RE, '').slice(0, props.length)
    if (!digits)
        return
    event.preventDefault()
    model.value = digits
    focusAt(digits.length)
}

// 挂载及提交失败（重新启用且已清空）时聚焦首格
watch(() => props.disabled, (disabled) => {
    if (props.autofocus && !disabled && !model.value)
        nextTick(() => focusAt(0))
})

onMounted(() => {
    if (props.autofocus)
        focusAt(0)
})
</script>

<template>
    <div class="flex justify-between gap-2 sm:gap-3">
        <input
            v-for="(_, i) in length"
            :key="i"
            ref="inputs"
            type="text"
            inputmode="numeric"
            :autocomplete="i === 0 ? 'one-time-code' : 'off'"
            :maxlength="length"
            :aria-label="`验证码第 ${i + 1} 位`"
            :value="model[i] ?? ''"
            :disabled="disabled"
            class="input input-bordered w-full aspect-square h-auto max-w-14 p-0 text-center font-mono text-2xl font-semibold"
            :class="{ 'input-error': invalid, 'input-primary': !invalid && model[i] }"
            @input="onInput(i, $event)"
            @keydown="onKeydown(i, $event)"
            @paste="onPaste"
            @focus="($event.target as HTMLInputElement).select()"
        >
    </div>
</template>
