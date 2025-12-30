<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Sparkles, RefreshCw } from 'lucide-vue-next'
import { useSettings } from '../composables/useSettings'
import CodeMineCard from '../components/dashboard/CodeMineCard.vue'
import RivalCard from '../components/dashboard/RivalCard.vue'
import BuzzList from '../components/dashboard/BuzzList.vue'

import ContextMenu from '../components/common/ContextMenu.vue'
import ScriptWorkbenchModal from '../components/workbench/ScriptWorkbenchModal.vue'
import AnalysisResultModal from '../components/dashboard/AnalysisResultModal.vue'
import { topicService } from '../services/topicService'
import { dataService } from '../services/dataService'

// --- Settings & Dynamic Columns ---
// --- Settings & Dynamic Columns ---
const { currentPersona } = useSettings()

const hasAnyBilibili = computed(() => currentPersona.value.bilibiliList?.some(i => i.enabled))
const hasAnyRss = computed(() => currentPersona.value.rssList?.some(i => i.enabled))
const hasAnyHot = computed(() => currentPersona.value.hotSources?.some(i => i.enabled))


// --- Mock Data ---
const repos = ref([
  { 
      id: 1, 
      name: 'Auto-GPT-Next', 
      description: 'Auto-GPT 的重大升级，稳定性大幅提升，支持更多插件。本项目旨在解决复杂的 Agent 任务链问题。', 
      stars: 12500, 
      todayStars: 450, 
      isRising: true,
      url: 'https://github.com/Significant-Gravitas/Auto-GPT',
      aiSummary: '核心功能：1. 自动化任务拆解与执行；2. 强大的插件系统支持浏览器操作；3. 长期记忆管理。适合用来做“AI 自动化工作流”相关的选题。' 
  },
  { 
      id: 2, 
      name: 'Vue3-Next', 
      description: '下一代 Vue.js 核心预览，性能提升 200%。基于 Rust 重写的编译器。', 
      stars: 8500, 
      todayStars: 120, 
      isRising: false,
      url: 'https://github.com/vuejs/core',
      aiSummary: '核心看点：1. Vapor Mode 无虚拟 DOM 渲染；2. 编译速度提升 10 倍；3. 完全兼容现有生态。是前端技术圈的重磅炸弹。' 
  },
  { 
      id: 3, 
      name: 'shadcn-vue', 
      description: '基于 Radix Vue 的组件库，复制粘贴即可使用。设计风格极简。', 
      stars: 3200, 
      todayStars: 89, 
      isRising: false,
      url: 'https://github.com/shadcn-ui/ui',
      aiSummary: '核心优势：1. 源码拷贝而非 NPM 包，定制自由度极高；2. 极简设计风格；3. 社区生态丰富。适合推荐给独立开发者。'
  },
])

const videos = ref([
  { 
      id: 1, 
      title: 'AI Sora 发布，视频变天了！这也是普通人的机会吗？', 
      author: '意愿AI', 
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix', 
      views: 120000, 
      likes: 8500,
      favorites: 3200,
      comments: 1200,
      aiSummary: '视频详细演示了 Sora 的 5 个核心功能，观点犀利。评论区都在讨论“失业”，适合做情绪对冲选题。',
      thumbnail: 'https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?w=500&q=80',
      url: 'https://www.bilibili.com/video/BV1xx411c7mD'
  },
  { 
      id: 2, 
      title: '主宋云新发布会解读：不仅仅是 AI', 
      author: 'Technology', 
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka', 
      views: 8000, 
      likes: 450,
      favorites: 120,
      comments: 50,
      aiSummary: '硬核解读，内容太干，播放量一般，但提到的“端侧模型”概念很有前瞻性。',
      thumbnail: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=500&q=80',
      url: 'https://www.bilibili.com/video/BV1xx411c7mD'
  },
  { 
      id: 3, 
      title: 'Vue3 源码深度解析 - 响应式原理', 
      author: 'CodeMaster', 
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=John', 
      views: 56000, 
      likes: 5600,
      favorites: 4500,
      comments: 800,
      aiSummary: '代码演示非常清晰，但是语速太慢。可以参考其结构，制作一个 3 分钟极速版。',
      thumbnail: 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=500&q=80',
      url: 'https://www.bilibili.com/video/BV1xx411c7mD'
  },
])

const buzzList = ref([
  { id: 1, title: 'OpenAI 发布 Sora 模型', source: '微博', heat: '200w+' },
  { id: 2, title: '程序员 35 岁危机话题重燃', source: '知乎', heat: '180w' },
  { id: 3, title: 'Python 还能火多久？', source: '知乎', heat: '90w' },
  { id: 4, title: 'DeepSeek 开源模型参数泄露', source: 'Twitter', heat: '500k' },
])

const isFiltering = ref(false)

