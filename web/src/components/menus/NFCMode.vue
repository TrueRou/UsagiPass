<script setup lang="ts">
import { ref } from 'vue';
import { readUuidFromNfc, writeUuidToNfc } from '@/utils';
import { useNotificationStore } from '@/stores/notification';
import { useRouter } from 'vue-router';

const notificationStore = useNotificationStore();
const router = useRouter();

const isReading = ref(false);
const uuid = ref<string | null>(null);
const selectedMode = ref<'fast' | 'normal'>('fast');
const isWriting = ref(false);
const scanStep = ref(1); // 1: 初始状态, 2: 正在扫描, 3: 扫描完成/选择模式, 4: 正在写入

const readCard = async () => {
    if (isReading.value) return;

    isReading.value = true;
    scanStep.value = 2;

    try {
        const result = await readUuidFromNfc();
        if (result) {
            uuid.value = result;
            scanStep.value = 3;
        } else {
            scanStep.value = 1;
        }
    } catch (error) {
        notificationStore.error("读取失败", "无法读取NFC卡片");
        scanStep.value = 1;
    } finally {
        isReading.value = false;
    }
};

const writeCard = async () => {
    if (!uuid.value || isWriting.value) return;

    isWriting.value = true;
    scanStep.value = 4;

    try {
        const success = await writeUuidToNfc(uuid.value, selectedMode.value);
        if (success) {
            router.replace({ name: 'cards', state: { "cardUUID": uuid.value } });
        } else {
            scanStep.value = 3;
        }
    } finally {
        isWriting.value = false;
    }
};

const resetState = () => {
    scanStep.value = 1;
    uuid.value = null;
};
</script>

