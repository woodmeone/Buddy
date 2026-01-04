<script setup>
import { ref, watch, onUnmounted, onMounted, onErrorCaptured } from 'vue'
import { Save, User, Hash, MonitorPlay, Rss, Flame, ChevronDown, RefreshCw, CheckCircle2, LayoutDashboard, X } from 'lucide-vue-next'
import { useSettings } from '../composables/useSettings'
import PersonaManager from '../components/settings/PersonaManager.vue'
import { dataService } from '../services/dataService'

const { currentPersona, saveCurrentPersona, currentPersonaId } = useSettings()

const showPersonaManager = ref(false)
const newTag = ref('')

// Helpers
const addTag = () => {
    if (newTag.value.trim() && currentPersona.value) {
        if (!currentPersona.value.interests) currentPersona.value.interests = []
        currentPersona.value.interests.push(newTag.value.trim())
        newTag.value = ''
    }
}

const removeTag = (tag) => {
    if (currentPersona.value && currentPersona.value.interests) {
        currentPersona.value.interests = currentPersona.value.interests.filter(t => t !== tag)
    }
}

const addBilibiliUid = () => {
    if (currentPersona.value) {
        if (!currentPersona.value.bilibiliList) currentPersona.value.bilibiliList = []
        currentPersona.value.bilibiliList.push({ name: '', uid: '', enabled: true, viewsThreshold: 0 })
    }
}

const addRssSource = () => {
    if (currentPersona.value) {
        if (!currentPersona.value.rssList) currentPersona.value.rssList = []
        currentPersona.value.rssList.push({ name: '', url: '', enabled: true })
    }
}

const addHotSource = () => {
    if (currentPersona.value) {
        if (!currentPersona.value.hotSources) currentPersona.value.hotSources = []
        currentPersona.value.hotSources.push({ id: Date.now().toString(), name: '', enabled: true })
    }
}

const isSyncing = ref(false)
const syncProgress = ref(0)
const syncMessage = ref('')
const showSyncToast = ref(false)
let syncTimer = null

// ... existing code ...

const startPolling = () => {
    if (syncTimer) return // Avoid multiple timers
    syncTimer = setInterval(async () => {
        try {
            const status = await dataService.getSyncStatus()
            syncProgress.value = status.progress
            syncMessage.value = status.last_message
            isSyncing.value = status.is_syncing

            if (!status.is_syncing) {
                stopPolling()
                if (status.progress === 100) {
                    showSyncToast.value = true
                    setTimeout(() => {
                        showSyncToast.value = false
                    }, 6000)
                }
            }
        } catch (e) {
            console.error('[Settings] Status polling failed', e)
            stopPolling()
            isSyncing.value = false
        }
    }, 1000)
}

const stopPolling = () => {
    if (syncTimer) {
        clearInterval(syncTimer)
        syncTimer = null
    }
}

onErrorCaptured((err, instance, info) => {
    console.error('[SettingsView] Error Captured:', err)
    console.error('Instance:', instance)
    console.error('Info:', info)
    return false // Stop propagation to prevent global crash
})

onMounted(async () => {
    // Check initial status when component mounts
    try {
        const status = await dataService.getSyncStatus()
        isSyncing.value = status.is_syncing
        syncProgress.value = status.progress
        syncMessage.value = status.last_message
        
        if (status.is_syncing) {
            startPolling()
        }
    } catch (e) {
        console.error('[Settings] Initial status check failed', e)
    }
})

onUnmounted(() => stopPolling())

const handleSync = async () => {
    if (isSyncing.value) return
    
    isSyncing.value = true
    syncProgress.value = 0
    syncMessage.value = '准备同步...'
    
    console.log('[Settings] Starting manual sync...')
    try {
        await dataService.manualSync()
        startPolling()
    } catch (e) {
        console.error('[Settings] Sync failed', e)
        alert('同步失败，请检查网络或配置。')
        isSyncing.value = false
    }
}

const handleSave = async () => {
    await saveCurrentPersona()
    alert('当前人设配置已保存！')
}
</script>

