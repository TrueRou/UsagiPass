<template>
    <div>
        <NuxtPage />
        <ClientOnly>
            <NuxtLoadingIndicator />
            <AppNotification />
        </ClientOnly>
    </div>
</template>
