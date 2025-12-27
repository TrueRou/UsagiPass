<template>
    <div class="flex justify-between px-4 py-4 mx-auto sm:px-8 max-w-2xl">
        <!-- Navigation -->
        <div class="text-gray-700 dark:text-gray-200">
            <NuxtLink class="mr-6" to="/docs/manual" active-class="font-bold">
                手册
            </NuxtLink>
            <NuxtLink class="mr-6" to="/docs/advanced" active-class="font-bold">
                开发者
            </NuxtLink>
            <NuxtLink class="mr-6" to="/docs/advanced/privacy-policy" active-class="font-bold">
                隐私政策
            </NuxtLink>
            <NuxtLink class="mr-6" to="/docs/advanced/terms-of-service" active-class="font-bold">
                服务条款
            </NuxtLink>
        </div>
        <!-- Social icons & Color Mode -->
        <div class="text-gray-500 space-x-3 transition">
            <a
                class="dark:text-gray-100 hover:text-gray-700 dark:hover:text-gray-300"
                href="https://github.com/TrueRou/UsagiPass"
                title="GitHub"
            >
                <Icon class="size-5" name="i-simple-icons-github" />
            </a>
        </div>
    </div>
</template>
