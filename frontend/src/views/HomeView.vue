<script setup lang="ts">
import { ref, onMounted } from 'vue';
import QRCode, { type QRCodeToDataURLOptions } from 'qrcode'
import { useUserStore } from '@/stores/user';
import { useServerStore } from '@/stores/server';

let lastFrameStatus = -1;
const overlayStyle = ref({})
const medalStyle = ref({})
const ratingStyle = ref({})
const userInfoStyle = ref({})

const userProfile = ref<UserProfile>()

const qrcodeOpts = {
    errorCorrectionLevel: 'L',
    type: 'image/jpeg',
    quality: 0.3,
    margin: 1
} as QRCodeToDataURLOptions

const setDefaultPreferences = () => {

}

const r = (resource_key: string) => {
    return import.meta.env.VITE_URL + "/images/" + resource_key
}

const updateWidth = () => {
    const cardBg = document.getElementById('card-bg') as HTMLImageElement;
    const overlayRating = document.getElementById('overlay-rating') as HTMLImageElement;
    const offset = (window.innerWidth - cardBg!.clientWidth) / 2
    redrawImage(offset); // redraw the frame
    overlayStyle.value = {
        left: `${offset}px`,
        width: `${cardBg!.clientWidth}px`
    }
    medalStyle.value = {
        height: `${offset === 0 ? 8 : 12}%`,
        top: `${offset === 0 ? 0.8 : 0}%`
    }
    ratingStyle.value = {
        height: `${offset === 0 ? 6 : 8}%`,
        top: `${offset === 0 ? 2.5 : 2}%`
    }
    userInfoStyle.value = {
        width: `${offset === 0 ? overlayRating.width : 170}px`,
        top: `${offset === 0 ? 9.5 : 10.5}%`,
        right: `${offset === 0 ? 0 : overlayRating.width - 170}px`
    }
};

const redrawImage = (offset: number) => {
    const frameStatus = offset === 0 ? 1 : 0
    if (lastFrameStatus === frameStatus) return
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

onMounted(() => {
    const userStore = useUserStore();
    const serverStore = useServerStore();
    const cardBg = document.getElementById('card-bg');
    const cardFr = document.getElementById('card-fr');
    const cardFrSource = document.getElementById('card-fr-source');
    const qrcodeImage = document.getElementById('overlay-qrcode-img') as HTMLImageElement;
    cardBg?.addEventListener('load', updateWidth);
    cardFr?.addEventListener('load', updateWidth);
    cardFrSource?.addEventListener('load', () => redrawImage(-1));
    window.addEventListener('resize', updateWidth);
    QRCode.toDataURL(userStore.maimaiCode, qrcodeOpts, (err, url) => {
        if (err) console.error(err)
        qrcodeImage!.src = url
    })
    userProfile.value = userStore.userProfile! // we can promise it's not null
    if (!userProfile.value.preferences.simplified_code) {
        userProfile.value.preferences.simplified_code = userStore.simplifiedCode
    }
    if (!userProfile.value.preferences.maimai_version) {
        userProfile.value.preferences.maimai_version = serverStore.serverMessage?.maimai_version
    }
    setDefaultPreferences() // set default preferences if the field is empty
});

</script>

<template>
    <img id="card-fr-source" style="display: none;" src="../assets/frame/UI_CMA_Card_Frame_00_Gold.png">
    <div id="background" class="flex flex-col items-center justify-center h-full w-full">
        <img id="card-bg" class="h-full absolute object-cover -z-30"
            src="../assets/base/UI_CardBase_0000002_000001.png">
        <img id="card-fr" style="object-position: 0" class="h-full absolute object-cover -z-10">
    </div>
    <div id="overlay" class="absolute h-full top-0" :style="overlayStyle">
        <img id="overlay-medal" class="absolute object-cover left-0" :style="medalStyle"
            src="../assets/frame/UI_CMA_PassName_01.png">
        <img id="overlay-rating" class="absolute object-cover right-0" :style="ratingStyle"
            src="../assets/rating/UI_CMA_Rating_Base_03.png">
        <img id="overlay-chara" class="absolute object-cover bottom-0 -z-20"
            src="../assets/chara/UI_CardChara_000201.png">
        <div id="overlay-user-info" class="absolute bg-white right-0 flex flex-col rounded-md pt-1"
            :style="userInfoStyle">
            <div class="flex items-center p-1" style="height: 3vh;">
                <p style="font-family: FOTSeurat; font-size: 3vh;">TuRou</p>
                <img class="ml-1" style="height: 3.5vh;"
                    src="../assets/misc/UI_CMN_Name_DX-topaz-sharpen-textai-enhance-4x.png">
            </div>
            <div class="flex items-center mt-1" style="height: 3vh;">
                <p class="text-white pl-2 pr-2 text-center font-extrabold rounded-bl-md"
                    style="font-size: 1vh; background-color: #405baa; -webkit-text-stroke: 1px #fff">
                    フレンド<br>コ一ド
                </p>
                <p class="ml-0.5" style="font-family: FOTSeurat; font-size: 1.6vh">211851246666024</p>
            </div>
        </div>
        <div id="overlay-chara-info" class="absolute flex flex-col left-0" style="width: 100%; bottom: 16%;">
            <div class="flex flex-col pt-1 pb-1 rounded-tr-lg" style="width: 33%; background-color: #fee37c;">
                <p class="text-center" style="font-size: 1.6vh;">Chara Name</p>
            </div>
            <div class="flex flex-col pb-1 rounded-tr-lg rounded-br-lg shadow-xl"
                style="width: 37%; background-color: #fee37c;">
                <p class="text-center" style="font-size: 1.4vh;">ブ一スト期限
                    <b class="ml-2" style="font-size: 2vh;">11:53:66</b>
                </p>
            </div>
        </div>
        <div id="overlay-chara-info" class="absolute flex flex-col left-0 items-center"
            style="width: 100%; bottom: 1.6%;">
            <div class="flex justify-between pt-1 pb-1 rounded-2xl bg-gray-800 text-white opacity-85"
                style="width: 80%; padding-left: 3%; padding-right: 3%;">
                <p style="font-size: 1.6vh; font-family: FOTSeurat; line-height: 120%;">{{
                    userProfile?.preferences.simplified_code }}</p>
                <p style="font-size: 1.6vh; font-family: FOTSeurat; line-height: 120%;">{{
                    userProfile?.preferences.maimai_version }}</p>
            </div>
        </div>
        <div id="overlay-qrcode" class="absolute p-0.5 rounded bg-white" style="bottom: 6%; right: 8%;">
            <img id="overlay-qrcode-img" style="width: 15vh;"></img>
        </div>
    </div>
</template>