<template>
    <div class="flex items-center w-full">
        <div class="p-8 w-full">
            <!-- 扫描状态区域 -->
            <div class="mb-8">
                <div class="relative">
                    <!-- 步骤指示器 -->
                    <div class="flex items-center justify-between mb-6">
                        <div v-for="step in 4" :key="step" class="flex flex-col items-center">
                            <div class="w-10 h-10 rounded-full flex items-center justify-center text-white text-lg font-medium"
                                :class="scanStep >= step ? 'bg-indigo-500' : 'bg-gray-300'">
                                {{ step }}
                            </div>
                            <div class="text-xs mt-2 text-center"
                                :class="scanStep >= step ? 'text-indigo-500' : 'text-gray-500'">
                                {{ ['准备', '扫描', '选择', '写入'][step - 1] }}
                            </div>
                        </div>
                    </div>

                    <!-- NFC动画 - 使用内联SVG -->
                    <div class="flex justify-center mb-8">
                        <!-- 初始状态 - 手机NFC位置 -->
                        <div v-if="scanStep === 1" class="w-64 h-64 relative">
                            <svg viewBox="0 0 200 200" class="w-full h-full">
                                <!-- 手机外形 -->
                                <rect x="60" y="30" width="80" height="140" rx="10" fill="#f1f5f9" stroke="#94a3b8"
                                    stroke-width="2" />
                                <rect x="70" y="45" width="60" height="100" rx="2" fill="#e2e8f0" />

                                <!-- NFC区域指示 -->
                                <circle cx="100" cy="80" r="20" fill="none" stroke="#4f46e5" stroke-width="2"
                                    stroke-dasharray="5,3" />
                                <path d="M90,82 Q100,72 110,82" stroke="#4f46e5" stroke-width="2" fill="none" />
                                <path d="M85,90 Q100,75 115,90" stroke="#4f46e5" stroke-width="2" fill="none" />

                                <!-- 文字标注 -->
                                <text x="100" y="115" text-anchor="middle" font-size="8" fill="#6b7280">NFC区域</text>
                            </svg>
                        </div>

                        <!-- 扫描状态 - 带动画效果 -->
                        <div v-else-if="scanStep === 2" class="w-64 h-64 relative nfc-scan-container">
                            <svg viewBox="0 0 200 200" class="w-full h-full">
                                <!-- 手机外形 -->
                                <rect x="60" y="30" width="80" height="140" rx="10" fill="#f1f5f9" stroke="#94a3b8"
                                    stroke-width="2" />
                                <rect x="70" y="45" width="60" height="100" rx="2" fill="#e2e8f0" />

                                <!-- NFC区域指示 -->
                                <circle cx="100" cy="80" r="20" fill="none" stroke="#4f46e5" stroke-width="2"
                                    stroke-dasharray="5,3" />

                                <!-- NFC波纹动画 -->
                                <circle cx="100" cy="80" r="10" fill="rgba(79, 70, 229, 0.1)">
                                    <animate attributeName="r" from="5" to="25" dur="2s" repeatCount="indefinite" />
                                    <animate attributeName="opacity" from="0.7" to="0" dur="2s"
                                        repeatCount="indefinite" />
                                </circle>

                                <circle cx="100" cy="80" r="10" fill="rgba(79, 70, 229, 0.1)">
                                    <animate attributeName="r" from="5" to="25" dur="2s" begin="0.5s"
                                        repeatCount="indefinite" />
                                    <animate attributeName="opacity" from="0.7" to="0" dur="2s" begin="0.5s"
                                        repeatCount="indefinite" />
                                </circle>

                                <circle cx="100" cy="80" r="10" fill="rgba(79, 70, 229, 0.1)">
                                    <animate attributeName="r" from="5" to="25" dur="2s" begin="1s"
                                        repeatCount="indefinite" />
                                    <animate attributeName="opacity" from="0.7" to="0" dur="2s" begin="1s"
                                        repeatCount="indefinite" />
                                </circle>

                                <!-- NFC卡 -->
                                <g transform="translate(100, 140) rotate(15)">
                                    <animateTransform attributeName="transform" type="translate" from="100, 150"
                                        to="100, 140" dur="2s" repeatCount="indefinite" additive="sum" />
                                    <rect x="-25" y="-15" width="50" height="30" rx="2" fill="#f5f3ff" stroke="#8b5cf6"
                                        stroke-width="1" />
                                    <circle cx="-15" cy="0" r="5" fill="#ddd6fe" />
                                    <path d="M-5,-5 H15 M-5,0 H10 M-5,5 H5" stroke="#c4b5fd" stroke-width="1" />
                                </g>
                            </svg>
                        </div>

                        <!-- 扫描成功状态 -->
                        <div v-else-if="scanStep === 3" class="w-64 h-64 relative">
                            <svg viewBox="0 0 200 200" class="w-full h-full">
                                <!-- 成功图标 -->
                                <circle cx="100" cy="100" r="50" fill="#c7d2fe" />
                                <circle cx="100" cy="100" r="40" fill="#818cf8" />
                                <path d="M80,100 L95,115 L120,85" stroke="white" stroke-width="6" fill="none"
                                    stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </div>

                        <!-- 写入状态 -->
                        <div v-else-if="scanStep === 4" class="w-64 h-64 relative nfc-write-container">
                            <svg viewBox="0 0 200 200" class="w-full h-full">
                                <!-- 手机外形 -->
                                <rect x="60" y="30" width="80" height="140" rx="10" fill="#f1f5f9" stroke="#94a3b8"
                                    stroke-width="2" />
                                <rect x="70" y="45" width="60" height="100" rx="2" fill="#e2e8f0" />

                                <!-- NFC区域指示 -->
                                <circle cx="100" cy="80" r="20" fill="none" stroke="#4f46e5" stroke-width="2"
                                    stroke-dasharray="5,3" />

                                <!-- NFC波纹动画 - 向外发射 -->
                                <circle cx="100" cy="80" r="10" fill="rgba(79, 70, 229, 0.1)">
                                    <animate attributeName="r" from="20" to="5" dur="1.5s" repeatCount="indefinite" />
                                    <animate attributeName="opacity" from="0" to="0.7" dur="1.5s"
                                        repeatCount="indefinite" />
                                </circle>

                                <circle cx="100" cy="80" r="10" fill="rgba(79, 70, 229, 0.1)">
                                    <animate attributeName="r" from="20" to="5" dur="1.5s" begin="0.3s"
                                        repeatCount="indefinite" />
                                    <animate attributeName="opacity" from="0" to="0.7" dur="1.5s" begin="0.3s"
                                        repeatCount="indefinite" />
                                </circle>

                                <circle cx="100" cy="80" r="10" fill="rgba(79, 70, 229, 0.1)">
                                    <animate attributeName="r" from="20" to="5" dur="1.5s" begin="0.6s"
                                        repeatCount="indefinite" />
                                    <animate attributeName="opacity" from="0" to="0.7" dur="1.5s" begin="0.6s"
                                        repeatCount="indefinite" />
                                </circle>

                                <!-- NFC卡 - 带振动效果 -->
                                <g>
                                    <animateTransform attributeName="transform" type="translate"
                                        values="0,0; 1,1; 0,-1; -1,0; 0,0" dur="0.5s" repeatCount="indefinite" />
                                    <rect x="75" y="130" width="50" height="30" rx="2" transform="rotate(15, 100, 145)"
                                        fill="#f5f3ff" stroke="#8b5cf6" stroke-width="1" />
                                    <circle cx="85" cy="145" r="5" transform="rotate(15, 100, 145)" fill="#ddd6fe" />
                                    <path d="M95,140 H115 M95,145 H110 M95,150 H105" transform="rotate(15, 100, 145)"
                                        stroke="#c4b5fd" stroke-width="1" />
                                </g>
                            </svg>
                        </div>
                    </div>

                    <!-- 操作指引 -->
                    <div class="text-center mb-6">
                        <h3 class="text-lg font-medium mb-2">
                            {{
                                scanStep === 1 ? '开始扫描' :
                                    scanStep === 2 ? '请将卡片靠近手机NFC区域' :
                                        scanStep === 3 ? '选择写入模式' :
                                            '正在写入卡片...'
                            }}
                        </h3>
                        <p class="text-gray-600 text-sm" v-if="scanStep <= 2">
                            NFC区域通常位于手机背面中上部或中部位置，不同手机可能位置略有不同，请尝试移动卡片找到正确位置。
                        </p>
                        <p class="text-gray-600 text-sm" v-else-if="scanStep === 3">
                            卡片读取成功，请选择写入模式。
                        </p>
                        <p class="text-gray-600 text-sm" v-else>
                            请保持卡片与手机接触，直到写入完成。
                        </p>
                    </div>
                </div>
            </div>

            <!-- 模式选择 -->
            <div v-if="scanStep === 3" class="mb-8">
                <div class="flex flex-col space-y-2 mb-6">
                    <div class="flex-1 border rounded-lg p-4 cursor-pointer transition-all"
                        :class="selectedMode === 'fast' ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300'"
                        @click="selectedMode = 'fast'">
                        <div class="flex items-center mb-2">
                            <div class="w-5 h-5 rounded-full border-2 mr-2 flex items-center justify-center"
                                :class="selectedMode === 'fast' ? 'border-indigo-500' : 'border-gray-400'">
                                <div v-if="selectedMode === 'fast'" class="w-3 h-3 rounded-full bg-indigo-500">
                                </div>
                            </div>
                            <h4 class="font-medium">快速模式</h4>
                        </div>
                        <p class="text-sm text-gray-600">
                            针对Android优化，支持多种浏览器快速打开，但在部分设备上可能兼容性略差。
                        </p>
                    </div>

                    <div class="flex-1 border rounded-lg p-4 cursor-pointer transition-all"
                        :class="selectedMode === 'normal' ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300'"
                        @click="selectedMode = 'normal'">
                        <div class="flex items-center mb-2">
                            <div class="w-5 h-5 rounded-full border-2 mr-2 flex items-center justify-center"
                                :class="selectedMode === 'normal' ? 'border-indigo-500' : 'border-gray-400'">
                                <div v-if="selectedMode === 'normal'" class="w-3 h-3 rounded-full bg-indigo-500">
                                </div>
                            </div>
                            <h4 class="font-medium">兼容模式</h4>
                        </div>
                        <p class="text-sm text-gray-600">
                            通用模式，兼容所有支持NFC的设备，但可能需要手动选择浏览器打开链接。
                        </p>
                    </div>
                </div>
            </div>

            <!-- 操作按钮 -->
            <div class="flex justify-center space-x-4">
                <button v-if="scanStep === 1" @click="readCard"
                    class="px-6 py-3 bg-indigo-500 text-white font-medium rounded-lg shadow-md hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-opacity-75 transition-colors"
                    :disabled="isReading">
                    {{ isReading ? '正在扫描...' : '开始扫描' }}
                </button>

                <button v-else-if="scanStep === 2"
                    class="px-6 py-3 bg-gray-400 text-white font-medium rounded-lg shadow-md cursor-not-allowed"
                    disabled>
                    扫描中...
                </button>

                <template v-else-if="scanStep === 3">
                    <button @click="resetState"
                        class="px-6 py-3 bg-gray-300 text-gray-700 font-medium rounded-lg shadow-md hover:bg-gray-400 focus:outline-none transition-colors">
                        重新扫描
                    </button>

                    <button @click="writeCard"
                        class="px-6 py-3 bg-indigo-500 text-white font-medium rounded-lg shadow-md hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-opacity-75 transition-colors">
                        写入卡片
                    </button>
                </template>

                <button v-else
                    class="px-6 py-3 bg-gray-400 text-white font-medium rounded-lg shadow-md cursor-not-allowed"
                    disabled>
                    写入中...
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* 保留必要的CSS样式，移除了与外部SVG相关的样式 */
.nfc-scan-container,
.nfc-write-container {
    position: relative;
    overflow: hidden;
}
</style>
