<script setup lang="ts">
const { data: navigation } = await useAsyncData('navigation', () =>
    queryCollectionNavigation('content'))

const appConfig = useAppConfig()
</script>

<template>
    <div class="flex justify-between px-4 py-4 mx-auto sm:px-8 max-w-2xl">
        <!-- Navigation -->
        <div class="text-gray-700 dark:text-gray-200">
            <NuxtLink
                v-for="link in navigation"
                :key="link.path" class="mr-6"
                :to="link.path"
                active-class="font-bold"
            >
                {{ link.title }}
            </NuxtLink>
        </div>
        <!-- Social icons & Color Mode -->
        <div class="text-gray-500 space-x-3 transition">
            <a
                v-if="appConfig.socials?.github"
                class="dark:text-gray-100 hover:text-gray-700 dark:hover:text-gray-300"
                :href="`https://github.com/${appConfig.socials?.github}`"
                title="GitHub"
            >
                <Icon class="size-5" name="i-simple-icons-github" />
            </a>
            <a
                v-if="appConfig.socials?.mastodon"
                class="dark:text-gray-100 hover:text-gray-700 dark:hover:text-gray-300"
                :href="`https://elk.zone/${appConfig.socials?.mastodon}`" title="Mastodon"
            >
                <Icon class="size-5" name="i-simple-icons-mastodon" />
            </a>
            <a
                v-if="appConfig.socials?.bluesky"
                class="dark:text-gray-100 hover:text-gray-700 dark:hover:text-gray-300"
                :href="`https://bsky.app/profile/${appConfig.socials?.bluesky}`" title="Bluesky"
            >
                <Icon class="size-5" name="i-simple-icons-bluesky" />
            </a>
            <DocsColorModeSwitch class="dark:text-gray-100 hover:text-gray-700 dark:hover:text-gray-300" />
        </div>
    </div>
</template>
