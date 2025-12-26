<script setup>
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { LayoutDashboard, Settings, Zap, ScrollText, BookMarked } from 'lucide-vue-next'

const route = useRoute()

const isActive = (path) => route.path === path
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex font-sans">
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-900 text-white flex flex-col fixed h-full z-10 transition-all duration-300">
      <div class="p-6 flex items-center gap-3">
        <div class="p-2 bg-indigo-600 rounded-lg">
          <Zap class="w-6 h-6 text-white" />
        </div>
        <span class="text-xl font-bold tracking-tight">Buddy Probe</span>
      </div>

      <nav class="flex-1 px-4 py-8 space-y-2">
        <RouterLink to="/" 
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200"
          :class="isActive('/') ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'">
          <LayoutDashboard class="w-5 h-5" />
          <span class="font-medium">情报大盘</span>
        </RouterLink>

        <RouterLink to="/settings" 
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200"
          :class="isActive('/settings') ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'">
          <Settings class="w-5 h-5" />
          <span class="font-medium">配置中心</span>
        </RouterLink>

        <RouterLink to="/scripts" 
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200"
          :class="isActive('/scripts') ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'">
          <ScrollText class="w-5 h-5" />
          <span class="font-medium">脚本模版</span>
        </RouterLink>

        <RouterLink to="/topics" 
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors duration-200"
          :class="isActive('/topics') ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'">
          <BookMarked class="w-5 h-5" />
          <span class="font-medium">选题库</span>
        </RouterLink>
      </nav>

      <div class="p-4 border-t border-slate-800">
        <div class="flex items-center gap-3 px-4 py-3">
          <div class="w-8 h-8 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center text-xs font-bold text-white">
            AX
          </div>
          <div>
            <div class="text-sm font-medium">Alex</div>
            <div class="text-xs text-slate-500">Pro Plan</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 ml-64 p-8">
      <RouterView />
    </main>
  </div>
</template>
