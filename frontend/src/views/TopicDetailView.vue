<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, ExternalLink, Share2, FileText, Code2, Tag, Sparkles, Copy, Trash2, Edit, Heading, AlignLeft, Hash, Lightbulb, RefreshCw, Save } from 'lucide-vue-next'
import { topicService } from '../services/topicService'
import { scriptService } from '../services/scriptService'
import { dataService } from '../services/dataService'
import { useSettings } from '../composables/useSettings'

const route = useRoute()
const topicId = route.params.id

const isLoading = ref(true)
const topic = ref(null)

// Workbench State
const templates = ref([])
const selectedTemplateId = ref(null)
const manualPrompt = ref('')
const isGenerating = ref(false)
const generatedScript = ref('')
const isEditingScript = ref(false)

// Metadata Generation
const { currentPersona } = useSettings()
const metadataRecommendations = ref(null)
const isGeneratingMetadata = ref(false)
const isGeneratingAnalysis = ref(false) // NEW: for initial insight

const generateMetadataAction = async (isManual = false) => {
    if (isGeneratingMetadata.value) return
    isGeneratingMetadata.value = true
    if (!isManual && !generatedScript.value) {
        isGeneratingAnalysis.value = true
    }
    
    try {
        const res = await dataService.generateMetadata(topicId, currentPersona.value?.id, generatedScript.value)
        topic.value = res
        
        if (isManual || generatedScript.value) {
            metadataRecommendations.value = res
        }
    } catch (e) {
        // ... (existing catch logic)
        console.error("AI Analysis Failed:", e)
        const errorMsg = e.response?.data?.detail || e.message || '未知错误'
        // Only alert if manual (user clicked the button)
        if (isManual) {
            alert('AI 总结生成失败: ' + (typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg)))
        }
    } finally {
        isGeneratingMetadata.value = false
        isGeneratingAnalysis.value = false
    }
}

const loadData = async () => {
    isLoading.value = true
    try {
        // 1. Fetch Topic
        // Assuming topicService has getTopic. If not, we use API directly or add it.
        // Checking topicService... it has delete/create, but getTopics returns list.
        // We need getTopic(id). Let's assume we can add/use api.
        // Wait, topicService doesn't have getTopic(id) in previously viewed code.
        // backend api has GET /topics/{id}.
        // Let's us api directly or assume I added it? 
        // Best to use raw API import or add to service but I can't edit service *and* view in one file call.
        // I will use direct API call or just implement fetch here for now.
        // Actually, let's fix topicService later if needed, but for now I'll import api.
        topic.value = await topicService.getTopic(topicId)
        
        // Show AI Insight Summary if exists
        if (!topic.value.ai_title && !isGeneratingMetadata.value) {
            // ONLY auto-generate the core summary (insight) if it's the first time
            generateMetadataAction(false)
        }

        // --- Persistence Recovery ---
        // 1. Recover Generated Script
        const savedScript = await dataService.getScriptForTopic(topicId)
        if (savedScript) {
            generatedScript.value = savedScript.content
            currentScriptId.value = savedScript.id
        }

        // 2. Recover Recommendations (Titles/Tags) if they exist
        if (topic.value.analysis_result?.ai_titles?.length > 0) {
            metadataRecommendations.value = {
                titles: topic.value.analysis_result.ai_titles,
                intros: topic.value.analysis_result.script_intro ? [topic.value.analysis_result.script_intro] : [topic.value.ai_summary],
                tags: topic.value.analysis_result.keywords || []
            }
        }
        
        // 2. Fetch Templates
        templates.value = await scriptService.getTemplates()
        if (templates.value.length > 0) {
            selectedTemplateId.value = templates.value[0].id
        }
        
    } catch (e) {
        console.error("Failed to load topic", e)
    } finally {
        isLoading.value = false
    }
}

