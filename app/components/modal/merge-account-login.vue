<script setup lang="ts">
import { z } from 'zod'

interface MergeLoginPayload {
    username: string
    password: string
    strategy: AuthStrategy
}

interface MergeLoginEmits {
    (event: 'update:open', value: boolean): void
    (event: 'confirm', payload: MergeLoginPayload): void
}

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<MergeLoginEmits>()

const strategyOptions: Array<{ label: string, value: AuthStrategy, description: string }> = [
    { label: 'UsagiCard（兔卡）账号', value: AuthStrategy.LOCAL, description: '使用 UsagiCard 兔卡旧账号' },
    { label: '水鱼旧账号', value: AuthStrategy.DIVING_FISH, description: '使用水鱼查分器旧账号' },
    { label: '落雪旧账号', value: AuthStrategy.LXNS, description: '使用落雪查分器旧账号' },
]

const form = reactive({
    username: '',
    password: '',
    strategy: AuthStrategy.LOCAL,
})

const schema = z.object({
    username: z.string().min(1, '用户名不能为空'),
    password: z.string().min(1, '密码不能为空'),
    strategy: z.number(),
})

const { validate, ve, clearErrors } = useFormValidation(schema, form)

watch(() => props.open, (open) => {
    if (open) {
        form.username = ''
        form.password = ''
        form.strategy = AuthStrategy.LOCAL
        clearErrors()
    }
}, { immediate: true })

function handleConfirm() {
    if (!validate())
        return
    emit('confirm', { ...form })
}
</script>

<template>
    <div v-if="props.open" class="modal modal-open">
        <div class="modal-box space-y-4">
            <div class="space-y-1">
                <p class="text-xs uppercase tracking-[0.3em] text-primary">
                    其他账号
                </p>
                <h3 class="text-xl font-semibold">
                    登录需要合并的账号
                </h3>
                <p class="text-sm text-base-content/70">
                    使用需要合并的账号登录，其凭证仅用于本次迁移。
                </p>
            </div>

            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-1">用户名</label>
                    <input
                        v-model="form.username" class="input input-bordered w-full" type="text"
                        :class="{ 'input-error': ve('username') }" placeholder="输入用户名"
                    >
                    <p v-if="ve('username')" class="text-error text-xs mt-1">
                        {{ ve('username') }}
                    </p>
                </div>

                <div>
                    <label class="block text-sm font-medium mb-1">密码</label>
                    <input
                        v-model="form.password" class="input input-bordered w-full" type="password"
                        :class="{ 'input-error': ve('password') }" placeholder="输入密码"
                    >
                    <p v-if="ve('password')" class="text-error text-xs mt-1">
                        {{ ve('password') }}
                    </p>
                </div>

                <div>
                    <label class="block text-sm font-medium mb-2">登录策略</label>
                    <div class="space-y-2">
                        <label
                            v-for="option in strategyOptions" :key="option.value" class="flex items-center gap-3 rounded-box border border-base-200 px-3 py-2"
                        >
                            <input
                                v-model="form.strategy" class="radio radio-primary" type="radio" :value="option.value"
                            >
                            <div>
                                <p class="text-sm font-medium">
                                    {{ option.label }}
                                </p>
                                <p class="text-xs text-base-content/70">
                                    {{ option.description }}
                                </p>
                            </div>
                        </label>
                    </div>
                </div>
            </div>

            <div class="modal-action">
                <button class="btn btn-ghost" type="button" @click="emit('update:open', false)">
                    取消
                </button>
                <button class="btn btn-primary" type="button" @click="handleConfirm">
                    继续
                </button>
            </div>
        </div>
        <div class="modal-backdrop" @click="emit('update:open', false)">
            取消
        </div>
    </div>
</template>
