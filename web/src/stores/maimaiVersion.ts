import { defineStore } from "pinia";

// 国框舞萌 DX 版本配置
const maimaiVersions = [
    {
        version: "[maimaiDX]CN1.51-E",
        releaseTime: "2025-08-20T10:00:00+08:00"
    },
    {
        version: "[maimaiDX]CN1.51-F", 
        releaseTime: "2025-09-24T10:00:00+08:00"
    }
];

export const useMaimaiVersionStore = defineStore('maimaiVersion', () => {
    // 获取当前版本
    function getCurrentVersion(): string {
        const now = new Date();
        const validVersions = maimaiVersions.filter(v => new Date(v.releaseTime) <= now);
        
        if (validVersions.length === 0) {
            // 如果版本列表为空，返回空字符串或第一个版本
            return maimaiVersions[0]?.version || "";
        }
        
        // 按发布时间排序，返回最新的已发布版本
        const sortedVersions = validVersions.sort((a, b) => 
            new Date(b.releaseTime).getTime() - new Date(a.releaseTime).getTime()
        );
        
        return sortedVersions[0].version;
    }

    return { getCurrentVersion };
});
