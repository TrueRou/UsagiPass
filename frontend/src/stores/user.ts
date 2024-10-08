import axios from "axios"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useUserStore = defineStore('user', () => {
    const cookieData = JSON.parse(document.cookie || '{}')
    const token = cookieData['token']
    const maimaiCode = cookieData['maimaiCode']
    const simplifiedCode = computed(() => maimaiCode.slice(8, 28).match(/.{1,4}/g)?.join(' '))
    const axiosInstance = axios.create({
        baseURL: import.meta.env.VITE_URL,
        timeout: 3000,
        headers: { 'Authorization': `Bearer ${token}` },
    });

    const isSignedIn = ref(false)
    const userProfile = ref<UserProfile | null>(null)

    async function refreshUser() {
        const response = (await axiosInstance.get('/users/profile'))
        if (response.status === 200) {
            userProfile.value = response.data
            isSignedIn.value = true
        }
        isSignedIn.value = false
    }

    return { axiosInstance, maimaiCode, simplifiedCode, userProfile, refreshUser, isSignedIn }
})