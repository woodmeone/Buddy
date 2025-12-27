<script setup>
import { ref, onMounted } from 'vue'
import { X, Sparkles, TrendingUp, Target, MessageSquare, ArrowRight, CheckCircle2 } from 'lucide-vue-next'
import ContextMenu from '../common/ContextMenu.vue'
import { topicService } from '../../services/topicService'

const props = defineProps({
  isOpen: Boolean,
  persona: Object
})

const emit = defineEmits(['close'])
// ... existing state ... 
const showContextMenu = ref(false)
const contextMenuPos = ref({ x: 0, y: 0 })
const selectedTopic = ref(null)

const handleContextMenu = (e, topic) => {
    e.preventDefault()
    showContextMenu.value = true
    contextMenuPos.value = { x: e.clientX, y: e.clientY }
    selectedTopic.value = topic
}

// Reuse logic would be better but duplicating for MVP speed
const menuItems = [
    { label: '🚀 再探 (Deep Dive)', action: () => selectTopic(selectedTopic.value) },
    { label: '📥 丢进选题库', action: async () => {
        if (!selectedTopic.value) return
        try {
            await topicService.saveTopic(selectedTopic.value)
            alert('已添加到选题库')
        } catch (e) {
            alert('添加失败或已存在')
        }
    }}
]

const analysisSteps = ref([
    { label: '解析人设核心...', status: 'pending' },
    { label: '扫描全网热点...', status: 'pending' },
    { label: '匹配垂直领域...', status: 'pending' },
    { label: '生成推荐解释...', status: 'pending' }
])

const recommendedTopics = ref([])
const isAnalyzing = ref(true)

// Mock Analysis Process
onMounted(() => {
    if (props.isOpen) startAnalysis()
})

const startAnalysis = async () => {
    isAnalyzing.value = true
    recommendedTopics.value = []
    
    // Simulate steps
    for (let i = 0; i < analysisSteps.value.length; i++) {
        analysisSteps.value[i].status = 'running'
        await new Promise(r => setTimeout(r, 600))
        analysisSteps.value[i].status = 'done'
    }

    // Mock Result
    recommendedTopics.value = [
        {
            id: 101,
            title: '普通人如何用 DeepSeek 提效？(实测)',
            domain: 'AI 工具',
            reason: '紧扣“技术博主”人设，DeepSeek 是近期最大热点，适合做工具评测。',
            heat: 'High',
        },
        {
            id: 102,
            title: '为什么我不推荐你现在学 Python？',
            domain: '职业建议',
            reason: '反直觉观点 (Counter-intuitive)，容易引发讨论，符合“犀利”风格。',
            heat: 'Medium',
        },
        {
            id: 103,
            title: 'Vercel 部署 Next.js 踩坑指南',
            domain: '前端开发',
            reason: '精准击中开发者痛点，长尾流量高，体现专业度。',
            heat: 'Low',
        },
        {
            id: 104,
            title: 'Sora 还没发布，这 3 个竞品已经杀疯了',
            domain: 'AI 视频',
            reason: '蹭 Sora 热度，但提供即刻可用的替代方案，价值感强。',
            heat: 'High',
        },
        {
            id: 105,
            title: '独立开发者的第一桶金：我的真实复盘',
            domain: '搞钱/副业',
            reason: '所有开发者都关心的话题，增加人设的真实感（Human Touch）。',
            heat: 'High',
        },
        {
            id: 106,
            title: 'Vue 3.4 性能优化完全指南',
            domain: '框架技术',
            reason: '硬核技术干货，稳固“资深”人设的基本盘。',
            heat: 'Medium',
        }
    ]
    isAnalyzing.value = false
}

const router = useRouter()
import { useRouter } from 'vue-router'

const selectTopic = async (topic) => {
    // Save and Navigate
    try {
         const saved = await topicService.createTopic({
            original_id: `rec-${topic.id}-${topic.title}`, // Stable ID for mock recs
            title: topic.title,
            url: '', 
            summary: topic.reason, 
            metrics: { heat: topic.heat },
            analysis_result: {
                domain: topic.domain,
                reason: topic.reason
            },
            status: 'saved'
        })
        emit('close')
        router.push({ name: 'topic-detail', params: { id: saved.data.id } })
    } catch (e) {
        console.error("Deep dive save failed", e)
        const msg = e.response?.data?.detail ? JSON.stringify(e.response.data.detail) : e.message
        alert('无法进入详情页：' + msg)
    }
}
</script>