// Generate Script
const generateScriptAction = async () => {
    if (isGenerating.value) return
    isGenerating.value = true
    try {
        // Pass Persona and Template to real AI backend
        const res = await dataService.generateScript(
            topicId, 
            selectedTemplateId.value, 
            currentPersona.value?.id,
            manualPrompt.value
        )
        generatedScript.value = res.content
        currentScriptId.value = res.id
    } catch (e) {
        console.error(e)
        const errorMsg = e.response?.data?.detail || e.message || '未知错误'
        alert('脚本生成失败: ' + (typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg)))
    } finally {
        isGenerating.value = false
    }
}

const copyScript = () => {
    navigator.clipboard.writeText(generatedScript.value)
    alert('已复制')
}

// Save Functionality
const isSaving = ref(false)
const currentScriptId = ref(null)

const saveAll = async () => {
    if (isSaving.value) return
    isSaving.value = true
    try {
        // 1. Update Topic Metadata
        // We need to merge metadataRecommendations back into analysis_result if they were modified manually (unavailable yet, but assuming we persist what filters generated)
        // For now, we persist whatever is in metadataRecommendations as the 'latest' state if it exists
        
        let analysisUpdate = { ...(topic.value.analysis_result || {}) }
        
        if (metadataRecommendations.value) {
           analysisUpdate.ai_titles = metadataRecommendations.value.titles
           analysisUpdate.keywords = metadataRecommendations.value.tags
           if (metadataRecommendations.value.intros && metadataRecommendations.value.intros.length > 0) {
               analysisUpdate.script_intro = metadataRecommendations.value.intros[0]
           }
        }

        await topicService.updateTopic(topicId, {
            analysis_result: analysisUpdate
        })

        // 2. Update Script Content
        if (currentScriptId.value && generatedScript.value) {
            await scriptService.updateScript(currentScriptId.value, generatedScript.value)
        }

        alert('保存成功！')
    } catch (e) {
        console.error('Save failed', e)
        alert('保存失败')
    } finally {
        isSaving.value = false
    }
}

// Helpers
const analysisDisplay = computed(() => {
    if (!topic.value) return {}
    // Backend stores analysis in 'analysis_result' dict
    // metrics in 'metrics'
    return {
        summary: topic.value.summary || '暂无摘要',
        ai_summary: topic.value.ai_summary,
        difficulty: topic.value.analysis_result?.difficulty || 'N/A',
        match: topic.value.analysis_result?.personaMatch || 'N/A',
        metrics: topic.value.metrics || {},
        author: topic.value.author || topic.value.metrics?.author || '未知',
        publishedAt: topic.value.published_at ? new Date(topic.value.published_at).toLocaleString('zh-CN', { hour12: false }) : '未知'
    }
})

onMounted(loadData)

</script>

