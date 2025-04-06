<script setup lang="ts">
import { RouterView } from 'vue-router'
import Notification from './components/widgets/Notification.vue'
import AnnouncementModal from './components/widgets/AnnouncementModal.vue'
import { useAnnouncementStore } from './stores/announcement'
import { useUserStore } from './stores/user'
import { watch } from 'vue'
import { Privilege } from './types'

const userStore = useUserStore()
const announcementStore = useAnnouncementStore()

// 监听用户登录状态，当用户登录后加载公告
watch(() => userStore.isSignedIn, (isSignedIn) => {
  if (isSignedIn && userStore.userProfile?.privilege !== Privilege.ADMIN) {
    announcementStore.initAnnouncements()
  }
}, { immediate: true })
</script>

<template>
  <Notification />
  <AnnouncementModal />
  <Suspense>
    <RouterView />
  </Suspense>
</template>
