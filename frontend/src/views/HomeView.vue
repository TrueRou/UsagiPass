<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import QRCode, { type QRCodeToDataURLOptions } from 'qrcode'
import { useUserStore } from '@/stores/user';
import { useServerStore } from '@/stores/server';
import { useRouter } from 'vue-router';


let lastFrameStatus = -1;
let eventCounter = 0;
const ratingLevels = [
    1000,
    2000,
    4000,
    7000,
    10000,
    12000,
    13000,
    14000,
    14500,
    15000,
]
const qrcodeOpts = {
    errorCorrectionLevel: 'L',
    type: 'image/jpeg',
    quality: 0.3,
    margin: 1
} as QRCodeToDataURLOptions

const overlayStyle = ref({})
const medalStyle = ref({})
const ratingStyle = ref({})
const userInfoStyle = ref({})
const userProfile = ref<UserProfile>()
const timeLimit = ref("12:00:00")
const router = useRouter()

const ratingImg = computed(() => {
    const arr = String(userProfile.value?.preferences.dx_rating).split('')
    while (arr.length < 5) arr.unshift('10');
    return arr.map(num => getStaticNumImage(num));
})

const borderImg = computed(() => {
    var rating = userProfile.value?.preferences.dx_rating || 0;
    rating = Math.max(ratingLevels[0], Math.min(rating, ratingLevels[9]));
    let stage = 0;
    while (rating >= ratingLevels[stage + 1]) stage++;
    return getStaticRatingImage(String(stage + 1));
})

function eventComplete() {
    eventCounter++;
    if (eventCounter === 3) {
        updateWidth();
    }
}

function getStaticNumImage(id: string) {
    return new URL(`../assets/rating/num/UI_CMN_Num_26p_${id}.png`, import.meta.url).href
}

function getStaticRatingImage(id: string) {
    return new URL(`../assets/rating/UI_CMA_Rating_Base_${id}.png`, import.meta.url).href
}

const r = (resource_key: ImagePublic | undefined) => {
    if (!resource_key) return ""
    return import.meta.env.VITE_URL + "/images/" + resource_key!.id
}

const setDefaultPreferences = () => {
    const userStore = useUserStore();
    const serverStore = useServerStore();
    userProfile.value!.preferences.character_name ||= userProfile.value!.preferences.character.name;
    userProfile.value!.preferences.display_name ||= userProfile.value!.nickname;
    userProfile.value!.preferences.dx_rating ||= userProfile.value!.player_rating;
    userProfile.value!.preferences.friend_code ||= "664994421382429" // this is my friend code
    userProfile.value!.preferences.simplified_code ||= userStore.simplifiedCode;
    userProfile.value!.preferences.maimai_version ||= serverStore.serverMessage!.maimai_version;
}

const updateWidth = () => {
    const cardBg = document.getElementById('card-bg') as HTMLImageElement;
    const offset = (window.innerWidth - cardBg!.clientWidth) / 2
    redrawImage(offset); // redraw the frame
    overlayStyle.value = {
        left: `${offset}px`,
        width: `${cardBg!.clientWidth}px`
    }
    medalStyle.value = {
        height: `${offset < 5 ? 8 : 12}%`,
        top: `${offset < 5 ? 0.8 : 0}%`
    }
    ratingStyle.value = {
        height: `${offset < 5 ? 6 : 8}%`,
        top: `${offset < 5 ? 2.5 : 2}%`
    }
    userInfoStyle.value = {
        width: `50%`,
        top: `${offset < 5 ? 9.5 : 10.5}%`,
        right: `0px`
    }
};

const redrawImage = (offset: number) => {
    const frameStatus = offset < 5 ? 1 : 0
    if (lastFrameStatus === frameStatus) return
    // if the frame is uploaded by the user, don't redraw the frame
    if (userProfile.value?.preferences.frame.uploaded_by) return
    lastFrameStatus = frameStatus

    const startY = 100;
    const endY = 200;

    const cardFrSource = document.getElementById('card-fr-source') as HTMLImageElement;
    const cardFr = document.getElementById('card-fr') as HTMLImageElement;
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    canvas.width = cardFrSource.naturalWidth;
    canvas.height = cardFrSource.naturalHeight;
    ctx!.drawImage(cardFrSource, 0, 0);
    var imageData = ctx!.getImageData(0, 0, canvas.width, canvas.height);
    var data = imageData.data;

    if (frameStatus === 1) {
        // remove the upper bottom of the frame
        for (var y = startY; y < endY; y++) {
            for (var x = 0; x < canvas.width; x++) {
                var index = (y * canvas.width + x) * 4;
                data[index + 3] = 0;
            }
        }
    }

    ctx!.putImageData(imageData, 0, 0);
    cardFr.src = canvas.toDataURL('image/png');
}

const routeSettings = () => {
    router.push({ name: 'settings' })
}

