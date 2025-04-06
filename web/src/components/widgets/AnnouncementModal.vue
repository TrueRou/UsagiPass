<script setup lang="ts">
import { useAnnouncementStore } from '@/stores/announcement';
import { computed } from 'vue';

const announcementStore = useAnnouncementStore();

const renderedContent = computed(() => {
  if (announcementStore.currentAnnouncement) {
    return announcementStore.renderMarkdown(announcementStore.currentAnnouncement.content);
  }
  return '';
});

const closeAndMarkAsRead = async () => {
  await announcementStore.handleCurrentAnnouncementRead();
};
</script>

<template>
  <Teleport to="body">
    <div v-if="announcementStore.showAnnouncementModal && announcementStore.currentAnnouncement"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[1000] p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- 公告标题 -->
        <div class="p-4 bg-blue-400 dark:bg-blue-600 text-white flex justify-between items-center">
          <span class="font-bold text-lg">{{ announcementStore.currentAnnouncement.title }}</span>
          <button @click="closeAndMarkAsRead" class="text-white hover:text-gray-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 公告内容 -->
        <div class="p-6 overflow-y-auto flex-1">
          <div class="prose dark:prose-invert max-w-none" v-html="renderedContent"></div>
        </div>

        <!-- 底部操作区 -->
        <div class="p-4 bg-gray-100 dark:bg-gray-700 flex justify-end">
          <button @click="closeAndMarkAsRead"
            class="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded transition-colors">
            我已阅读
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
:deep(.prose) {
  max-width: 100%;
}

:deep(.prose a) {
  color: #3b82f6;
  text-decoration: underline;
}

:deep(.prose a:hover) {
  color: #2563eb;
}

:deep(.prose img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.375rem;
}

:deep(.prose pre) {
  background-color: #f3f4f6;
  border-radius: 0.375rem;
  padding: 1rem;
  overflow-x: auto;
}

:deep(.prose code) {
  background-color: #f3f4f6;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
}

@media (prefers-color-scheme: dark) {
  :deep(.prose pre) {
    background-color: #374151;
  }

  :deep(.prose code) {
    background-color: #374151;
  }
}
</style>