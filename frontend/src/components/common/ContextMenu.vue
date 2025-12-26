<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
    visible: Boolean,
    x: Number,
    y: Number,
    menuItems: Array // [{ label: 'Name', action: () => {} }]
})

const emit = defineEmits(['close'])

const closeMenu = () => emit('close')

onMounted(() => {
    window.addEventListener('click', closeMenu)
})

onUnmounted(() => {
    window.removeEventListener('click', closeMenu)
})
</script>

<template>
    <div 
        v-if="visible"
        class="fixed z-50 bg-white rounded-lg shadow-xl border border-slate-100 py-1 w-32 overflow-hidden animate-in fade-in zoom-in-95 duration-100"
        :style="{ top: y + 'px', left: x + 'px' }"
        @click.stop
    >
        <button 
            v-for="(item, index) in menuItems" 
            :key="index"
            @click="item.action(); closeMenu()"
            class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-indigo-600 transition-colors cursor-pointer"
        >
            {{ item.label }}
        </button>
    </div>
</template>
