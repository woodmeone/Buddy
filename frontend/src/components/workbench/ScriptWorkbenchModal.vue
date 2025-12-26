<script setup>
import { ref, watch, onMounted } from 'vue'
import { X, Sparkles, FileText, Send, Copy } from 'lucide-vue-next'
import { scriptService } from '../../services/scriptService'

const props = defineProps({
  isOpen: Boolean,
  topic: Object
})

const emit = defineEmits(['close'])

const generatedScript = ref('')
const isGenerating = ref(false)
const manualPrompt = ref('')
const templates = ref([])
const selectedTemplateId = ref(null)

const fetchTemplates = async () => {
    try {
       templates.value = await scriptService.getTemplates()
       if (templates.value.length > 0) {
           selectedTemplateId.value = templates.value[0].id
       }
    } catch (e) {
        console.error(e)
    }
}

// Generate script using template + Topic
const generateScript = () => {
    isGenerating.value = true
    const topicTitle = props.topic?.title || '未命名选题'
    
    setTimeout(() => {
        isGenerating.value = false
        const template = templates.value.find(t => t.id === selectedTemplateId.value)
        if (template) {
            // Simple replace. In real app, this would be an AI API call with the template as context
            generatedScript.value = template.template.replaceAll('{{topic.title}}', topicTitle)
        } else {
            generatedScript.value = `# ${topicTitle}\n\n(No template selected)`
        }
    }, 1000)
}

watch(() => props.isOpen, (newVal) => {
    if (newVal) {
        if (templates.value.length === 0) fetchTemplates()
        if (props.topic) {
            manualPrompt.value = `请为选题 "${props.topic.title}" 生成脚本。`
        }
    }
})

const copyScript = () => {
    navigator.clipboard.writeText(generatedScript.value)
    alert('脚本已复制！')
}
</script>

<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="opacity-0 translate-y-4 scale-95"
    enter-to-class="opacity-100 translate-y-0 scale-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="opacity-100 translate-y-0 scale-100"
    leave-to-class="opacity-0 translate-y-4 scale-95"
  >
    <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-8 bg-black/40 backdrop-blur-sm" @click.self="$emit('close')">
      <!-- Modal Content: 80% Screen -->
      <div class="bg-white rounded-2xl shadow-2xl w-[90%] h-[90%] md:w-[80%] md:h-[85%] flex flex-col overflow-hidden border border-slate-200 relative">
        
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
            <div class="flex items-center gap-3">
                <div class="p-2 bg-indigo-100 text-indigo-600 rounded-lg">
                    <FileText class="w-5 h-5" />
                </div>
                <div>
                    <h2 class="font-bold text-slate-800 text-lg">脚本生成台 (Workbench)</h2>
                    <p class="text-xs text-slate-500" v-if="topic">正在为 <span class="font-bold text-indigo-600">"{{ topic.title }}"</span> 创作</p>
                </div>
            </div>
            <button @click="$emit('close')" class="p-2 hover:bg-slate-100 rounded-full transition-colors">
                <X class="w-6 h-6 text-slate-400" />
            </button>
        </div>

        <!-- Body -->
        <div class="flex-1 flex overflow-hidden">
            <!-- Left: Configuration -->
            <div class="w-1/3 bg-slate-50 border-r border-slate-200 p-6 flex flex-col gap-6 overflow-y-auto">
                
                <div>
                    <label class="font-bold text-slate-700 text-sm mb-2 block">选择脚本模板</label>
                    <div class="flex flex-col gap-2">
                         <label 
                            v-for="t in templates" :key="t.id"
                            class="flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all"
                            :class="selectedTemplateId === t.id ? 'bg-indigo-50 border-indigo-500 shadow-sm' : 'bg-white border-slate-200 hover:border-indigo-300'"
                        >
                            <input type="radio" :value="t.id" v-model="selectedTemplateId" class="hidden">
                            <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0"
                                :class="selectedTemplateId === t.id ? 'border-indigo-600' : 'border-slate-300'">
                                <div v-if="selectedTemplateId === t.id" class="w-2 h-2 rounded-full bg-indigo-600"></div>
                            </div>
                            <span class="text-sm font-medium" :class="selectedTemplateId === t.id ? 'text-indigo-900' : 'text-slate-600'">{{ t.name }}</span>
                        </label>
                        <div v-if="templates.length === 0" class="text-xs text-slate-400 text-center py-4 bg-slate-100 rounded-lg dashed">
                            暂无模版，请去“脚本模版”页添加
                        </div>
                    </div>
                </div>

                <div class="flex-1 flex flex-col">
                    <label class="font-bold text-slate-700 text-sm mb-2 block">补充指令 (Prompt)</label>
                    <textarea 
                        v-model="manualPrompt"
                        class="flex-1 w-full bg-white border border-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:border-indigo-500 transition-colors resize-none mb-4"
                        placeholder="输入额外要求..."
                    ></textarea>
                    
                    <button 
                        @click="generateScript"
                        :disabled="isGenerating"
                        class="w-full py-3 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-indigo-200 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        <Sparkles class="w-5 h-5" :class="isGenerating ? 'animate-spin' : ''" />
                        {{ isGenerating ? 'AI 正在生成...' : '立即生成 (Mock)' }}
                    </button>
                </div>
            </div>

            <!-- Right: Editor -->
            <div class="flex-1 bg-white p-6 flex flex-col relative">
                <div v-if="!generatedScript" class="flex-1 flex flex-col items-center justify-center text-slate-300 gap-4">
                    <FileText class="w-16 h-16 opacity-20" />
                    <p>暂无脚本内容，请在左侧点击生成</p>
                </div>
                <div v-else class="flex-1 flex flex-col h-full">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Markdown Editor</span>
                        <button @click="copyScript" class="text-xs flex items-center gap-1 text-slate-500 hover:text-indigo-600">
                            <Copy class="w-3 h-3" /> 复制全文
                        </button>
                    </div>
                    <textarea 
                        v-model="generatedScript" 
                        class="flex-1 w-full h-full resize-none outline-none font-mono text-sm text-slate-700 leading-relaxed bg-transparent"
                    ></textarea>
                </div>
            </div>
        </div>
      </div>
    </div>
  </Transition>
</template>
