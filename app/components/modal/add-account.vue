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
                    {{ t('accounts.add-modal.title') }}
                </h3>
                <p class="text-sm text-base-content/70">
                    {{ t('accounts.add-modal.description') }}
                </p>
            </div>

            <div class="space-y-4">
                <div class="form-control">
                    <label class="label">
                        <span class="label-text">{{ t('fields.account.server') }}</span>
                    </label>
                    <select
                        v-model="selectedServer" class="select select-bordered"
                        :disabled="props.servers.length === 0"
                    >
                        <option v-for="server in props.servers" :key="server.id" :value="server">
                            {{ server.name }}
                        </option>
                    </select>
                </div>

                <div class="form-control">
                    <label class="label">
                        <span class="label-text">
                            {{ t('fields.account.credentials') }}
                        </span>
                    </label>
                    <input
                        v-model="credentialsModel" class="input input-bordered" type="text"
                        :placeholder="selectedServer?.credentialsField || ''"
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
                    <p class="text-xs leading-relaxed">
                        {{ serverMap.get(selectedServer.id)!.tipsDesc }}
                    </p>
                    <a
                        v-if="serverMap.get(selectedServer.id)!.tipsUrl"
                        class="link link-primary text-xs"
                        :href="serverMap.get(selectedServer.id)!.tipsUrl" target="_blank"
                        rel="noopener"
                    >
                        {{ t("sections.accounts.tips-link") }}
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
