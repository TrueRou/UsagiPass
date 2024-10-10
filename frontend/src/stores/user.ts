import axios from "axios"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

const textCookie = {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InR1cm91In0.ziiLRBKYwcSn3DYb5GyMrDaeUWREvfQnOds-4P1h3UY",
    "maimaiCode": "1234567890123456789012345678901234567890",
    "timeLimit": "10:30:00"
}

export const useUserStore = defineStore('user', () => {
    const cookieData = JSON.parse(document.cookie || JSON.stringify(textCookie))
    const token = cookieData['token']
    const maimaiCode = cookieData['maimaiCode']
    const timeLimit = cookieData['timeLimit']
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

    async function getImages() : Promise<Record<string, ImagePublic[]>> {
        const response = await axiosInstance.get('/images')
        const data = response.data
        const result = data.reduce((acc: any, obj: any) => {
            if (!acc[obj.kind]) {
              acc[obj.kind] = [];
            }
            
            acc[obj.kind].push({
              id: obj.id,
              name: obj.name,
              uploaded_by: obj.uploaded_by
            });
            
            return acc;
          }, {});
        return result
    }

    async function patchPreferences(preferences: UserPreferencePublic) {
        const response = await axiosInstance.patch('/users/preference', preferences)
        if (response.status === 200) {
            userProfile.value = response.data
        }
        return response.status === 200
    }

    return { axiosInstance, maimaiCode, timeLimit, simplifiedCode, userProfile, isSignedIn, refreshUser, getImages, patchPreferences }
})