<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="opacity-0 scale-95"
    enter-to-class="opacity-100 scale-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-95"
  >
    <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-8 bg-black/60 backdrop-blur-sm">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-5xl h-[85vh] flex flex-col overflow-hidden relative">
            
            <!-- Close Button -->
            <button @click="$emit('close')" class="absolute top-4 right-4 p-2 bg-slate-100 hover:bg-slate-200 rounded-full z-10">
                <X class="w-5 h-5 text-slate-500" />
            </button>

            <!-- Loading State -->
            <div v-if="isAnalyzing" class="flex-1 flex flex-col items-center justify-center gap-8">
                <div class="relative w-24 h-24">
                    <div class="absolute inset-0 border-4 border-indigo-100 rounded-full"></div>
                    <div class="absolute inset-0 border-4 border-indigo-600 rounded-full border-t-transparent animate-spin"></div>
                    <Sparkles class="absolute inset-0 m-auto w-10 h-10 text-indigo-600 animate-pulse" />
                </div>
                <div class="space-y-4 w-64">
                    <div v-for="(step, index) in analysisSteps" :key="index" class="flex items-center gap-3">
                        <div class="w-5 h-5 flex items-center justify-center">
                            <CheckCircle2 v-if="step.status === 'done'" class="w-5 h-5 text-green-500" />
                            <div v-else-if="step.status === 'running'" class="w-4 h-4 border-2 border-indigo-600 border-r-transparent rounded-full animate-spin"></div>
                            <div v-else class="w-2 h-2 rounded-full bg-slate-200"></div>
                        </div>
                        <span class="text-sm font-medium transition-colors" 
                            :class="step.status === 'running' ? 'text-indigo-600' : step.status === 'done' ? 'text-slate-400' : 'text-slate-300'">
                            {{ step.label }}
                        </span>
                    </div>
                </div>
            </div>

            <!-- Result State -->
            <div v-else class="flex-1 flex flex-col overflow-hidden" @click="showContextMenu = false">
                <!-- Header -->
                <div class="p-8 bg-indigo-600 text-white flex flex-col gap-2">
                    <div class="flex items-center gap-3">
                        <div class="p-2 bg-white/10 rounded-lg backdrop-blur">
                            <Target class="w-6 h-6 text-white" />
                        </div>
                        <h2 class="text-2xl font-bold">AI 选题分析报告</h2>
                    </div>
                    <p class="text-indigo-100 text-sm ml-11 opacity-90">
                        基于人设 <span class="font-bold text-white underline decoration-dashed">{{ persona?.name }}</span>，
                        从 142 条情报中精选出以下 6 个高价值选题：
                    </p>
                </div>

                <!-- Cards Grid -->
                <div class="flex-1 overflow-y-auto p-8 bg-slate-50">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <div 
                            v-for="(topic, index) in recommendedTopics" :key="topic.id"
                            class="group bg-white rounded-xl p-5 border border-slate-200 hover:border-indigo-400 hover:shadow-lg hover:-translate-y-1 transition-all cursor-pointer relative overflow-hidden"
                            @click="selectTopic(topic)"
                            @contextmenu="(e) => handleContextMenu(e, topic)"
                        >
                            <!-- Rank Number -->
                            <div class="absolute -right-4 -top-4 w-16 h-16 bg-slate-100 rounded-full flex items-end justify-start p-3 text-4xl font-black text-slate-200 group-hover:text-indigo-100 transition-colors">
                                {{ index + 1 }}
                            </div>

                            <div class="flex flex-col h-full relative z-10">
                                <span class="text-xs font-bold px-2 py-1 rounded bg-slate-100 text-slate-600 w-fit mb-3">
                                    {{ topic.domain }}
                                </span>
                                
                                <h3 class="font-bold text-slate-800 text-lg leading-snug mb-3 group-hover:text-indigo-700 transition-colors">
                                    {{ topic.title }}
                                </h3>

                                <div class="bg-indigo-50/50 rounded-lg p-3 mb-4 flex-1">
                                    <div class="flex items-start gap-2">
                                        <MessageSquare class="w-4 h-4 text-indigo-500 mt-0.5 flex-shrink-0" />
                                        <p class="text-xs text-slate-600 leading-relaxed">
                                            <span class="font-bold text-indigo-600">推荐理由：</span>
                                            {{ topic.reason }}
                                        </p>
                                    </div>
                                </div>

                                <div class="flex items-center justify-between mt-auto pt-2 border-t border-slate-100">
                                    <div class="flex items-center gap-1.5">
                                        <TrendingUp class="w-4 h-4" :class="topic.heat === 'High' ? 'text-red-500' : 'text-orange-400'" />
                                        <span class="text-xs font-medium text-slate-500">热度: {{ topic.heat }}</span>
                                    </div>
                                    <div class="text-indigo-600 text-xs font-bold flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity transform translate-x-2 group-hover:translate-x-0">
                                        去创作 <ArrowRight class="w-3 h-3" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <ContextMenu 
            :visible="showContextMenu" 
            :x="contextMenuPos.x" 
            :y="contextMenuPos.y" 
            :menuItems="menuItems"
            @close="showContextMenu = false"
        />
    </div>
  </Transition>
</template>
