<template>
  <div 
    class="group relative bg-white rounded-xl p-3 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300 cursor-pointer flex flex-col gap-2 overflow-hidden"
    @mouseenter="startHover" 
    @mouseleave="endHover"
    @click="openVideo"
  >
    <div class="flex gap-3">
        <!-- Thumbnail (Left) -->
        <div class="relative w-32 shrink-0 aspect-video bg-slate-200 rounded-lg overflow-hidden self-start">
        <img :src="video.thumbnail" :alt="video.title" referrerpolicy="no-referrer" class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500" />
        <div class="absolute inset-0 bg-black/10 group-hover:bg-black/20 transition-colors"></div>
        
        <!-- Duration / Overlay -->
        <div class="absolute bottom-1 right-1 bg-black/60 text-white text-[10px] px-1 rounded">
            12:34
        </div>
        
        <!-- Play Icon -->
        <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <div class="w-8 h-8 bg-white/30 backdrop-blur rounded-full flex items-center justify-center">
                <Play class="w-4 h-4 text-white fill-white" />
            </div>
        </div>
        </div>

        <!-- Info (Right) -->
        <div class="flex-1 min-w-0 flex flex-col justify-between py-1">
        <div>
            <h3 class="font-bold text-slate-800 text-sm leading-tight group-hover:text-indigo-600 transition-colors" :title="video.title">{{ video.title }}</h3>
        </div>

        <!-- Stats & Author -->
        <div class="flex flex-col gap-1.5 mt-2">
            <!-- Author -->
            <div class="flex items-center gap-2 text-xs text-slate-500">
                <img :src="video.authorAvatar" class="w-4 h-4 rounded-full" />
                <span class="truncate">{{ video.author }}</span>
            </div>
            
            <!-- Stats -->
            <div class="flex items-center gap-3 text-xs text-slate-400 font-mono">
                <div class="flex items-center gap-1">
                    <PlayCircle class="w-3 h-3" />
                    <span>{{ formatNumber(video.views) }}</span>
                </div>
                <div class="flex items-center gap-1">
                    <ThumbsUp class="w-3 h-3" />
                    <span>{{ formatNumber(video.likes) }}</span>
                </div>
            </div>
        </div>
        </div>
    </div>

    <!-- AI Summary (Expandable) -->
    <div 
        class="grid transition-all duration-300 ease-in-out"
        :class="showSummary ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'"
    >
        <div class="overflow-hidden">
             <div class="bg-indigo-50 rounded-lg p-2.5 mt-1 border border-indigo-100">
                 <div class="flex gap-2 items-start">
                    <Sparkles class="w-3.5 h-3.5 text-indigo-600 mt-0.5 shrink-0" />
                     <div class="flex-1">
                        <p class="text-xs font-bold text-indigo-600 mb-0.5">视频简介</p>
                        <p class="text-xs text-slate-700 leading-relaxed font-medium line-clamp-4">
                            {{ video.summary || '暂无简介' }}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Play, Sparkles, PlayCircle, ThumbsUp, Star } from 'lucide-vue-next'

const props = defineProps({
  video: {
    type: Object,
    required: true
  }
})

const showSummary = ref(false)
let hoverTimer = null

const startHover = () => {
    hoverTimer = setTimeout(() => {
        showSummary.value = true
    }, 1000)
}

const endHover = () => {
    if (hoverTimer) clearTimeout(hoverTimer)
    showSummary.value = false
}

const openVideo = () => {
    if (props.video.url) {
        window.open(props.video.url, '_blank')
    } else {
        // Fallback or alert for mock
        console.log('No URL for video:', props.video.title)
        window.open('https://www.bilibili.com', '_blank')
    }
}

const formatNumber = (num) => {
    if (!num) return '0'
    if (num >= 10000) {
        return (num / 10000).toFixed(1) + 'w'
    }
    return num
}
</script>