const handleAIFilter = () => {
    isFiltering.value = true
    // Wait for the modal to mount/open then start analysis
    // Actually we just toggle visibility, the modal handles the startAnalysis onMounted/watched
    setTimeout(() => {
        isFiltering.value = false
        showAnalysisModal.value = true
    }, 800)
}

// --- Context Menu & Workbench Logic ---
const showContextMenu = ref(false)
const contextMenuPos = ref({ x: 0, y: 0 })
const selectedTopic = ref(null)
const showWorkbench = ref(false)

const handleContextMenu = (e, topic) => {
    e.preventDefault()
    showContextMenu.value = true
    contextMenuPos.value = { x: e.clientX, y: e.clientY }
    selectedTopic.value = topic
}

const openWorkbench = () => {
    showWorkbench.value = true
}

const showAnalysisModal = ref(false)

const router = useRouter() // Import router if not exists, wait, need to check top
// ...
const handleDeepDive = async (topic) => {
    if (!topic) return
    
    // Safety check: Needs to be saved to DB for script generation foreign keys.
    try {
         // Normalize Data (CodeMine uses name/description, others title/summary)
         const title = topic.title || topic.name
         // Fallback for summary
         const summary = topic.summary || topic.aiSummary || topic.description || ''
         // Determine ID
         const safeOriginalId = topic.original_id || topic.url || `mock-${topic.id}-${title}`

         const saved = await topicService.createTopic({
            original_id: safeOriginalId,
            title: title,
            url: topic.url || '',
            summary: summary,
            thumbnail: topic.thumbnail,
            metrics: topic.metrics || {
                views: topic.views || topic.stars, // Fallback for CodeMine
                likes: topic.likes, 
                stars: topic.favorites || topic.stars
            },
            analysis_result: topic.analysis_result || {
                reason: topic.reason, heat: topic.heat, aiSummary: topic.aiSummary
            },
            status: 'saved'
        })
        
        router.push({ name: 'topic-detail', params: { id: saved.data.id } })
        
    } catch (e) {
        console.error("Deep dive save failed", e)
        const msg = e.response?.data?.detail ? JSON.stringify(e.response.data.detail) : e.message
        alert('进入详情页失败: ' + msg)
    }
}

const menuItems = [
    { label: '🚀 再探 (Deep Dive)', action: () => handleDeepDive(selectedTopic.value) },
    { label: '📥 丢进选题库', action: async () => {
        if (!selectedTopic.value) return
        try {
            const topic = selectedTopic.value
            // Normalize Data
            const title = topic.title || topic.name
            const summary = topic.summary || topic.aiSummary || topic.description || ''
            const safeOriginalId = topic.original_id || topic.url || `mock-${topic.id}-${title}`
            
            await topicService.createTopic({
                original_id: safeOriginalId,
                title: title,
                url: topic.url || '',
                summary: summary,
                thumbnail: topic.thumbnail,
                metrics: topic.metrics || {
                    views: topic.views || topic.stars, 
                    likes: topic.likes, 
                    stars: topic.favorites || topic.stars
                },
                analysis_result: topic.analysis_result || {
                    reason: topic.reason, 
                    heat: topic.heat,
                    aiSummary: topic.aiSummary
                },
                status: 'saved'
            })
            alert('已添加到选题库')
        } catch (e) {
            console.error(e)
            const msg = e.response?.data?.detail ? JSON.stringify(e.response.data.detail) : e.message
            alert('添加失败: ' + msg)
        }
    }}
]

