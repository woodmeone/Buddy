<script setup>
import { ref, computed, onMounted } from 'vue'
import { BookMarked, Search, Trash2, Filter, MoreHorizontal, Sparkles } from 'lucide-vue-next'
import { topicService } from '../services/topicService'
import ContextMenu from '../components/common/ContextMenu.vue'
import ScriptWorkbenchModal from '../components/workbench/ScriptWorkbenchModal.vue'

const topics = ref([])
const isLoading = ref(true)
const searchQuery = ref('')
const selectedIds = ref([])

// Load Data
const fetchTopics = async () => {
    isLoading.value = true
    try {
        topics.value = await topicService.getTopics()
    } catch (e) {
        console.error(e)
    } finally {
        isLoading.value = false
    }
}

// Filtering
const filteredTopics = computed(() => {
    if (!searchQuery.value) return topics.value
    const q = searchQuery.value.toLowerCase()
    return topics.value.filter(t => 
        t.title.toLowerCase().includes(q) || 
        t.summary?.toLowerCase().includes(q) ||
        t.source?.toLowerCase().includes(q)
    )
})

// Bulk Selection
const toggleSelect = (id) => {
    if (selectedIds.value.includes(id)) {
        selectedIds.value = selectedIds.value.filter(i => i !== id)
    } else {
        selectedIds.value.push(id)
    }
}

const toggleSelectAll = () => {
    if (selectedIds.value.length === filteredTopics.value.length) {
        selectedIds.value = []
    } else {
        selectedIds.value = filteredTopics.value.map(t => t.id)
    }
}

const deleteSelected = async () => {
    if (!selectedIds.value.length) return
    if (!confirm(`确定删除选中的 ${selectedIds.value.length} 个选题吗？`)) return
    
    try {
        await topicService.deleteTopics(selectedIds.value)
        selectedIds.value = []
        await fetchTopics()
    } catch (e) {
        console.error(e)
    }
}

// Custom right click logic
const showContextMenu = ref(false)
const contextMenuPos = ref({ x: 0, y: 0 })
const activeTopic = ref(null)

const showWorkbench = ref(false)

const openWorkbench = () => {
    showWorkbench.value = true
}

const deleteSingle = async () => {
    if (!activeTopic.value) return
    if (!confirm('确定删除该选题吗？')) return
    await topicService.deleteTopic(activeTopic.value.id)
    await fetchTopics()
}

const handleContextMenu = (e, topic) => {
    e.preventDefault()
    showContextMenu.value = true
    contextMenuPos.value = { x: e.clientX, y: e.clientY }
    activeTopic.value = topic
}

// Context Menu Items
const menuItems = [
    { label: '🚀 再探 (Deep Dive)', action: openWorkbench },
    { label: '🗑️ 删除选题', action: deleteSingle }
]

onMounted(fetchTopics)
</script>

<template>
    <div class="h-full flex flex-col gap-6" @click="showContextMenu = false">
        <!-- Header -->
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-2xl font-bold text-slate-800 flex items-center gap-2">
                     <div class="p-1.5 bg-indigo-500 rounded-lg">
                        <BookMarked class="w-6 h-6 text-white" />
                    </div>
                    选题库
                    <span class="text-sm font-normal text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full ml-2">{{ topics.length }}</span>
                </h1>
                <p class="text-slate-500 text-sm mt-1">收藏的灵感与潜在选题</p>
            </div>
            
             <div v-if="selectedIds.length > 0" class="flex items-center gap-3 animate-in fade-in slide-in-from-right-4 duration-300">
                <span class="text-sm font-bold text-slate-600">已选 {{ selectedIds.length }} 项</span>
                <button @click="deleteSelected" class="bg-red-50 text-red-600 hover:bg-red-100 px-4 py-2 rounded-lg font-bold flex items-center gap-2 transition-colors">
                    <Trash2 class="w-4 h-4" /> 批量删除
                </button>
            </div>
        </div>

        <!-- Filter Bar -->
        <div class="flex items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
             <div class="relative flex-1">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input 
                    v-model="searchQuery" 
                    placeholder="搜索选题标题、来源、摘要..." 
                    class="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:border-indigo-500 transition-colors"
                />
             </div>
             <button class="flex items-center gap-2 px-3 py-2 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 text-sm font-medium">
                 <Filter class="w-4 h-4" /> 筛选
             </button>
        </div>

        <!-- List -->
        <div v-if="isLoading" class="flex-1 flex items-center justify-center">
            <div class="animate-spin w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full"></div>
        </div>

        <div v-else-if="filteredTopics.length === 0" class="flex-1 flex flex-col items-center justify-center text-slate-400 gap-4">
            <BookMarked class="w-16 h-16 opacity-20" />
            <p>暂无符合条件的选题</p>
        </div>

        <div v-else class="flex-1 overflow-y-auto bg-white rounded-xl border border-slate-200 shadow-sm">
             <table class="w-full text-left">
                <thead class="bg-slate-50 border-b border-slate-200 sticky top-0 z-10">
                    <tr>
                        <th class="p-4 w-12 text-center">
                             <input type="checkbox" 
                                :checked="selectedIds.length === filteredTopics.length"
                                @change="toggleSelectAll"
                                class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer" 
                             />
                        </th>
                        <th class="p-4 text-xs font-bold text-slate-500 uppercase">标题 / 摘要</th>
                        <th class="p-4 text-xs font-bold text-slate-500 uppercase w-32">来源</th>
                        <th class="p-4 text-xs font-bold text-slate-500 uppercase w-48">收藏时间</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    <tr v-for="topic in filteredTopics" :key="topic.id" 
                        class="group hover:bg-indigo-50/30 transition-colors cursor-default"
                        @contextmenu="(e) => handleContextMenu(e, topic)"
                    >
                        <td class="p-4 text-center">
                            <input type="checkbox" 
                                :checked="selectedIds.includes(topic.id)"
                                @change="toggleSelect(topic.id)"
                                class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                            />
                        </td>
                        <td class="p-4">
                            <div class="font-bold text-slate-800 mb-1 group-hover:text-indigo-700 transition-colors">{{ topic.title }}</div>
                            <div class="text-xs text-slate-400 line-clamp-2 max-w-xl">{{ topic.summary }}</div>
                        </td>
                        <td class="p-4">
                            <span class="inline-flex items-center px-2 py-1 rounded bg-slate-100 text-xs font-medium text-slate-600">
                                {{ topic.source }}
                            </span>
                        </td>
                        <td class="p-4 text-sm text-slate-500 font-mono">
                            {{ new Date(topic.savedAt).toLocaleDateString() }}
                        </td>
                    </tr>
                </tbody>
             </table>
        </div>

        <!-- Modals -->
        <ContextMenu 
            :visible="showContextMenu" 
            :x="contextMenuPos.x" 
            :y="contextMenuPos.y" 
            :menuItems="menuItems"
            @close="showContextMenu = false"
        />

        <ScriptWorkbenchModal 
            :isOpen="showWorkbench"
            :topic="activeTopic"
            @close="showWorkbench = false"
        />
    </div>
</template>
