<script setup lang="ts">
definePageMeta({ middleware: 'require-login' })
useHead({
    title: '管理员设置 - UsagiPass',
})

const { $leporid } = useNuxtApp()
const { user } = useUserSession()

const { data: maimaiVersionMetadata } = await useLeporid<Metadata | null>('/api/nuxt/metadata', {
    query: { key: 'maimaiVersion' },
})

const canManageMetadata = computed(() => user.value?.permissions.includes(UserPermission.METADATA_ADMIN) === true)
const metadataValue = ref(maimaiVersionMetadata.value?.value || '')
const isSaving = ref(false)

async function handleSave() {
    isSaving.value = true
    try {
        await $leporid('/api/nuxt/metadata', {
            method: 'PUT',
            body: {
                key: 'maimaiVersion',
                value: metadataValue.value,
            },
            showSuccessToast: true,
            successMessage: '元数据已保存',
        })
    }
    finally {
        isSaving.value = false
    }
}
</script>

<template>
    <div class="min-h-screen bg-base-200">
        <main class="mx-auto w-full max-w-3xl px-4 py-4 lg:py-10">
            <div class="mb-6 flex items-center gap-3">
                <NuxtLink to="/preference" class="btn btn-ghost btn-sm" aria-label="返回偏好设置">
                    <span aria-hidden="true">←</span>
                    <span>返回</span>
                </NuxtLink>
                <h1 class="text-xl font-semibold">
                    管理员设置
                </h1>
            </div>

            <section class="rounded-box border border-base-200 bg-base-100 p-4 shadow-sm">
                <div class="mb-4">
                    <h2 class="font-semibold">
                        元数据管理
                    </h2>
                    <p class="mt-1 text-sm text-base-content/60">
                        管理应用使用的全局默认设置。
                    </p>
                </div>

                <div class="form-control gap-2">
                    <label for="maimai-version-metadata">
                        <p class="font-medium text-sm">
                            maimaiVersion
                        </p>
                        <p class="text-xs text-base-content/60">
                            设置未单独覆盖游戏版本的用户所使用的默认版本。
                        </p>
                    </label>
                    <div class="flex flex-col gap-3 sm:flex-row">
                        <input
                            id="maimai-version-metadata" v-model="metadataValue" class="input input-bordered flex-1"
                            type="text" :readonly="!canManageMetadata"
                        >
                        <button
                            v-if="canManageMetadata" class="btn btn-primary sm:min-w-28" type="button"
                            :disabled="isSaving" @click="handleSave"
                        >
                            <span v-if="isSaving" class="loading loading-spinner" />
                            <span>保存</span>
                        </button>
                    </div>
                    <p v-if="!canManageMetadata" class="text-sm text-warning">
                        当前账户没有 metadata 管理权限，只能查看设置。
                    </p>
                </div>
            </section>
        </main>
    </div>
</template>
