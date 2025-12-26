<script setup>
import { ref } from 'vue'
import { User, Plus, Trash2, Edit2, Check, X, LogOut } from 'lucide-vue-next'
import { useSettings } from '../../composables/useSettings'
import { personaService } from '../../services/personaService'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])

const { personas, currentPersonaId, switchPersona, reloadPersonas } = useSettings()

const isEditing = ref(false)
const editingPersona = ref({})

// Start editing a persona
const startEdit = (persona) => {
    editingPersona.value = { ...persona }
    isEditing.value = true
}

// Create new persona
const createNew = () => {
    editingPersona.value = {
        name: '新人设',
        description: '',
        customPrompt: '',
        depth: 5,
        interests: [],
        bilibiliList: [],
        rssList: []
    }
    isEditing.value = true
}

// Save (Create/Update)
const save = async () => {
    try {
        if (editingPersona.value.id) {
            await personaService.updatePersona(editingPersona.value.id, editingPersona.value)
        } else {
            const newP = await personaService.createPersona(editingPersona.value)
            // If it's the first one or user want to switch to it immediately
            switchPersona(newP.id)
        }
        await reloadPersonas()
        isEditing.value = false
    } catch (e) {
        console.error(e)
        alert('保存失败')
    }
}

// Delete
const remove = async (id) => {
    if (!confirm('确定删除该人设吗？')) return
    try {
        await personaService.deletePersona(id)
        await reloadPersonas()
    } catch (e) {
        console.error(e)
    }
}

// Select/Switch
const select = (id) => {
    switchPersona(id)
    emit('close')
}
</script>

<template>
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0 scale-95"
    enter-to-class="opacity-100 scale-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-95"
  >
    <div v-if="isOpen" class="fixed top-20 left-64 ml-8 z-50 w-96 bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[600px]">
        
        <!-- Header -->
        <div class="px-5 py-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
            <h3 class="font-bold text-slate-800 flex items-center gap-2">
                <User class="w-5 h-5 text-indigo-600" />
                人设管理
            </h3>
            
            <div class="flex gap-2">
                 <button v-if="!isEditing" @click="createNew" class="p-1.5 hover:bg-slate-200 rounded text-slate-600" title="新建">
                    <Plus class="w-4 h-4" />
                </button>
                <button @click="$emit('close')" class="p-1.5 hover:bg-slate-200 rounded text-slate-400 hover:text-red-500">
                    <X class="w-4 h-4" />
                </button>
            </div>
        </div>

        <!-- List Mode -->
        <div v-if="!isEditing" class="flex-1 overflow-y-auto p-2 space-y-1">
             <div 
                v-for="p in personas" :key="p.id"
                class="group flex items-center justify-between p-3 rounded-lg cursor-pointer border hover:shadow-md transition-all"
                :class="currentPersonaId === p.id ? 'bg-indigo-50 border-indigo-200' : 'bg-white border-transparent hover:border-slate-200'"
                @click="select(p.id)"
             >
                <div class="flex items-center gap-3">
                    <div class="w-2 h-2 rounded-full" :class="currentPersonaId === p.id ? 'bg-indigo-600' : 'bg-slate-300'"></div>
                    <div>
                        <div class="font-bold text-sm text-slate-800">{{ p.name }}</div>
                        <div class="text-xs text-slate-400 truncate w-32">{{ p.description || '无描述' }}</div>
                    </div>
                </div>
                <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity" @click.stop>
                    <button @click="startEdit(p)" class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-white rounded shadow-sm border border-transparent hover:border-slate-100">
                        <Edit2 class="w-3 h-3" />
                    </button>
                    <!-- Don't verify delete last one for now, keeping it simple -->
                    <button v-if="personas.length > 1" @click="remove(p.id)" class="p-1.5 text-slate-400 hover:text-red-600 hover:bg-white rounded shadow-sm border border-transparent hover:border-slate-100">
                        <Trash2 class="w-3 h-3" />
                    </button>
                </div>
             </div>
        </div>

        <!-- Edit Mode -->
        <div v-else class="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50/50">
            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">名称</label>
                <input v-model="editingPersona.name" class="w-full text-sm border border-slate-200 rounded px-2 py-1.5 focus:border-indigo-500 outline-none bg-white" placeholder="例如：毒舌评论员" />
            </div>
             <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">描述</label>
                <input v-model="editingPersona.description" class="w-full text-sm border border-slate-200 rounded px-2 py-1.5 focus:border-indigo-500 outline-none bg-white" placeholder="简短描述用途..." />
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">核心 Prompt</label>
                <textarea v-model="editingPersona.customPrompt" class="w-full h-32 text-sm border border-slate-200 rounded px-2 py-1.5 focus:border-indigo-500 outline-none bg-white resize-none" placeholder="你是一个..."></textarea>
            </div>
        </div>

        <!-- Footer -->
        <div v-if="isEditing" class="p-4 border-t border-slate-100 bg-white flex justify-end gap-3">
             <button @click="isEditing = false" class="text-sm text-slate-500 hover:text-slate-800 px-3 py-2">取消</button>
             <button @click="save" class="text-sm bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold shadow-lg shadow-indigo-200 hover:bg-indigo-700">保存人设</button>
        </div>
    </div>
  </Transition>
</template>
