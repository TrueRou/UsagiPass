<script setup lang="ts">
definePageMeta({ middleware: 'require-login' })

const route = useRoute()
const dateLimit = route.query.date as string | undefined
const timeLimit = route.query.time as string | undefined
const maimaiMaid = route.query.maid as string | undefined

const { data: profile } = await useLeporid<UserProfile>('/api/nuxt/profile')
const { img } = useUtils()

const simplifiedCode = computed(() => {
    if (maimaiMaid)
        return maimaiMaid.slice(8, 28).match(/.{1,4}/g)?.join(' ')
    return ''
})

const playerRating = computed(() => {
    // 覆盖优先级：动态评分（不为 0 的话） > 用户偏好设置
    if (profile.value?.preference.dynamicRating && profile.value?.player?.rating)
        return String(profile.value?.player?.rating)
    return profile.value?.preference.dxRating
})

const playerName = computed(() => {
    // 覆盖优先级：用户偏好设置 > 被动获取用户名
    if (profile.value?.preference.displayName)
        return profile.value?.preference.displayName
    return profile.value?.player?.name
})

const friendCode = computed(() => {
    // 覆盖优先级：用户偏好设置 > 被动获取好友代码
    if (profile.value?.preference.friendCode)
        return profile.value?.preference.friendCode
    return profile.value?.player?.friendCode
})
</script>

<template>
    <div v-if="profile" class="isolate h-[100dvh] dark:bg-gray-800">
        <div class="relative h-full w-fit mx-auto">
            <img class="object-cover h-full" :src="img(profile.preference.backgroundId)">
            <div class="absolute inset-0">
                <img class="chara-center h-full absolute object-cover" :src="img(profile.preference.characterId)">

                <img class="frame-upper h-full absolute" :src="img(profile.preference.frameId)">
                <div class="absolute inset-0">
                    <div class="relative space-y-2 w-full">
                        <WidgetDxRating class="pt-4 w-[40%]" :rating="playerRating" />
                        <WidgetPlayerInfo
                            :username="playerName"
                            :friend-code="friendCode" :player-info-color="profile.preference.playerInfoColor"
                        />
                    </div>
                </div>

                <WidgetCharaInfo
                    :chara-name="profile.preference.characterName || undefined" :time="timeLimit"
                    :date="dateLimit" :show-date="profile.preference.showDate"
                    :chara-info-color="profile.preference.charaInfoColor" class="bottom-[18%] absolute"
                />

                <div
                    id="c-footer" class="flex absolute bottom-0 items-center justify-center w-full pb-[0.8%]"
                    :style="{ '--b-bottom': `url(${img(profile.preference.frameId)})` }"
                >
                    <div class="footer-widget flex justify-between py-1 rounded-2xl bg-gray-800 text-white opacity-85">
                        <p class="footer-text font-sega">
                            {{ profile.preference.simplifiedCode || simplifiedCode }}
                        </p>
                        <p class="footer-text font-sega">
                            {{ profile.preference.maimaiVersion || '[maimaiDX]CN1.51-F' }}
                        </p>
                    </div>
                    <NuxtLink to="/preference">
                        <div class="p-1 rounded-full bg-white dark:bg-gray-800" aria-label="settings" role="img">
                            <svg
                                xmlns="http://www.w3.org/2000/svg" style="width: 3vmin;" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" aria-hidden="true"
                            >
                                <circle cx="12" cy="12" r="3" />
                                <path
                                    d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06A2 2 0 1 1 2.27 16.9l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09c.6 0 1.14-.36 1.51-1a1.65 1.65 0 0 0-.33-1.82l-.06-.06A2 2 0 1 1 6.1 2.27l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09c0 .6.36 1.14 1 1.51a1.65 1.65 0 0 0 1.82-.33l.06-.06A2 2 0 1 1 21.73 7.1l-.06.06a1.65 1.65 0 0 0-.33 1.82 1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09c-.6 0-1.14.36-1.51 1z"
                                />
                            </svg>
                        </div>
                    </NuxtLink>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.frame-upper {
    object-fit: contain;
    object-position: center top;
    clip-path: polygon(0 0, 100% 0, 100% 50%, 0 50%);
}

.chara-center {
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%)
}

.header-widget {
    padding-left: 2%;
    padding-right: 2%;
    padding-top: 0.4%;
}

.footer-widget {
    width: 85%;
    padding-left: 3%;
    padding-right: 3%;
}

.footer-text {
    font-size: clamp(1.2dvh, 2dvw, 1.8vmin);
    line-height: 120%;
}

.qr-front {
    bottom: 7%;
    right: 1%;
}

#c-footer {
    &:before {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding-top: 100vh;

        background-image: var(--b-bottom);
        background-size: contain;
        background-repeat: no-repeat;
        background-position: left bottom;
        clip-path: polygon(0 50%, 100% 50%, 100% 100%, 0 100%);
    }

    >* {
        z-index: 1;
    }
}
</style>
