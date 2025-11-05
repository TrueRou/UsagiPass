<script setup lang="ts">
import type { Server } from '~~/server/utils/drizzle'

const props = defineProps<{
    open: boolean
    servers: Server[]
}>()

const emit = defineEmits<{
    (event: 'update:open', value: boolean): void
    (event: 'confirm', server: Server, credentials: string): void
}>()

const selectedServer = ref<Server | null>(null)
const credentialsModel = ref('')

const serverMap = computed(() => {
    const map = new Map<number, Server>()
    props.servers.forEach(server => map.set(server.id, server))
    return map
})

const { t } = useI18n()
</script>

<template>
    <div v-if="props.open" class="modal modal-open">
        <div class="modal-box space-y-4">
            <div class="space-y-1">
                <h3 class="text-lg font-semibold">
                    {{ t('title') }}
                </h3>
                <p class="text-sm text-base-content/70">
                    {{ t('description') }}
                </p>
            </div>

            <div class="space-y-4">
                <div class="form-control flex flex-col">
                    <label class="label">
                        <span class="label-text">{{ t('fields.server.label') }}</span>
                    </label>
                    <select
                        v-model="selectedServer" class="select select-bordered"
                        :disabled="props.servers.length === 0" required
                    >
                        <option :value="null" disabled selected>
                            {{ t('fields.server.placeholder') }}
                        </option>
                        <option v-for="server in props.servers" :key="server.id" :value="server">
                            {{ server.name }}
                        </option>
                    </select>
                </div>

                <div class="form-control flex flex-col">
                    <label class="label">
                        <span class="label-text">
                            {{ t('fields.credentials.label') }}
                        </span>
                    </label>
                    <input
                        v-model="credentialsModel" class="input input-bordered" type="text"
                        :placeholder="selectedServer?.credentialsName || t('fields.credentials.placeholder')"
                    >
                </div>
            </div>

            <div
                v-if="selectedServer"
                class="alert bg-base-200 text-base-content/80"
            >
                <div>
                    <h4 class="text-sm font-semibold">
                        {{ serverMap.get(selectedServer.id)!.tipsTitle }}
                    </h4>
                    <p class="text-xs leading-relaxed whitespace-pre-wrap">
                        {{ serverMap.get(selectedServer.id)!.tipsDesc }}
                    </p>
                    <a
                        v-if="serverMap.get(selectedServer.id)!.tipsUrl"
                        class="link link-primary text-xs"
                        :href="serverMap.get(selectedServer.id)!.tipsUrl" target="_blank"
                        rel="noopener"
                    >
                        {{ t("tips-link") }}
                    </a>
                </div>
            </div>

            <div class="modal-action">
                <button class="btn btn-ghost" type="button" @click="emit('update:open', false)">
                    {{ t('actions.cancel') }}
                </button>
                <button class="btn btn-primary" type="button" :disabled="!selectedServer || !credentialsModel" @click="emit('confirm', selectedServer!, credentialsModel)">
                    {{ t('actions.add-account') }}
                </button>
            </div>
        </div>
        <button
            class="modal-backdrop" type="button" :aria-label="t('actions.cancel')"
            @click="emit('update:open', false)"
        >
            {{ t('actions.cancel') }}
        </button>
    </div>
</template>

<style scoped>
option[disabled] {
  display: none;
}
</style>

<i18n lang="yaml">
zh-CN:
    title: 添加账号
    description: 添加用于更新查分器的账号
    fields:
        server:
            label: 查分器
            placeholder: 选择一个支持的查分器
        credentials:
            label: 凭证
            placeholder: 输入查分器的凭证(例如个人秘钥)
    actions:
        cancel: 取消
        add-account: 添加账号
en-GB:
    title: Add Account
    description: Add account which for update your scores to provider data.
    fields:
        server:
            label: Server Provider
            placeholder: Select an server which supported
        credentials:
            label: Credentials
            placeholder: Enter Server Credentials
    actions:
        cancel: Cancel
        add-account: Add Account
</i18n>