<template>
  <div class="max-w-4xl mx-auto h-full flex flex-col relative">
    
    <!-- Header Area -->
    <div class="mb-8 flex items-end justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <div class="p-1.5 bg-yellow-400 rounded-lg">
            <span class="text-xl">🤔</span>
            </div>
            配置中心
        </h1>
        <p class="text-slate-500 text-sm mt-1">
            当前正在编辑: 
            <span v-if="currentPersona" class="font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                {{ currentPersona.name }}
            </span>
            <span v-else class="text-slate-400">Loading...</span>
        </p>
      </div>
      
      <div class="relative">
          <button 
            @click="showPersonaManager = !showPersonaManager"
            class="flex items-center gap-2 bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-lg font-medium shadow-sm hover:border-indigo-300 hover:text-indigo-600 transition-all"
          >
              <User class="w-4 h-4" />
              切换/管理人设
              <ChevronDown class="w-4 h-4 opacity-50" />
          </button>
          
          <PersonaManager 
            :isOpen="showPersonaManager" 
            @close="showPersonaManager = false"
          />
      </div>
    </div>

    <!-- Main Card -->
    <div v-if="currentPersona && currentPersona.id" class="bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden relative flex-1 min-h-[500px]">
        
        <div class="p-8 grid grid-cols-12 gap-12 h-full overflow-y-auto">
            
            <!-- Left: Avatar -->
            <div class="col-span-12 md:col-span-4 flex flex-col items-center gap-4 border-r border-slate-100 border-dashed pr-8">
                <div class="w-48 h-48 bg-slate-100 rounded-lg border-4 border-slate-200 border-dashed flex items-center justify-center relative group cursor-pointer hover:border-indigo-300 transition-colors">
                    <User class="w-16 h-16 text-slate-300 group-hover:text-indigo-300 transition-colors" />
                    <div class="absolute inset-0 bg-black/5 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-xs font-medium text-slate-600">
                        Change Avatar
                    </div>
                </div>
                <h3 class="font-bold text-lg text-slate-700 text-center">{{ currentPersona.name }}</h3>
                <p class="text-xs text-slate-400 text-center px-4">{{ currentPersona.description || '暂无描述' }}</p>
            </div>

            <!-- Right: Forms -->
            <div class="col-span-12 md:col-span-8 flex flex-col gap-8 pb-20">
                
                <!-- Sliders & Prompts -->
                <div class="space-y-6">
                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <label class="font-bold text-slate-700">专业深度 (Depth)</label>
                            <span class="text-xs font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-500">{{ currentPersona.depth || 5 }}/10</span>
                        </div>
                        <div class="h-8 bg-slate-100 rounded-lg p-1 flex items-center gap-1 border border-slate-200">
                            <div v-for="n in 10" :key="'depth-'+n" 
                                @click="currentPersona.depth = n"
                                class="flex-1 h-full rounded cursor-pointer transition-all duration-200 transform hover:scale-105"
                                :class="n <= (currentPersona.depth || 0) ? 'bg-slate-600 shadow-sm' : 'bg-transparent'">
                            </div>
                        </div>
                    </div>

                    <!-- System Prompt (Read Only / Quick View) -->
                    <div>
                         <div class="flex items-center justify-between mb-2">
                            <label class="font-bold text-slate-700 flex items-center gap-2">
                               人设详细设定 (System Prompt)
                               <span class="text-[10px] font-normal text-white bg-indigo-500 px-1.5 py-0.5 rounded">CORE</span>
                            </label>
                            <button @click="showPersonaManager = true" class="text-xs text-indigo-500 hover:underline">去修改</button>
                        </div>
                        <div class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm text-slate-600 font-mono leading-relaxed h-24 overflow-y-auto">
                            {{ currentPersona.customPrompt }}
                        </div>
                    </div>
                </div>

                <!-- Interests -->
                <div>
                   <label class="font-bold text-slate-700 mb-2 block">喜好 (Interests)</label>
                   <div class="flex flex-wrap gap-2 p-4 bg-slate-50 rounded-xl border border-slate-200 shadow-inner min-h-[80px]">
                        <div v-for="tag in (currentPersona.interests || [])" :key="tag" 
                             class="bg-white border border-slate-300 shadow-sm px-3 py-1.5 rounded-lg flex items-center gap-2 text-sm font-medium text-slate-700 group -rotate-1 hover:rotate-0 transition-transform cursor-default">
                            <Hash class="w-3 h-3 text-slate-400" />
                            {{ tag }}
                            <button @click="removeTag(tag)" class="text-slate-300 hover:text-red-500 ml-1">×</button>
                        </div>
                        
                        <input 
                            v-model="newTag"
                            @keydown.enter="addTag"
                            placeholder="+ Add..." 
                            class="bg-transparent text-sm min-w-[60px] outline-none placeholder:text-slate-400 text-slate-700 px-2"
                        />
                   </div>
                </div>

                <div class="h-px bg-slate-200 w-full dashed"></div>

                <!-- Integration -->
                <div class="space-y-6">
                    <h3 class="font-bold text-slate-700 text-lg">监控源配置 (关闭所有子项以隐藏整列)</h3>

                    <!-- Bilibili UP Owners -->
                    <div class="bg-slate-50 rounded-xl border border-slate-200 overflow-hidden">
                        <div class="px-4 py-3 border-b border-slate-200 bg-slate-100/50 flex items-center justify-between">
                            <div class="flex items-center gap-2 font-medium text-slate-700">
                                <MonitorPlay class="w-4 h-4 text-pink-500" />
                                B 站竞品监控
                            </div>
                            <button @click="addBilibiliUid" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium">+ 添加竞品</button>
                        </div>
                        <div class="p-4 space-y-3">
                            <div v-for="(item, index) in (currentPersona.bilibiliList || [])" :key="index" class="flex items-center gap-3">
                                <input v-model="item.name" placeholder="备注名" class="bg-white border text-sm rounded px-2 py-1 w-24 outline-none focus:border-indigo-400" />
                                <div class="flex-1 flex flex-col gap-1">
                                    <input v-model="item.uid" placeholder="UID (数字)" class="bg-white border text-sm rounded px-2 py-1 outline-none focus:border-indigo-400 font-mono" />
                                    <span class="text-[10px] text-slate-400">UID 为个人空间链接结尾的数字 (e.g. 2267573)</span>
                                </div>
                                <div class="flex flex-col gap-1 w-20">
                                    <input v-model.number="item.viewsThreshold" type="number" placeholder="阈值" class="bg-white border text-sm rounded px-2 py-1 outline-none focus:border-indigo-400 font-mono" />
                                    <span class="text-[10px] text-slate-400">播放量阈值</span>
                                </div>
                                <button 
                                    @click="item.enabled = !item.enabled"
                                    class="w-8 h-4 rounded-full transition-colors relative flex items-center p-0.5"
                                    :class="item.enabled ? 'bg-pink-500' : 'bg-slate-300'">
                                    <div class="w-3 h-3 rounded-full bg-white shadow transform transition-transform"
                                        :class="item.enabled ? 'translate-x-4' : 'translate-x-0'"></div>
                                </button>
                                <button @click="currentPersona.bilibiliList.splice(index, 1)" class="text-slate-400 hover:text-red-500">×</button>
                            </div>
                            <div v-if="!(currentPersona.bilibiliList && currentPersona.bilibiliList.length)" class="text-center text-xs text-slate-400 py-2">暂无监控UP主，点击上方添加</div>
                        </div>
                    </div>

                    <!-- Hot Sources -->
                    <div class="bg-slate-50 rounded-xl border border-slate-200 overflow-hidden">
                        <div class="px-4 py-3 border-b border-slate-200 bg-slate-100/50 flex items-center justify-between">
                            <div class="flex items-center gap-2 font-medium text-slate-700">
                                <Flame class="w-4 h-4 text-emerald-500" />
                                今日热点源
                            </div>
                            <button @click="addHotSource" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium">+ 添加热点源</button>
                        </div>
                        <div class="p-4 space-y-3">
                            <div v-for="(item, index) in (currentPersona.hotSources || [])" :key="index" class="flex items-center gap-3">
                                <input v-model="item.name" placeholder="名称 (如: 知乎热榜)" class="flex-1 bg-white border text-sm rounded px-2 py-1 outline-none focus:border-indigo-400" />
                                <button 
                                    @click="item.enabled = !item.enabled"
                                    class="w-8 h-4 rounded-full transition-colors relative flex items-center p-0.5"
                                    :class="item.enabled ? 'bg-emerald-500' : 'bg-slate-300'">
                                    <div class="w-3 h-3 rounded-full bg-white shadow transform transition-transform"
                                        :class="item.enabled ? 'translate-x-4' : 'translate-x-0'"></div>
                                </button>
                                <button @click="currentPersona.hotSources.splice(index, 1)" class="text-slate-400 hover:text-red-500">×</button>
                            </div>
                            <div v-if="!(currentPersona.hotSources && currentPersona.hotSources.length)" class="text-center text-xs text-slate-400 py-2">暂无热点源，点击上方添加</div>
                        </div>
                    </div>

                    <!-- RSS Feeds -->
                    <div class="bg-slate-50 rounded-xl border border-slate-200 overflow-hidden">
                        <div class="px-4 py-3 border-b border-slate-200 bg-slate-100/50 flex items-center justify-between">
                            <div class="flex items-center gap-2 font-medium text-slate-700">
                                <Rss class="w-4 h-4 text-orange-500" />
                                RSS / 周刊订阅
                            </div>
                            <button @click="addRssSource" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium">+ 添加订阅</button>
                        </div>
                        <div class="p-4 space-y-3">
                            <div v-for="(item, index) in (currentPersona.rssList || [])" :key="index" class="flex items-center gap-3">
                                <input v-model="item.name" placeholder="名称" class="bg-white border text-sm rounded px-2 py-1 w-24 outline-none focus:border-indigo-400" />
                                <input v-model="item.url" placeholder="RSS URL" class="flex-1 bg-white border text-sm rounded px-2 py-1 outline-none focus:border-indigo-400 font-mono" />
                                <button 
                                    @click="item.enabled = !item.enabled"
                                    class="w-8 h-4 rounded-full transition-colors relative flex items-center p-0.5"
                                    :class="item.enabled ? 'bg-orange-500' : 'bg-slate-300'">
                                    <div class="w-3 h-3 rounded-full bg-white shadow transform transition-transform"
                                        :class="item.enabled ? 'translate-x-4' : 'translate-x-0'"></div>
                                </button>
                                <button @click="currentPersona.rssList.splice(index, 1)" class="text-slate-400 hover:text-red-500">×</button>
                            </div>
                             <div v-if="!(currentPersona.rssList && currentPersona.rssList.length)" class="text-center text-xs text-slate-400 py-2">暂无订阅源，点击上方添加</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="absolute bottom-8 right-8 flex flex-col items-end gap-3 z-10">
            <!-- Progress Bar (Visible during sync) -->
            <transition name="fade">
                <div v-if="isSyncing" class="w-64 bg-slate-100 rounded-full h-1.5 overflow-hidden border border-slate-200 shadow-inner mb-1">
                    <div 
                        class="bg-indigo-500 h-full transition-all duration-500 ease-out"
                        :style="{ width: `${syncProgress}%` }"
                    ></div>
                </div>
            </transition>
            <div v-if="isSyncing" class="text-[10px] text-slate-400 mb-2 font-mono">{{ syncMessage }} ({{ syncProgress }}%)</div>

            <div class="flex gap-3">
                <button @click="handleSync" 
                    :disabled="isSyncing"
                    class="bg-white border border-slate-200 text-slate-700 px-6 py-3 rounded-xl font-bold flex items-center gap-2 shadow-lg hover:border-indigo-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                    <RefreshCw class="w-5 h-5" :class="isSyncing ? 'animate-spin' : ''" />
                    {{ isSyncing ? '同步中...' : '立即同步' }}
                </button>
                <button @click="handleSave" class="bg-black text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 shadow-lg hover:-translate-y-1 transition-transform">
                    <Save class="w-5 h-5" />
                    保存配置
                </button>
            </div>
        </div>

        <!-- Success Toast -->
        <transition name="toast">
            <div v-if="showSyncToast" class="fixed bottom-10 left-1/2 -translate-x-1/2 z-50 bg-white border border-slate-200 shadow-2xl rounded-2xl p-4 flex items-center gap-4 min-w-[320px] animate-bounce-subtle">
                <div class="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600">
                    <CheckCircle2 class="w-6 h-6" />
                </div>
                <div class="flex-1">
                    <h4 class="font-bold text-slate-800 text-sm">情报抓取完毕</h4>
                    <p class="text-xs text-slate-500">建议立即前往情报大盘查看最新动态</p>
                </div>
                <router-link to="/" class="bg-slate-900 text-white px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1 hover:bg-indigo-600 transition-colors">
                    <LayoutDashboard class="w-3 h-3" />
                    前往查看
                </router-link>
                <button @click="showSyncToast = false" class="text-slate-300 hover:text-slate-500">
                    <X class="w-4 h-4" />
                </button>
            </div>
        </transition>
    </div>
    
    <div v-else class="flex-1 flex items-center justify-center text-slate-400">
        Loading Persona...
    </div>
  </div>
</template>

<style scoped>
.dashed {
    background-image: linear-gradient(to right, #e2e8f0 50%, rgba(255,255,255,0) 0%);
    background-position: bottom;
    background-size: 8px 1px;
    background-repeat: repeat-x;
}

/* Transitions */
.fade-enter-active, .fade-leave-active {
    transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
    opacity: 0;
}

.toast-enter-active {
    animation: toast-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.toast-leave-active {
    animation: toast-in 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) reverse;
}

@keyframes toast-in {
    0% { transform: translate(-50%, 20px) scale(0.9); opacity: 0; }
    100% { transform: translate(-50%, 0) scale(1); opacity: 1; }
}

@keyframes bounce-subtle {
    0%, 100% { transform: translate(-50%, 0); }
    50% { transform: translate(-50%, -5px); }
}
.animate-bounce-subtle {
    animation: bounce-subtle 3s infinite ease-in-out;
}
</style>