// --- API Linkage ---
const isLoadingFeed = ref(false)
const loadFeed = async () => {
    if (!currentPersona.value?.id) {
        console.log('[Dashboard] No persona selected, skipping feed load')
        return
    }
    isLoadingFeed.value = true
    console.log('[Dashboard] Loading feed for persona:', currentPersona.value.id)
    try {
        const feed = await dataService.getDiscoveryFeed(currentPersona.value.id)
        console.log('[Dashboard] Received feed items:', feed.length)
        
        // Reset to clear mock data
        videos.value = []
        repos.value = []
        
        feed.forEach(item => {
            if (item.source === 'Bilibili') {
                const proto_pic = (url) => url?.startsWith('//') ? `https:${url}` : url
                videos.value.push({
                    ...item,
                    thumbnail: proto_pic(item.thumbnail),
                    summary: item.summary, // The original introduction for hover
                    aiSummary: '', // Leave empty until 'Deep Dive'
                    author: item.author || '未知UP主',
                    authorAvatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${item.author || item.id || 'default'}`,
                    views: item.metrics?.views || 0,
                    likes: item.metrics?.likes || 0,
                    url: item.url
                })
            } else if (item.source?.toLowerCase().includes('rss') || item.source?.toLowerCase().includes('github')) {
                repos.value.push({
                    ...item,
                    name: item.title,
                    description: item.summary,
                    stars: item.metrics?.stars || 0
                })
            }
        })
        console.log('[Dashboard] Processed videos:', videos.value.length)
    } catch (e) {
        console.error("[Dashboard] Failed to load feed", e)
    } finally {
        isLoadingFeed.value = false
    }
}

onMounted(() => {
    loadFeed()
})

watch(() => currentPersona.value?.id, (newVal) => {
    if (newVal) loadFeed()
})

</script>

<template>
  <div class="h-full flex flex-col gap-6" @click="showContextMenu = false">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">情报大盘</h1>
        <p class="text-slate-500 text-sm">今日已为您聚合 142 条情报，AI 推荐 5 条</p>
      </div>
      <button 
        @click="handleAIFilter"
        class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-full font-medium flex items-center gap-2 transition-all hover:scale-105 active:scale-95 shadow-lg shadow-indigo-200">
        <RefreshCw v-if="isFiltering" class="w-5 h-5 animate-spin" />
        <Sparkles v-else class="w-5 h-5" />
        {{ isFiltering ? 'AI 正在思考...' : 'AI 帮我挑' }}
      </button>
    </div>

    <!-- Dynamic Columns Container -->
    <div class="flex-1 flex gap-6 min-h-0 overflow-x-auto pb-2">
      
      <!-- GitHub Trending (Code Mine) - Always Show (Logic: RSS represents generic sources/code mine for now) -->
      <section v-if="hasAnyRss" class="flex-1 min-w-[320px] flex flex-col gap-4">
        <div class="flex items-center justify-between">
          <h2 class="font-bold text-slate-700 flex items-center gap-2">
            <div class="w-2 h-6 bg-yellow-400 rounded-full"></div>
            开源矿场
          </h2>
          <span class="text-xs font-mono text-slate-400">GitHub Trending</span>
        </div>
        <div class="flex-1 bg-slate-50/50 rounded-2xl border-2 border-slate-100 border-dashed p-4 space-y-4 overflow-y-auto pr-2 custom-scrollbar">
          <CodeMineCard 
             v-for="repo in repos" :key="repo.id" :repo="repo" 
             @contextmenu="(e) => handleContextMenu(e, repo)"
          />
        </div>
      </section>

      <!-- Bilibili (Rivals) - Dynamic Hide/Expand -->
      <section v-if="hasAnyBilibili" class="flex-1 min-w-[320px] flex flex-col gap-4">
        <div class="flex items-center justify-between">
          <h2 class="font-bold text-slate-700 flex items-center gap-2">
            <div class="w-2 h-6 bg-pink-400 rounded-full"></div>
            竞品风向
          </h2>
          <span class="text-xs font-mono text-slate-400">Bilibili Monitor</span>
        </div>
        <div class="flex-1 bg-slate-50/50 rounded-2xl border-2 border-slate-100 border-dashed p-4 space-y-4 overflow-y-auto pr-2 custom-scrollbar">
          <RivalCard 
             v-for="video in videos" :key="video.id" :video="video" 
             @contextmenu="(e) => handleContextMenu(e, video)"
          />
        </div>
      </section>

      <!-- Hot Lists (Buzz) - Dynamic Hide/Expand -->
      <section v-if="hasAnyHot" class="flex-1 min-w-[320px] flex flex-col gap-4">
        <div class="flex items-center justify-between">
          <h2 class="font-bold text-slate-700 flex items-center gap-2">
            <div class="w-2 h-6 bg-emerald-400 rounded-full"></div>
            今日热榜
          </h2>
          <span class="text-xs font-mono text-slate-400">Hot Lists</span>
        </div>
        <div class="flex-1 bg-slate-50/50 rounded-2xl border-2 border-slate-100 border-dashed p-4 overflow-y-auto pr-2 custom-scrollbar relative">
           <!-- Tape visual -->
           <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-32 h-8 bg-slate-200/40 rotate-1 z-0"></div>
           <!-- Tape visual -->
           <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-32 h-8 bg-slate-200/40 rotate-1 z-0"></div>
           <BuzzList :items="buzzList" class="relative z-10" @item-contextmenu="handleContextMenu" />
        </div>
      </section>

    </div>

    <!-- Modals & Overlays -->
    <ContextMenu 
        :visible="showContextMenu" 
        :x="contextMenuPos.x" 
        :y="contextMenuPos.y" 
        :menuItems="menuItems"
        @close="showContextMenu = false"
    />

    <ScriptWorkbenchModal 
        :isOpen="showWorkbench"
        :topic="selectedTopic"
        @close="showWorkbench = false"
    />

    <AnalysisResultModal 
        v-if="showAnalysisModal"
        :isOpen="showAnalysisModal"
        :persona="currentPersona"
        @close="showAnalysisModal = false"
    />
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}
</style>
