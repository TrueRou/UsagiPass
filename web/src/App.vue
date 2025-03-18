<script setup lang="ts">
import { RouterView } from 'vue-router'
import Notification from './components/widgets/Notification.vue'
</script>
<template>
  <Notification />
  <Suspense>
    <RouterView />
  </Suspense>
</template>
