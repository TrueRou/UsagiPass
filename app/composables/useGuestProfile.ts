const GUEST_STORAGE_KEY = 'usagipass_guest_profile'

const DEFAULT_GUEST_PROFILE: UserPreference = {
    userId: '',
    maimaiVersion: '',
    simplifiedCode: '',
    characterName: '',
    friendCode: '',
    displayName: '',
    dxRating: '',
    qrSize: 15,
    maskType: 0,
    playerInfoColor: '#ffffff',
    charaInfoColor: '#fee37c',
    showDxRating: true,
    showDisplayName: true,
    showFriendCode: true,
    showDate: true,
    enableMask: false,
    characterId: '2e7046aa-ddc2-40fb-bf5d-5236ffca50f9',
    maskId: '421943e9-2221-45f1-8f76-5a1ca012028e',
    backgroundId: '6a742fd3-f9e2-4edf-ab65-9208fae30d36',
    frameId: '421943e9-2221-45f1-8f76-5a1ca012028e',
    passnameId: 'f6988add-bb65-4b78-a69c-7d01c453d4a8',
    skipTour: false,
}

export function useGuestProfile() {
    const guestProfile = ref<UserPreference>({ ...DEFAULT_GUEST_PROFILE })
    const isLoaded = ref(false)

    function loadGuestProfile(): UserPreference | null {
        if (import.meta.client) {
            try {
                const data = localStorage.getItem(GUEST_STORAGE_KEY)
                return data ? JSON.parse(data) : null
            }
            catch (error) {
                console.error('Failed to load guest profile from localStorage:', error)
                return null
            }
        }
        return null
    }

    function saveGuestProfile(profile: UserPreference) {
        if (import.meta.client) {
            try {
                localStorage.setItem(GUEST_STORAGE_KEY, JSON.stringify(profile))
            }
            catch (error) {
                console.error('Failed to save guest profile to localStorage:', error)
                throw error
            }
        }
    }

    function clearGuestProfile() {
        if (import.meta.client) {
            try {
                localStorage.removeItem(GUEST_STORAGE_KEY)
            }
            catch (error) {
                console.error('Failed to clear guest profile from localStorage:', error)
            }
        }
        guestProfile.value = { ...DEFAULT_GUEST_PROFILE }
    }

    // Initialize on client mount only
    onMounted(() => {
        const stored = loadGuestProfile()
        if (stored) {
            guestProfile.value = { ...DEFAULT_GUEST_PROFILE, ...stored }
        }
        isLoaded.value = true
    })

    return {
        guestProfile: computed(() => guestProfile.value),
        isLoaded,
        saveGuestProfile,
        clearGuestProfile,
    }
}
