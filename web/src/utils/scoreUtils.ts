import type { FCType, FSType } from '@/types';

// 获取成绩难度颜色
export function getDifficultyColor(levelIndex: number): string {
    const colors: { [key: number]: string } = {
        0: '#6fe163', // BASIC
        1: '#ffd653', // ADVANCED
        2: '#ff7b7b', // EXPERT
        3: '#9f51dc', // MASTER
        4: '#dbaaff', // Re:MASTER
    };
    return colors[levelIndex] || '#26c9fc';
}

// 获取成绩评级样式
export function getAchievementStyle(achievements: number | null) {
    if (!achievements) return { class: 'bg-gray-500', text: '-', name: '-', color: 'bg-gray-500' };

    if (achievements >= 100.5) return { name: 'SSS+', class: 'bg-purple-600', text: 'SSS+', color: 'bg-purple-600' };
    if (achievements >= 100) return { name: 'SSS', class: 'bg-purple-500', text: 'SSS', color: 'bg-purple-500' };
    if (achievements >= 99.5) return { name: 'SS+', class: 'bg-yellow-500', text: 'SS+', color: 'bg-yellow-500' };
    if (achievements >= 99) return { name: 'SS', class: 'bg-yellow-400', text: 'SS', color: 'bg-yellow-400' };
    if (achievements >= 98) return { name: 'S+', class: 'bg-green-600', text: 'S+', color: 'bg-green-600' };
    if (achievements >= 97) return { name: 'S', class: 'bg-green-500', text: 'S', color: 'bg-green-500' };
    if (achievements >= 94) return { name: 'AAA', class: 'bg-blue-600', text: 'AAA', color: 'bg-blue-600' };
    if (achievements >= 90) return { name: 'AA', class: 'bg-blue-500', text: 'AA', color: 'bg-blue-500' };
    if (achievements >= 80) return { name: 'A', class: 'bg-blue-400', text: 'A', color: 'bg-blue-400' };
    return { name: 'B', class: 'bg-gray-500', text: 'B', color: 'bg-gray-500' };
}

// 获取评级图标的URL
export function getAchievementIconSrc(achievements: number | null) {
    if (!achievements) return undefined;

    const rankIcons: { [key: string]: string } = {
        'SSS+': new URL('../assets/bonus/UI_TTR_Rank_SSSp.png', import.meta.url).href,
        'SSS': new URL('../assets/bonus/UI_TTR_Rank_SSS.png', import.meta.url).href,
        'SS+': new URL('../assets/bonus/UI_TTR_Rank_SSp.png', import.meta.url).href,
        'SS': new URL('../assets/bonus/UI_TTR_Rank_SS.png', import.meta.url).href,
        'S+': new URL('../assets/bonus/UI_TTR_Rank_Sp.png', import.meta.url).href,
        'S': new URL('../assets/bonus/UI_TTR_Rank_S.png', import.meta.url).href,
        'AAA': new URL('../assets/bonus/UI_TTR_Rank_AAA.png', import.meta.url).href,
        'AA': new URL('../assets/bonus/UI_TTR_Rank_AA.png', import.meta.url).href,
        'A': new URL('../assets/bonus/UI_TTR_Rank_A.png', import.meta.url).href,
        'BBB': new URL('../assets/bonus/UI_TTR_Rank_BBB.png', import.meta.url).href,
        'BB': new URL('../assets/bonus/UI_TTR_Rank_BB.png', import.meta.url).href,
        'B': new URL('../assets/bonus/UI_TTR_Rank_B.png', import.meta.url).href,
        'C': new URL('../assets/bonus/UI_TTR_Rank_C.png', import.meta.url).href,
        'D': new URL('../assets/bonus/UI_TTR_Rank_D.png', import.meta.url).href,
    };

    const style = getAchievementStyle(achievements);
    return rankIcons[style.name];
}

// 获取歌曲类型标签
export function getSongTypeLabel(type: string) {
    const types = {
        'standard': { name: 'SD', color: 'bg-blue-500' },
        'dx': { name: 'DX', color: 'bg-orange-500' },
        'utage': { name: 'UT', color: 'bg-red-800' }
    };

    return types[type as keyof typeof types] || { name: '标准', color: 'bg-blue-500' };
}

// 将FC状态转换为显示文本
export function getFCText(fc: FCType | null, useNoFC = false) {
    if (fc === null) return useNoFC ? 'NO FC' : '无';
    const fcMap = {
        0: 'AP+',
        1: 'AP',
        2: 'FC+',
        3: 'FC'
    };
    return fcMap[fc as FCType] || (useNoFC ? 'NO FC' : '无');
}

// 将FS状态转换为显示文本
export function getFSText(fs: FSType | null, useNoFS = false) {
    if (fs === null) return useNoFS ? 'NO FS' : '无';
    const fsMap = {
        0: 'SYNC',
        1: 'FS',
        2: 'FS+',
        3: 'FSD',
        4: 'FSD+'
    };
    return fsMap[fs as FSType] || (useNoFS ? 'NO FS' : '无');
}

// 获取FC图标的URL
export function getFCIconSrc(fc: FCType | null) {
    if (fc === null) return undefined;
    const fcIcons = {
        0: new URL('../assets/bonus/UI_MSS_MBase_Icon_APp.png', import.meta.url).href,   // APP
        1: new URL('../assets/bonus/UI_MSS_MBase_Icon_AP.png', import.meta.url).href,    // AP
        2: new URL('../assets/bonus/UI_MSS_MBase_Icon_FCp.png', import.meta.url).href,   // FCP
        3: new URL('../assets/bonus/UI_MSS_MBase_Icon_FC.png', import.meta.url).href,    // FC
    };
    return fcIcons[fc];
}

// 获取FS图标的URL
export function getFSIconSrc(fs: FSType | null) {
    if (fs === null) return undefined;
    const fsIcons = {
        0: new URL('../assets/bonus/UI_MSS_MBase_Icon_Sync.png', import.meta.url).href,  // SYNC
        1: new URL('../assets/bonus/UI_MSS_MBase_Icon_FS.png', import.meta.url).href,    // FS
        2: new URL('../assets/bonus/UI_MSS_MBase_Icon_FSp.png', import.meta.url).href,   // FSP
        3: new URL('../assets/bonus/UI_MSS_MBase_Icon_FSD.png', import.meta.url).href,   // FSD
        4: new URL('../assets/bonus/UI_MSS_MBase_Icon_FSDp.png', import.meta.url).href,  // FSDP
    };
    return fsIcons[fs];
}

// 处理封面图加载错误
export function handleImageError(event: Event) {
    const target = event.target as HTMLImageElement;
    target.src = 'https://via.placeholder.com/80?text=No+Image';
}

// 获取歌曲封面URL
export function getSongJacketUrl(songId: number | null) {
    if (!songId) return null;
    return `https://assets2.lxns.net/maimai/jacket/${songId}.png`;
}

// 格式化成绩达成率显示
export function formatAchievement(achievement: number | null): string {
    if (!achievement) return '-';
    const intPart = parseInt(String(achievement));
    const decimalPart = (String(achievement).split(".")[1] || "0").padEnd(4, "0");
    return `${intPart}.${decimalPart}%`;
}
