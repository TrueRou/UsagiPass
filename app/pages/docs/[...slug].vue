<script setup lang="ts">
/**
 * Document driven is removed in Content v3.
 * This page is a simple/full-feature replacement of document driven.
 */
import '@/assets/css/cms.css'

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
        <CmsNavBar />
        <div class="px-4 py-10 m-auto sm:px-8 sm:rounded-lg max-w-2xl sm:shadow bg-white dark:bg-gray-800 ring-1 ring-gray-200 dark:ring-gray-700">
            <main class="max-w-none">
                <ContentRenderer
                    v-if="page"
                    :value="page"
                    class="prose dark:prose-invert prose-pre:bg-gray-100 dark:prose-pre:bg-gray-900"
                />
            </main>
        </div>
    </div>
</template>
