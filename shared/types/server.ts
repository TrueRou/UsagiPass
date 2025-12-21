export type ServerCredentialsField = 'username' | 'credentials' | 'friend_code'

export interface UpdatesChainTargetBody {
    [serverIdentifier: string]: {
        username?: string
        credentials?: string
        friend_code?: string
    }
}
