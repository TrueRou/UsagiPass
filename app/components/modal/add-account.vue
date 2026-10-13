<script setup lang="ts">
import type { Server } from '~~/server/utils/drizzle'

const props = defineProps<{
    open: boolean
    servers: Server[]
    authorizing?: boolean
}>()

const emit = defineEmits<{
    (event: 'update:open', value: boolean): void
    (event: 'confirm', server: Server, credentials: string): void
    (event: 'oauth', server: Server): void
}>()

const selectedServer = ref<Server | null>(null)
const credentialsModel = ref('')

const serverMap = computed(() => {
    const map = new Map<number, Server>()
    props.servers.forEach(server => map.set(server.id, server))
    return map
})

const oauthCapable = computed(() => isProberOAuthServer(selectedServer.value?.identifier))
</script>

<template>
    <div v-if="props.open" class="modal modal-open">
        <div class="modal-box space-y-4">
            <div class="space-y-1">
                <h3 class="text-lg font-semibold">
                    添加账号
                </h3>
                <p class="text-sm text-base-content/70">
                    添加用于更新查分器的账号
                </p>
            </div>

            <div class="space-y-4">
                <div class="form-control flex flex-col">
                    <label class="label">
                        <span class="label-text">查分器</span>
                    </label>
                    <select
                        v-model="selectedServer" class="select select-bordered"
                        :disabled="props.servers.length === 0" required
                    >
                        <option :value="null" disabled selected>
                            选择一个支持的查分器
                        </option>
                        <option v-for="server in props.servers" :key="server.id" :value="server">
                            {{ server.name }}
                        </option>
                    </select>
                </div>

                <template v-if="oauthCapable">
                    <div class="space-y-2">
                        <button
                            class="btn btn-primary w-full" type="button" :disabled="props.authorizing"
                            @click="emit('oauth', selectedServer!)"
                        >
                            <span v-if="props.authorizing" class="loading loading-spinner loading-sm" />
                            使用 {{ selectedServer!.name }} 授权
                        </button>
                        <p class="text-xs text-base-content/60 leading-relaxed">
                            跳转至查分器完成 OAuth 授权，安全且方便。
                        </p>
                    </div>

                    <!-- <details class="collapse collapse-arrow rounded-lg border border-base-300">
                        <summary class="collapse-title min-h-0 py-3 text-sm">
                            使用 {{ selectedServer!.credentialsName || '凭证' }}
                        </summary>
                        <div class="collapse-content">
                            <input
                                v-model="credentialsModel" class="input input-bordered w-full" type="text"
                                :placeholder="selectedServer!.credentialsName || '输入查分器凭证（如个人密钥）'"
                            >
                        </div>
                    </details> -->
                </template>

                <div v-else class="form-control flex flex-col">
                    <label class="label">
                        <span class="label-text">
                            凭证
                        </span>
                    </label>
                    <input
                        v-model="credentialsModel" class="input input-bordered" type="text"
                        :placeholder="selectedServer?.credentialsName || '输入查分器凭证（如个人密钥）'"
                    >
                </div>
            </div>

            <div
                v-if="selectedServer && (!oauthCapable || credentialsModel)"
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
                        前往查分器
                    </a>
                </div>
            </div>

            <div v-if="!oauthCapable" class="modal-action">
                <button class="btn btn-ghost" type="button" @click="emit('update:open', false)">
                    取消
                </button>
                <button v-if="!oauthCapable || credentialsModel" class="btn" :class="oauthCapable ? 'btn-outline' : 'btn-primary'" type="button" :disabled="!selectedServer || !credentialsModel" @click="emit('confirm', selectedServer!, credentialsModel)">
                    添加账号
                </button>
            </div>
        </div>
        <button
            class="modal-backdrop" type="button" aria-label="取消"
            @click="emit('update:open', false)"
        >
            取消
        </button>
    </div>
</template>

<style scoped>
option[disabled] {
  display: none;
}
</style>