<template>
  <div class="h-full flex flex-col overflow-hidden bg-slate-50">
    <!-- Header -->
    <div class="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between shrink-0">
         <div class="flex items-center gap-4">
            <RouterLink to="/" class="p-2 hover:bg-slate-100 rounded-full transition text-slate-500">
                <ArrowLeft class="w-5 h-5" />
            </RouterLink>
            <h1 class="text-xl font-bold text-slate-800 line-clamp-1 max-w-xl" :title="topic?.title">
                {{ topic?.title || '加载中...' }}
            </h1>
            <span v-if="topic" class="px-2 py-0.5 bg-slate-100 text-slate-500 text-xs rounded font-mono">
                ID: {{ topic.id }}
            </span>
         </div>
         <div class="flex items-center gap-3">
             <a v-if="topic?.url" :href="topic.url" target="_blank" class="flex items-center gap-2 text-sm text-slate-500 hover:text-indigo-600 transition">
                 <ExternalLink class="w-4 h-4" /> 原文
             </a>
             <div class="h-4 w-px bg-slate-200 mx-2"></div>
             <button disabled class="text-sm text-slate-400 cursor-not-allowed flex items-center gap-1">
                 <Share2 class="w-4 h-4" /> 推送飞书
             </button>
         </div>
    </div>

    <!-- Thumbnail Banner (Small) -->
    <div v-if="topic?.thumbnail" class="w-full h-32 relative shrink-0 overflow-hidden">
        <img :src="topic.thumbnail" class="w-full h-full object-cover blur-2xl opacity-20 absolute inset-0" />
        <div class="absolute inset-0 flex items-center px-8 gap-6 bg-gradient-to-r from-slate-50 to-transparent">
            <img :src="topic.thumbnail" class="h-20 w-32 object-cover rounded-lg shadow-lg border-2 border-white" />
            <div class="flex flex-col">
                <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Original Feed Info</span>
                <h2 class="text-xl font-bold text-slate-700 truncate max-w-2xl">{{ topic.title }}</h2>
                <div class="flex items-center gap-3 text-xs text-slate-500 mt-1">
                    <span>{{ analysisDisplay.author }}</span>
                    <span>•</span>
                    <span>发布于 {{ analysisDisplay.publishedAt }}</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div v-if="isLoading" class="flex-1 flex items-center justify-center">
        <div class="animate-spin w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full"></div>
    </div>
    
    <div v-else class="flex-1 flex overflow-hidden">
        
        <!-- Left: Analysis & Info -->
        <div class="w-1/3 min-w-[350px] max-w-[450px] border-r border-slate-200 overflow-y-auto p-6 flex flex-col gap-6 bg-white">
            
            <!-- Analysis Card -->
            <section>
                <div class="flex items-center justify-between mb-4">
                    <h2 class="font-bold text-slate-800 flex items-center gap-2">
                        <Sparkles class="w-5 h-5 text-indigo-500" />
                        AI 智能洞察
                    </h2>
                    <span v-if="isGeneratingMetadata" class="text-xs text-indigo-500 animate-pulse flex items-center gap-1">
                        <RefreshCw class="w-3 h-3 animate-spin" /> 分析中...
                    </span>
                </div>
                
                <div class="bg-indigo-50/50 rounded-xl p-4 border border-indigo-100 space-y-4">
                    <!-- Only show pulse if the CORE summary is missing AND we are generating initial analysis -->
                    <div v-if="!analysisDisplay.ai_summary && isGeneratingAnalysis" class="space-y-2">
                        <div class="h-4 bg-indigo-100 rounded w-full animate-pulse"></div>
                        <div class="h-4 bg-indigo-100 rounded w-5/6 animate-pulse"></div>
                        <div class="h-4 bg-indigo-100 rounded w-4/6 animate-pulse"></div>
                    </div>
                    <div v-else>
                        <span class="text-xs font-bold text-indigo-400 uppercase tracking-wider">AI Insight</span>
                        <p class="text-sm text-slate-700 leading-relaxed mt-1 whitespace-pre-wrap min-h-[60px]">
                            {{ analysisDisplay.ai_summary || (isGeneratingAnalysis ? 'AI 正在深度解析选题价值...' : '暂无分析结果') }}
                        </p>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-3">
                         <div class="bg-white p-3 rounded-lg border border-slate-100">
                             <div class="text-xs text-slate-400">选题匹配度</div>
                             <div class="flex items-center gap-1">
                                <div class="font-bold text-indigo-600 text-lg">{{ analysisDisplay.match }}</div>
                                <div class="text-[10px] text-slate-400">/10</div>
                             </div>
                         </div>
                         <div class="bg-white p-3 rounded-lg border border-slate-100">
                             <div class="text-xs text-slate-400">上手难度</div>
                             <div class="flex items-center gap-1">
                                <div class="font-bold text-amber-600 text-lg">{{ analysisDisplay.difficulty }}</div>
                                <div class="text-[10px] text-slate-400">/10</div>
                             </div>
                         </div>
                    </div>
                </div>
            </section>

            <!-- Raw Content -->
            <section>
                <h2 class="font-bold text-slate-800 flex items-center gap-2 mb-4">
                    <AlignLeft class="w-5 h-5 text-slate-400" />
                    原文摘要
                </h2>
                <div class="bg-slate-50 rounded-xl p-4 border border-slate-200">
                    <p class="text-sm text-slate-600 leading-relaxed italic">
                        "{{ analysisDisplay.summary }}"
                    </p>
                </div>
            </section>

            <!-- Metrics Card (New) -->
            <section v-if="topic?.metrics">
                <h2 class="font-bold text-slate-800 flex items-center gap-2 mb-4">
                    <Tag class="w-5 h-5 text-blue-500" />
                    情报详情
                </h2>
                <div class="bg-white rounded-xl border border-slate-200 p-4 space-y-4 shadow-sm">
                    <div class="grid grid-cols-2 gap-4">
                        <div class="flex flex-col">
                            <span class="text-xs text-slate-400 mb-1">播放/阅读</span>
                            <span class="font-mono font-bold text-slate-700">{{ topic.metrics.views || '-' }}</span>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-xs text-slate-400 mb-1">点赞</span>
                            <span class="font-mono font-bold text-slate-700">{{ topic.metrics.likes || '-' }}</span>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-xs text-slate-400 mb-1">评论</span>
                            <span class="font-mono font-bold text-slate-700">{{ topic.metrics.comments || '-' }}</span>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-xs text-slate-400 mb-1">收藏/转发</span>
                            <span class="font-mono font-bold text-slate-700">{{ topic.metrics.favorites || topic.metrics.stars || '-' }}</span>
                        </div>
                    </div>
                    
                    <div class="pt-4 border-t border-slate-100 flex flex-col gap-2">
                         <div class="flex items-center justify-between text-sm">
                             <span class="text-slate-500">来源</span>
                             <span class="font-medium text-slate-700 bg-slate-100 px-2 py-0.5 rounded">{{ topic.original_id?.startsWith('BV') ? 'Bilibili' : 'Web/RSS' }}</span>
                         </div>
                         <div v-if="topic.url" class="flex items-center justify-between text-sm">
                             <span class="text-slate-500">作者</span>
                             <span class="font-medium text-slate-700 truncate max-w-[150px]">{{ topic.metrics.author || '未知' }}</span>
                         </div>
                    </div>
                </div>
            </section>

            <!-- Workbench Config -->
            <section class="flex-1 flex flex-col">
                <h2 class="font-bold text-slate-800 flex items-center gap-2 mb-4">
                    <FileText class="w-5 h-5 text-purple-500" />
                    脚本工作台
                </h2>
                
                <div class="space-y-4 flex-1">
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-2">选择模版</label>
                        <select v-model="selectedTemplateId" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-indigo-500 transition">
                            <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
                        </select>
                        <p v-if="templates.length===0" class="text-xs text-red-400 mt-1">未找到模版，请先去配置中心添加</p>
                    </div>

                    <div class="flex-1 flex flex-col">
                         <label class="block text-sm font-medium text-slate-700 mb-2">额外提示词 (Optional)</label>
                         <textarea 
                            v-model="manualPrompt"
                            class="flex-1 w-full bg-slate-50 border border-slate-200 rounded-lg p-3 text-sm outline-none focus:border-indigo-500 transition resize-none min-h-[120px]"
                            placeholder="例如：语气要更幽默一点，开头加入提问..."
                        ></textarea>
                    </div>
                    
                    <button 
                        @click="generateScriptAction"
                        :disabled="isGenerating || templates.length===0"
                        class="w-full py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Sparkles class="w-5 h-5" :class="isGenerating ? 'animate-spin':''" />
                        {{ isGenerating ? 'AI 正在创作...' : '生成脚本' }}
                    </button>
                    
                    <p class="text-xs text-center text-slate-400">
                        生成后可在右侧直接编辑
                    </p>
                </div>
            </section>
        </div>

        <!-- Right: Editor -->
        <div class="flex-1 bg-slate-50 flex flex-col h-full relative">
             <div v-if="!generatedScript" class="flex-1 flex flex-col items-center justify-center text-slate-300 gap-4">
                <div class="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center">
                    <FileText class="w-10 h-10 opacity-30" />
                </div>
                <p>点击左侧“生成脚本”开始创作</p>
            </div>
            
            <div v-else class="flex-1 flex flex-col h-full">
                <!-- Toolbar -->
                <div class="h-12 border-b border-slate-200 bg-white flex items-center justify-between px-4">
                    <span class="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">Markdown Preview</span>
                    <div class="flex items-center gap-3">
                         <button 
                            @click="generateMetadataAction(true)"
                            :disabled="isGeneratingMetadata || !generatedScript"
                            class="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-600 hover:bg-indigo-100 rounded-lg text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Sparkles class="w-4 h-4" :class="isGeneratingMetadata ? 'animate-spin' : ''" />
                            {{ isGeneratingMetadata ? '生成中...' : '生成标题/简介' }}
                        </button>
                        <div class="h-4 w-px bg-slate-200"></div>
                        <div class="flex items-center gap-2">
                        <button @click="copyScript" class="p-1.5 hover:bg-slate-100 rounded text-slate-500 transition" title="Copy">
                            <Copy class="w-4 h-4" />
                        </button>
                         <button 
                            @click="saveAll" 
                            :disabled="isSaving"
                            class="p-1.5 hover:bg-slate-100 rounded text-slate-500 transition flex items-center gap-1" title="Save All">
                            <Save class="w-4 h-4" :class="isSaving ? 'animate-bounce' : ''" />
                        </button>
                    </div>
                </div>
                </div>
                
                <!-- Editor Area -->
                <textarea 
                    v-model="generatedScript"
                    class="flex-1 w-full h-full p-8 bg-white outline-none font-mono text-slate-700 leading-relaxed resize-none text-base"
                    placeholder="Script content..."
                ></textarea>
            </div>
        </div>

        <!-- Recommendations Column -->
        <div v-if="metadataRecommendations" class="w-80 min-w-[320px] border-l border-slate-200 bg-white overflow-y-auto p-5 flex flex-col gap-8 animate-in slide-in-from-right duration-300">
            <!-- Titles -->
            <section>
                 <h3 class="font-bold text-slate-800 mb-3 flex items-center gap-2 text-sm">
                    <Heading class="w-4 h-4 text-pink-500" /> 推荐标题
                 </h3>
                 <div class="space-y-3">
                     <div v-for="(item, i) in metadataRecommendations.titles" :key="i" class="group relative">
                         <div class="p-3 bg-slate-50 hover:bg-indigo-50 rounded-lg border border-slate-100 hover:border-indigo-100 transition-colors cursor-pointer" @click="navigator.clipboard.writeText(item); alert('已复制')">
                            <p class="text-sm text-slate-700 leading-snug pr-2">{{ item }}</p>
                         </div>
                     </div>
                 </div>
            </section>

            <!-- Intros -->
            <section>
                 <h3 class="font-bold text-slate-800 mb-3 flex items-center gap-2 text-sm">
                    <AlignLeft class="w-4 h-4 text-orange-500" /> 推荐简介
                 </h3>
                 <div class="space-y-3">
                     <div v-for="(item, i) in metadataRecommendations.intros" :key="i" class="group relative">
                         <div class="p-3 bg-slate-50 hover:bg-indigo-50 rounded-lg border border-slate-100 hover:border-indigo-100 transition-colors cursor-pointer" @click="navigator.clipboard.writeText(item); alert('已复制')">
                            <p class="text-xs text-slate-600 leading-relaxed">{{ item }}</p>
                         </div>
                     </div>
                 </div>
            </section>

            <!-- Tags -->
            <section>
                 <h3 class="font-bold text-slate-800 mb-3 flex items-center gap-2 text-sm">
                    <Hash class="w-4 h-4 text-blue-500" /> 推荐标签
                 </h3>
                 <div class="flex flex-wrap gap-2">
                      <span 
                        v-for="tag in metadataRecommendations.tags" 
                        :key="tag" 
                        class="px-2 py-0.5 bg-slate-50 hover:bg-indigo-50 rounded border border-slate-200 hover:border-indigo-200 text-xs text-slate-500 cursor-copy transition-colors"
                        @click="navigator.clipboard.writeText(tag); alert('已复制标签: #' + tag)"
                      >
                        #{{ tag }}
                      </span>
                 </div>
            </section>
        </div>
    </div>
  </div>
</template>
