declare module '#auth-utils' {
    interface User {
        id: string
        username: string
        email: string
        permissions: string[]
    }

    interface UserSession {
        // Add your own fields
    }

    interface SecureSessionData {
        accessToken: string
        refreshToken: string
        expiresAt: number
    }
}

export { }
