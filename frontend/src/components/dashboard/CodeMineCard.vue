<script setup>
import { ref } from 'vue'
import { Star, TrendingUp, Sparkles } from 'lucide-vue-next'

const props = defineProps({
  repo: {
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

const openRepo = () => {
    if (props.repo.url) {
        window.open(props.repo.url, '_blank')
    }
}
</script>

<template>
  <div 
    class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-all relative group cursor-pointer flex flex-col overflow-hidden"
    @mouseenter="startHover"
    @mouseleave="endHover"
    @click="openRepo"
  >
    <!-- Top Row: Stats -->
    <div class="flex items-center gap-3 text-sm text-slate-600 mb-2">
      <div class="flex items-center gap-1 bg-amber-50 text-amber-600 px-2 py-0.5 rounded-full">
        <Star class="w-3.5 h-3.5 fill-amber-600" />
        <span class="font-bold text-xs">{{ (repo.stars / 1000).toFixed(1) }}k</span>
      </div>
      <div class="flex items-center gap-1 bg-emerald-50 text-emerald-600 px-2 py-0.5 rounded-full">
        <TrendingUp class="w-3.5 h-3.5" />
        <span class="font-bold text-xs">+{{ repo.todayStars }}</span>
      </div>
    </div>
    
    <!-- Title -->
    <h3 class="font-bold text-slate-800 text-lg mb-2 group-hover:text-indigo-600 transition-colors leading-tight">{{ repo.name }}</h3>

    <!-- Description -->
    <p class="text-slate-500 text-sm leading-relaxed mb-2">{{ repo.description }}</p>

    <!-- AI Summary (Expandable) -->
    <div 
        class="grid transition-all duration-300 ease-in-out"
        :class="showSummary ? 'grid-rows-[1fr] opacity-100 pt-2 border-t border-indigo-100 border-dashed mt-1' : 'grid-rows-[0fr] opacity-0'"
    >
        <div class="overflow-hidden">
            <div class="bg-indigo-50/50 rounded-lg p-3">
                 <div class="flex gap-2 items-start">
                    <Sparkles class="w-4 h-4 text-indigo-600 mt-0.5 shrink-0" />
                    <div class="flex-1">
                        <p class="text-xs font-bold text-indigo-600 mb-1">AI 核心功能总结</p>
                        <p class="text-sm text-slate-700 leading-relaxed font-medium">
                            {{ repo.aiSummary || 'AI 正在解析该项目的核心价值与应用场景...' }}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>
