<script setup>
import { ArrowUpRight } from 'lucide-vue-next'

defineProps({
  items: {
    type: Array,
    required: true
  }
})
</script>

<template>
  <div class="space-y-3">
    <div v-for="(item, index) in items" :key]
      ="item.id" 
      class="bg-white p-3 rounded-lg border border-slate-200 shadow-sm flex items-center gap-3 group cursor-pointer hover:border-indigo-200 hover:shadow-md transition-all relative overflow-hidden">
      
      <!-- Rank -->
      <div class="text-2xl font-black text-slate-100 group-hover:text-indigo-50 transition-colors italic w-8 text-center shrink-0">
        {{ index + 1 }}
      </div>
      
      <div class="flex-1 min-w-0 z-10">
        <h4 class="font-medium text-slate-700 truncate group-hover:text-indigo-700 transition-colors">{{ item.title }}</h4>
        <div class="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
            <span class="bg-slate-100 px-1.5 py-0.5 rounded text-slate-500 group-hover:bg-indigo-50 group-hover:text-indigo-500 transition-colors">{{ item.source }}</span>
            <span>{{ item.heat }} 热度</span>
        </div>
      </div>

      <ArrowUpRight class="w-4 h-4 text-slate-300 group-hover:text-indigo-400 transition-colors shrink-0" />
      
      <!-- Tape effect -->
      <div class="absolute -left-1 top-1/2 -translate-y-1/2 w-1.5 h-8 bg-slate-200/50 rounded-r"></div>
    </div>
  </div>
</template>
