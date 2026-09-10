declare module '#auth-utils' {
    interface User {
        id: string
        username: string
        email: string
        roles: string[]
    }

    interface UserSession {
        // Add your own fields
    }

    interface SecureSessionData {
        accessToken: string
        refreshToken: string
    }
}

export { }
