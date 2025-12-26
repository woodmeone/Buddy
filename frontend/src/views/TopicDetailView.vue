<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, ExternalLink, Share2, FileText, Code2, Tag } from 'lucide-vue-next'

const route = useRoute()
const topicId = route.params.id

// Mock Data
const topic = ref({
  id: topicId,
  title: 'Auto-GPT-Next: The New Automated Agent',
  source: 'GitHub',
  originUrl: 'https://github.com/example/auto-gpt-next',
  score: 98,
  labels: ['#AI Tool', '#Python Automation', '#High Potential'],
  summary: 'Auto-GPT-Next is a lightweight wrapper around GPT-4 that allows for recursive task execution. It has gained 5k stars in 24h.',
  analysis: {
    difficulty: 'Low (3 lines of code)',
    personaMatch: 'High. Matches "Tech for Beginners" and "Cutting Edge AI" interests.',
    viralityPotential: 'Very High. Automation tools are trending.',
    commercialValue: 'Medium. Good for affiliate links or course upsell.'
  },
  scriptDraft: ''
})

const isGenerating = ref(false)
const generatedScript = ref('')

const generateScript = () => {
  isGenerating.value = true
  setTimeout(() => {
    generatedScript.value = `# Video Script: Auto-GPT-Next\n\n**0-5s Hook**:\n(Screen: Matrix Code Rain)\n"Guys, are you still manually writing emails? This new GitHub repo just exploded..."\n\n**15-30s Demo**:\n(Screen: Terminal recording)\n"Watch this. Just type 'pip install auto-gpt-next' and boom..."\n\n**CTA**:\n"Link in bio for the full config!"`
    isGenerating.value = false
  }, 2000)
}

const pushToFeishu = () => {
  alert('Synced to Feishu Multidimensional Table!')
}
</script>

<template>
  <div class="p-8 max-w-5xl mx-auto">
    <!-- Back & Header -->
    <div class="mb-8">
      <RouterLink to="/" class="inline-flex items-center text-slate-500 hover:text-indigo-600 mb-4 transition">
        <ArrowLeft class="w-4 h-4 mr-1" /> Back to Dashboard
      </RouterLink>
      
      <div class="flex justify-between items-start">
        <h1 class="text-3xl font-bold text-slate-800 leading-tight w-2/3">{{ topic.title }}</h1>
        <div class="flex items-center gap-3">
          <a :href="topic.originUrl" target="_blank" class="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition flex items-center gap-2 font-medium">
            <ExternalLink class="w-4 h-4" /> Source
          </a>
          <button @click="pushToFeishu" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2 font-medium">
            <Share2 class="w-4 h-4" /> Sync to Feishu
          </button>
        </div>
      </div>
      
      <div class="flex items-center gap-3 mt-4">
        <span class="px-3 py-1 bg-slate-900 text-white text-xs font-bold rounded-full">{{ topic.source }}</span>
        <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">Score: {{ topic.score }}</span>
        <div class="flex gap-2 ml-4">
          <span v-for="label in topic.labels" :key="label" class="text-slate-500 text-sm flex items-center">
            <Tag class="w-3 h-3 mr-1" /> {{ label }}
          </span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Left: Analysis -->
      <div class="lg:col-span-2 space-y-6">
        <!-- AI Insight Card -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="p-2 bg-indigo-100 rounded-lg text-indigo-600">
              <Code2 class="w-5 h-5" />
            </div>
            <h2 class="text-xl font-bold text-slate-800">AI Analysis</h2>
          </div>
          
          <div class="space-y-4">
            <div class="p-4 bg-slate-50 rounded-lg border border-slate-100">
              <h3 class="font-medium text-slate-900 mb-1">Summary</h3>
              <p class="text-slate-600 leading-relaxed">{{ topic.summary }}</p>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div class="p-4 bg-slate-50 rounded-lg border border-slate-100">
                <h3 class="font-medium text-slate-900 mb-1">Difficulty</h3>
                <p class="text-slate-600">{{ topic.analysis.difficulty }}</p>
              </div>
              <div class="p-4 bg-slate-50 rounded-lg border border-slate-100">
                <h3 class="font-medium text-slate-900 mb-1">Persona Match</h3>
                <p class="text-slate-600">{{ topic.analysis.personaMatch }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Script Generator -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="p-2 bg-purple-100 rounded-lg text-purple-600">
                <FileText class="w-5 h-5" />
              </div>
              <h2 class="text-xl font-bold text-slate-800">Content Script</h2>
            </div>
            <button @click="generateScript" :disabled="isGenerating"
              class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
              <span v-if="isGenerating" class="animate-spin">⟳</span>
              {{ isGenerating ? 'Generating...' : 'Generate Script' }}
            </button>
          </div>

          <div v-if="generatedScript" class="mt-4">
             <textarea class="w-full h-64 p-4 bg-slate-50 border border-slate-200 rounded-lg font-mono text-sm focus:ring-2 focus:ring-purple-500 focus:outline-none" v-model="generatedScript"></textarea>
          </div>
          <div v-else class="h-32 bg-slate-50 rounded-lg border border-dashed border-slate-300 flex items-center justify-center text-slate-400">
            Click generate to draft a script...
          </div>
        </div>
      </div>

      <!-- Right: Metadata / Actions -->
      <div class="space-y-6">
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
          <h3 class="font-bold text-slate-800 mb-4">Topic Actions</h3>
          <div class="space-y-3">
            <button class="w-full py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition">Mark as Rejected</button>
            <button class="w-full py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition">Save for later</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
