import { z } from 'zod'

export interface ValidationErrors {
    [key: string]: string
}

export function useFormValidation<T extends Record<string, any>>(schema: z.ZodSchema<T>, form: Ref<T> | T) {
    const errors = ref<ValidationErrors>({})
    const isValid = ref(true)

    const validate = () => {
        errors.value = {}
        isValid.value = true

        try {
            const formData = unref(form)
            schema.parse(formData)
            return true
        }
        catch (error) {
            if (error instanceof z.ZodError) {
                error.issues.forEach((issue) => {
                    const field = issue.path[0] as string
                    errors.value[field] = issue.message
                })
                isValid.value = false
            }
            return false
        }
    }

    const validateField = (field: string) => {
        try {
            const formData = unref(form)
            schema.parse(formData)
            delete errors.value[field]
            return true
        }
        catch (error) {
            if (error instanceof z.ZodError) {
                const fieldError = error.issues.find(issue => issue.path[0] === field)
                if (fieldError) {
                    errors.value[field] = fieldError.message
                }
            }
            return false
        }
    }

    const clearErrors = () => {
        errors.value = {}
        isValid.value = true
    }

    const clearFieldError = (field: string) => {
        delete errors.value[field]
    }

    const getFieldError = (field: string) => {
        return errors.value[field] || null
    }

    return {
        errors: readonly(errors),
        isValid: readonly(isValid),
        validate,
        validateField,
        clearErrors,
        clearFieldError,
        ve: getFieldError,
    }
}
