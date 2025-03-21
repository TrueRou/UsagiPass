import { useNotificationStore } from "./stores/notification";
import type { Card } from "./types";

const matchPhoneNumber = (phoneNumber: string) => {
    const notificationStore = useNotificationStore();
    const re = /^(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$/;
    const result = re.test(phoneNumber);
    if (!result) notificationStore.warning("格式错误", "请输入正确的手机号码");
    return result;
}

const getShortUuid = (uuid: string) => {
    return uuid.substring(0, 6);
};

const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    });
};

const getOrderStatus = (card: Card) => {
    if (card.user_id && card.card_id) return '已激活';
    return card.card_id ? '已确认' : '草稿';
};

export { matchPhoneNumber, getShortUuid, formatDate, getOrderStatus };