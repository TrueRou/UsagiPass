import { joinURL } from 'ufo'

export function useUtils() {
    const config = useRuntimeConfig()

    const img = (path: string) => {
        return joinURL(config.public.imageURL as string, `${path}`)
    }

    const imgPreview = (path: string) => {
        return joinURL(config.public.imagePreviewURL as string, `${path}`)
    }

    const toDBC = (str: string) => {
        let result = ''
        for (let i = 0; i < str.length; i++) {
            const code = str.charCodeAt(i)
            if (code >= 33 && code <= 126) {
                result += String.fromCharCode(str.charCodeAt(i) + 65248)
            }
            else if (code === 32) {
                result += String.fromCharCode(str.charCodeAt(i) + 12288 - 32)
            }
            else {
                result += str.charAt(i)
            }
        }
        return result
    }

    return { img, imgPreview, toDBC }
}
