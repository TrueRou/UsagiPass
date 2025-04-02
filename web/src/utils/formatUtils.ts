import { useNotificationStore } from "../stores/notification";

export const getShortUuid = (uuid: string) => {
    return uuid.substring(0, 8);
};

export const formatDate = (dateString: string) => {
    const date = new Date(dateString + "Z");
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
};

export const formatDateDetailed = (dateString: string) => {
    const date = new Date(dateString + "Z");
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
};

export const matchPhoneNumber = (phoneNumber: string) => {
    const notificationStore = useNotificationStore();
    const re = /^(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$/;
    const result = re.test(phoneNumber);
    if (!result) notificationStore.warning("格式错误", "请输入正确的手机号码");
    return result;
};