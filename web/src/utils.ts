import { useNotificationStore } from "./stores/notification";

const matchPhoneNumber = (phoneNumber: string) => {
    const notificationStore = useNotificationStore();
    const re = /^(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$/;
    const result = re.test(phoneNumber);
    if (!result) notificationStore.warning("格式错误", "请输入正确的手机号码");
    return result;
}

const getShortUuid = (uuid: string) => {
    return uuid.substring(0, 8);
};

const formatDate = (dateString: string) => {
    const date = new Date(dateString + "Z");
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
};

const formatDateDetailed = (dateString: string) => {
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

const ensureNfcSupport = () => {
    const notificationStore = useNotificationStore();

    if (!('NDEFReader' in window)) {
        notificationStore.warning("不支持NFC", "您的浏览器或设备不支持Web NFC功能");
        return null;
    }

    return new (window as any).NDEFReader();
}

const readUuidFromNfc = async (): Promise<string | null> => {
    const notificationStore = useNotificationStore();
    const ndef = ensureNfcSupport();
    if (!ndef) return null;

    try {
        await ndef.scan();
        return new Promise((resolve) => {
            ndef.onreadingerror = () => {
                notificationStore.error("读取失败", "NFC卡片读取失败");
                resolve(null);
            };
            ndef.onreading = (event: any) => {
                const message = event.message;
                if (message.records.length >= 1 && message.records[0].recordType === "url") {
                    const decoder = new TextDecoder();
                    const urlData = decoder.decode(message.records[0].data);
                    const uuid = urlData.substring(urlData.lastIndexOf("/") + 1);
                    resolve(uuid);
                } else {
                    notificationStore.error("读取失败", "该NFC卡片不是UsagiCard卡片");
                    resolve(null);
                }
            };
        });
    } catch (error) {
        notificationStore.error("读取失败", error instanceof Error ? error.message : "未知错误");
        return null;
    }
}

const writeUuidToNfc = async (uuid: string, mode: ("normal" | "fast") = "fast"): Promise<boolean> => {
    const notificationStore = useNotificationStore();
    const ndef = ensureNfcSupport();
    if (!ndef) return false;

    const recordsMap = {
        "normal": [{
            recordType: "url",
            data: `https://up.turou.fun/cards/${uuid}`
        }],
        "fast": [
            {
                recordType: "url",
                data: `https://up.turou.fun/cards/${uuid}`
            },
            {
                recordType: "android.com:pkg",
                data: new TextEncoder().encode("alook.browser")
            },
            {
                recordType: "android.com:pkg",
                data: new TextEncoder().encode("com.android.chrome")
            },
            {
                recordType: "android.com:pkg",
                data: new TextEncoder().encode("com.microsoft.emmx")
            },
            {
                recordType: "android.com:pkg",
                data: new TextEncoder().encode("com.qihoo.browser")
            },
            {
                recordType: "android.com:pkg",
                data: new TextEncoder().encode("com.android.browser")
            },
        ]
    }

    try {
        notificationStore.info("写入中", "请将NFC卡片靠近手机背面");
        await ndef.write({ records: recordsMap[mode] });
        notificationStore.success("写卡成功", "NFC卡片已成功写入");
        return true;
    } catch (error) {
        notificationStore.error("写卡失败", error instanceof Error ? error.message : "未知错误");
        return false;
    }
};
export { matchPhoneNumber, getShortUuid, formatDate, formatDateDetailed, readUuidFromNfc, writeUuidToNfc };