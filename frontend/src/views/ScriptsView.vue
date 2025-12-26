<script setup>
import { ref, onMounted } from 'vue'
// Fix: ensure correct imports and setup
console.log('ScriptsView loaded')
import { Plus, Trash2, Edit2, Save, X, FileText } from 'lucide-vue-next'
import { scriptService } from '../services/scriptService'

const scripts = ref([])
const isLoading = ref(true)
const isEditing = ref(false)

const currentScript = ref({
    name: '',
    template: ''
})

const fetchScripts = async () => {
    isLoading.value = true
    try {
        scripts.value = await scriptService.getTemplates()
    } catch (e) {
        console.error(e)
    } finally {
        isLoading.value = false
    }
}

const openEditor = (script = null) => {
    if (script) {
        currentScript.value = { ...script }
    } else {
        currentScript.value = { name: '', template: '' }
    }
    console.log('Opening editor with:', currentScript.value)
    isEditing.value = true
}

const saveScript = async () => {
    if (!currentScript.value.name) return
    
    try {
        if (currentScript.value.id) {
            await scriptService.updateTemplate(currentScript.value.id, currentScript.value)
        } else {
            await scriptService.createTemplate(currentScript.value)
        }
        await fetchScripts()
        isEditing.value = false
    } catch (e) {
        console.error(e)
    }
}

const deleteScript = async (id) => {
    console.log('deleteScript called with ID:', id)
    if (!confirm('确认删除该模版吗？')) {
        console.log('Delete cancelled')
        return
    }
    try {
        console.log('Sending delete request...')
        await scriptService.deleteTemplate(id)
        console.log('Delete request success, fetching scripts...')
        await fetchScripts()
    } catch (e) {
        console.error('Delete failed:', e)
    }
}

onMounted(fetchScripts)
</script>

<template>
    <div class="h-full flex flex-col gap-6">
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
                    <div class="p-1.5 bg-indigo-500 rounded-lg">
                        <FileText class="w-6 h-6 text-white" />
                    </div>
                    脚本模版库
                </h1>
                <p class="text-slate-500 text-sm mt-1">管理你的口播、长视频脚本结构</p>
            </div>
            <button @click.stop="openEditor()" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all z-10 cursor-pointer">
                <Plus class="w-4 h-4" /> 新建模版
            </button>
        </div>

        <div v-if="isLoading" class="flex-1 flex items-center justify-center">
             <div class="animate-spin w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full"></div>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="script in scripts" :key="script.id" class="group bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden">
                <div class="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2 z-20">
                    <button @click.stop="openEditor(script)" class="p-2 text-slate-400 hover:text-indigo-600 bg-slate-50 hover:bg-indigo-50 rounded-lg transition-colors cursor-pointer shadow-sm border border-slate-200">
                        <Edit2 class="w-4 h-4" />
                    </button>
                    <button @click.stop="deleteScript(script.id)" class="p-2 text-slate-400 hover:text-red-600 bg-slate-50 hover:bg-red-50 rounded-lg transition-colors cursor-pointer shadow-sm border border-slate-200">
                        <Trash2 class="w-4 h-4" />
                    </button>
                </div>
                
                <div class="flex items-center gap-3 mb-4">
                    <div class="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-lg">
                        {{ script.name.charAt(0) }}
                    </div>
                    <div>
                        <h3 class="font-bold text-slate-700">{{ script.name }}</h3>
                        <p class="text-xs text-slate-400 font-mono">ID: {{ script.id }}</p>
                    </div>
                </div>
                <div class="bg-slate-50 rounded-lg p-3 text-xs text-slate-500 font-mono h-24 overflow-hidden border border-slate-100">
                    {{ script.template }}
                </div>
            </div>
        </div>

        <!-- Editor Modal -->
        <div v-if="isEditing" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
            <div class="bg-white rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
                <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
                    <h3 class="font-bold text-lg text-slate-800">{{ currentScript.id ? '编辑模版' : '新建模版' }}</h3>
                    <button @click="isEditing = false" class="text-slate-400 hover:text-slate-600">
                        <X class="w-6 h-6" />
                    </button>
                </div>
                
                <div class="p-6 flex-1 overflow-y-auto space-y-4">
                    <div>
                        <label class="block text-sm font-bold text-slate-700 mb-2">模版名称</label>
                        <input v-model="currentScript.name" class="w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-indigo-500" placeholder="例如：快节奏口播" />
                    </div>
                    <div class="flex-1 flex flex-col min-h-[300px]">
                        <label class="block text-sm font-bold text-slate-700 mb-2">
                            模版内容 (Markdown)
                            <span class="font-normal text-slate-400 ml-2" v-pre>支持 {{topic.title}} 等变量</span>
                        </label>
                        <textarea v-model="currentScript.template" class="flex-1 w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-indigo-500 font-mono text-sm resize-none bg-slate-50" placeholder="# 脚本结构..."></textarea>
                    </div>
                </div>

                <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
                    <button @click="isEditing = false" class="px-4 py-2 rounded-lg text-slate-600 hover:bg-slate-200 font-medium">取消</button>
                    <button @click="saveScript" class="px-6 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 font-medium flex items-center gap-2">
                        <Save class="w-4 h-4" /> 保存
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
