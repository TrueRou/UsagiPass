<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-30"
      @click.self="closeDialog"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-4xl mx-4 max-h-[90vh] transform transition-all">
        <div class="p-5 sm:p-6">
          <!-- Header -->
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg sm:text-xl font-medium text-gray-900 dark:text-white">
              配置对战好友开关
            </h3>
            <button
              @click="closeDialog"
              class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="flex justify-center items-center h-64">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="text-center text-red-500 p-8">
            <p>{{ error }}</p>
            <button 
              @click="loadFriends"
              class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              重试
            </button>
          </div>

          <!-- Friends List -->
          <div v-else class="space-y-4 max-h-96 overflow-y-auto">
            <div v-if="friends.length === 0" class="text-center text-gray-500 py-8">
              暂无好友数据
            </div>
            
            <div 
              v-for="friend in friends" 
              :key="friend.id"
              class="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                  <!-- Friend Avatar -->
                  <div class="flex-shrink-0">
                    <img 
                      v-if="friend.icon_id"
                      :src="getIconUrl(friend.icon_id)"
                      :alt="friend.name"
                      class="w-12 h-12 rounded-full"
                      @error="handleImageError"
                    />
                    <div 
                      v-else
                      class="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center"
                    >
                      <span class="text-gray-600 text-sm">{{ friend.name?.charAt(0) || '?' }}</span>
                    </div>
                  </div>
                  
                  <!-- Friend Info -->
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center space-x-2">
                      <h4 class="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {{ friend.name || '未知用户' }}
                      </h4>
                      <!-- Nameplate -->
                      <img 
                        v-if="friend.plate_id"
                        :src="getPlateUrl(friend.plate_id)"
                        :alt="'姓名框'"
                        class="h-6"
                        @error="handleImageError"
                      />
                    </div>
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                      好友代码: {{ friend.friend_code || '未知' }}
                    </p>
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                      DX分数: {{ friend.rating || 'N/A' }}
                    </p>
                  </div>
                </div>

                <!-- Action Buttons -->
                <div class="flex items-center space-x-2">
                  <button
                    v-if="!friend.is_opponent"
                    @click="setOpponent(friend.id)"
                    :disabled="actionLoading === friend.id"
                    class="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {{ actionLoading === friend.id ? '设置中...' : '设置对手' }}
                  </button>
                  <button
                    v-else
                    @click="cancelOpponent(friend.id)"
                    :disabled="actionLoading === friend.id"
                    class="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {{ actionLoading === friend.id ? '取消中...' : '取消对手' }}
                  </button>
                </div>
              </div>
              
              <!-- Background Preview (if available) -->
              <div v-if="friend.frame_id" class="mt-3">
                <img 
                  :src="getFrameUrl(friend.frame_id)"
                  :alt="'背景'"
                  class="w-full h-20 object-cover rounded"
                  @error="handleImageError"
                />
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
            <button
              @click="closeDialog"
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useUserStore } from '@/stores/user';
import { useNotificationStore } from '@/stores/notification';

const props = defineProps<{
  show: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const userStore = useUserStore();
const notificationStore = useNotificationStore();

const loading = ref(false);
const error = ref('');
const friends = ref<any[]>([]);
const actionLoading = ref<string | null>(null);

// Public API base URL for maimai assets
const ASSETS_BASE_URL = 'https://assets2.lxns.net/maimai';

const getIconUrl = (iconId: string) => `${ASSETS_BASE_URL}/icon/${iconId}.png`;
const getPlateUrl = (plateId: string) => `${ASSETS_BASE_URL}/plate/${plateId}.png`;
const getFrameUrl = (frameId: string) => `${ASSETS_BASE_URL}/frame/${frameId}.png`;

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  img.style.display = 'none';
};

const loadFriends = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    const response = await userStore.axiosInstance.get('/accounts/friends');
    friends.value = response.data.friends || [];
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取好友列表失败';
    console.error('获取好友列表失败:', err);
  } finally {
    loading.value = false;
  }
};

const setOpponent = async (friendId: string) => {
  actionLoading.value = friendId;
  
  try {
    await userStore.axiosInstance.post(`/accounts/friends/${friendId}/opponent`);
    
    // Update local state
    const friend = friends.value.find(f => f.id === friendId);
    if (friend) {
      friend.is_opponent = true;
    }
    
    notificationStore.success('设置成功', '已设置为对手');
  } catch (err: any) {
    notificationStore.error('设置失败', err.response?.data?.detail || '设置对手失败');
    console.error('设置对手失败:', err);
  } finally {
    actionLoading.value = null;
  }
};

const cancelOpponent = async (friendId: string) => {
  actionLoading.value = friendId;
  
  try {
    await userStore.axiosInstance.delete(`/accounts/friends/${friendId}/opponent`);
    
    // Update local state
    const friend = friends.value.find(f => f.id === friendId);
    if (friend) {
      friend.is_opponent = false;
    }
    
    notificationStore.success('取消成功', '已取消对手设置');
  } catch (err: any) {
    notificationStore.error('取消失败', err.response?.data?.detail || '取消对手失败');
    console.error('取消对手失败:', err);
  } finally {
    actionLoading.value = null;
  }
};

const closeDialog = () => {
  emit('close');
};

// Load friends when dialog opens
watch(() => props.show, (newVal) => {
  if (newVal) {
    loadFriends();
  }
});
</script>

<style scoped>
/* Custom scrollbar for webkit browsers */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Dark mode scrollbar */
.dark .overflow-y-auto::-webkit-scrollbar-track {
  background: #374151;
}

.dark .overflow-y-auto::-webkit-scrollbar-thumb {
  background: #6b7280;
}

.dark .overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>