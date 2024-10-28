import axios from "axios"
import { defineStore } from "pinia"
import { computed, ref } from "vue"

export const useUserStore = defineStore('user', () => {
    const token = ref(localStorage.getItem('token'))
    const maimaiCode = ref("")
    const timeLimit = ref("12:00:00")
    const simplifiedCode = computed(() => maimaiCode.value.slice(8, 28).match(/.{1,4}/g)?.join(' '))
    const axiosInstance = computed(() => axios.create({
        baseURL: import.meta.env.VITE_URL,
        timeout: 3000,
        headers: { 'Authorization': `Bearer ${token.value}` },
    }));

    const isSignedIn = ref(false)
    const userProfile = ref<UserProfile | null>(null)

    async function login(username: string, password: string) {
        try {
            const data = await axiosInstance.value.post('/users/token', new URLSearchParams({
                username,
                password
            }))
            localStorage.setItem('token', data.data.access_token)
            token.value = data.data.access_token
            await refreshUser()
            return true
        } catch (error) {
            alert("账号或密码错误")
            return false
        }
    }

    function logout() {
        localStorage.removeItem('token')
        token.value = null
        isSignedIn.value = false
        location.reload()
    }

    async function updateRating() {
        if (isSignedIn) {
            await axiosInstance.value.patch('/users/rating')
        }
    }

    async function refreshUser() {
        try {
            const response = (await axiosInstance.value.get('/users/profile'))
            userProfile.value = response.data
            isSignedIn.value = true
        } catch (error) {
            isSignedIn.value = false
        }
    }

    async function getImages(): Promise<Record<string, ImagePublic[]>> {
        const response = await axiosInstance.value.get('/users/gallery')
        const result = response.data.reduce((acc: any, obj: any) => {
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

    async function patchPreferences() {
        const response = await axiosInstance.value.patch('/users/preference', userProfile.value!.preferences)
        if (response.status === 200) {
            await refreshUser()
        }
        return response.status === 200
    }

    return { maimaiCode, timeLimit, simplifiedCode, userProfile, isSignedIn, refreshUser, updateRating, getImages, patchPreferences, login, logout }
})