onMounted(() => {
    const userStore = useUserStore();
    if (router.currentRoute.value.query.maid) userStore.maimaiCode = router.currentRoute.value.query.maid as string
    if (router.currentRoute.value.query.time) userStore.timeLimit = router.currentRoute.value.query.time as string

    const cardBg = document.getElementById('card-bg') as HTMLImageElement;
    const cardFr = document.getElementById('card-fr') as HTMLImageElement;
    const overlayRating = document.getElementById('overlay-rating') as HTMLImageElement;
    const cardFrSource = document.getElementById('card-fr-source');
    const qrcodeImage = document.getElementById('overlay-qrcode-img') as HTMLImageElement;
    cardBg?.addEventListener('load', eventComplete);
    cardFr?.addEventListener('load', eventComplete);
    overlayRating?.addEventListener('load', eventComplete);
    cardFrSource?.addEventListener('load', () => redrawImage(-1));
    cardFrSource?.setAttribute('crossOrigin', 'anonymous');
    window.addEventListener('resize', updateWidth);
    if (userStore.maimaiCode) {
        QRCode.toDataURL("SGWC" + userStore.maimaiCode, qrcodeOpts, (err, url) => {
            if (err) console.error(err)
            qrcodeImage!.src = url
        })
    }
    userProfile.value = userStore.userProfile! // we can promise it's not null
    timeLimit.value = userStore.timeLimit
    setDefaultPreferences() // set default preferences if the field is empty
});

</script>

<template>
    <img id="card-fr-source" style="display: none;" :src="r(userProfile?.preferences.frame)">
    <div id="background" class="flex flex-col items-center justify-center h-full w-full">
        <img id="card-bg" class="h-full absolute object-cover -z-30" :src="r(userProfile?.preferences.background)">
        <img id="card-fr" style="object-position: 0" class="h-full absolute object-cover -z-10">
    </div>
    <div id="overlay" class="absolute h-full top-0" :style="overlayStyle">
        <img id="overlay-medal" class="absolute object-cover left-0" :style="medalStyle"
            :src="r(userProfile?.preferences.passname)">
        <img id="overlay-rating" class="absolute object-cover right-0" :style="ratingStyle" :src="borderImg">
        <div class="flex absolute object-cover right-0" style="margin-right: 2%; margin-top: 3%;" :style="ratingStyle">
            <img v-for="path in ratingImg" style="height: 46%; width: 46%;" :src="path">
        </div>
        <img id="overlay-chara" class="absolute object-cover -z-20" :src="r(userProfile?.preferences.character)"
            style="left: 50%; top: 50%; transform:translate(-50%,-50%);">
        <div id="overlay-user-info" class="absolute bg-white right-0 flex flex-col rounded-md pt-1"
            :style="userInfoStyle">
            <div class="flex items-center p-1" style="height: 3vh;">
                <p style="font-family: FOTSeurat; font-size: 3vh;">{{ userProfile?.preferences.display_name }}</p>
                <img class="ml-1" style="height: 3.5vh;" src="../assets/misc/UI_CMN_Name_DX.png">
            </div>
            <div class="flex items-center mt-1" style="height: 3vh;">
                <p class="text-white pl-2 pr-2 text-center font-extrabold rounded-bl-md"
                    style="font-size: 1vh; background-color: #405baa; -webkit-text-stroke: 1px #fff">
                    フレンド<br>コ一ド
                </p>
                <p class="ml-0.5" style="font-family: FOTSeurat; font-size: 1.4vh">{{
                    userProfile?.preferences.friend_code }}</p>
            </div>
        </div>
        <div id="overlay-chara-info" class="absolute flex flex-col left-0" style="width: 100%; bottom: 16%;">
            <div class="flex flex-col pt-1 pb-1 rounded-tr-lg" style="width: 33%; background-color: #fee37c;">
                <p class="text-center" style="font-size: 1.6vh;">{{ userProfile?.preferences.character_name }}</p>
            </div>
            <div class="flex flex-col pb-1 rounded-tr-lg rounded-br-lg shadow-xl"
                style="width: 37%; background-color: #fee37c;">
                <p class="text-center" style="font-size: 1.4vh;">ブ一スト期限
                    <b class="ml-2" style="font-size: 1.6vh;">{{ timeLimit }}</b>
                </p>
            </div>
        </div>
        <div id="overlay-chara-info" class="absolute flex flex-col left-0 items-center"
            style="width: 100%; bottom: 1.6%;">
            <div class="flex justify-between pt-1 pb-1 rounded-2xl bg-gray-800 text-white opacity-85"
                style="width: 80%; padding-left: 3%; padding-right: 3%;">
                <p style="font-size: 1.2vh; font-family: FOTSeurat; line-height: 120%;">{{
                    userProfile?.preferences.simplified_code }}</p>
                <p style="font-size: 1.2vh; font-family: FOTSeurat; line-height: 120%;">{{
                    userProfile?.preferences.maimai_version }}</p>
            </div>
        </div>
        <div id="overlay-qrcode" class="absolute p-0.5 rounded bg-white" style="bottom: 6%; left: 65%;">
            <img id="overlay-qrcode-img" :style="{ width: userProfile?.preferences.qr_size }"></img>
        </div>
        <div id="overlay-qrcode" class="absolute p-1 rounded-full bg-white" style="bottom: 1%; right: 1.2%;"
            @click="routeSettings">
            <img src="../assets/misc/settings.svg" style="width: 3vh;"></img>
        </div>
    </div>
</template>
