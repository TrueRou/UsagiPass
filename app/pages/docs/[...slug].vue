<script setup lang="ts">
/**
 * Document driven is removed in Content v3.
 * This page is a simple/full-feature replacement of document driven.
 */
import type { LayoutKey } from '#build/types/layouts'
import '@/assets/css/docs.css'

const route = useRoute()

const { data: page } = await useAsyncData(`page-${route.params.slug}`, () => {
    return queryCollection('content').path(route.path).first()
})

if (!page.value) {
    throw createError({
        statusCode: 404,
        statusMessage: 'Page not found',
    })
}

useSeoMeta(page.value?.seo || {})
</script>

<template>
    <div class="sm:pt-6 sm:pb-10">
        <DocsNavbar />
        <NuxtLayout :name="page?.layout as LayoutKey || 'default'" class="bg-white dark:bg-gray-800 ring-1 ring-gray-200 dark:ring-gray-700">
            <ContentRenderer
                v-if="page"
                :value="page"
                class="prose dark:prose-invert prose-pre:bg-gray-100 dark:prose-pre:bg-gray-900"
            />
        </NuxtLayout>
    </div>
</template>
