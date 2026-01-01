import api from './api'

export const dataService = {
    // Manual Sync
    async manualSync() {
        return api.post('/dashboard/sync', {}, { timeout: 60000 })
    },

    // Discovery Feed (Mock -> Backend Crawler)
    async getDiscoveryFeed(personaId, type = 'all') {
        if (!personaId) return []

        const params = { persona_id: personaId }
        if (type !== 'all') {
            params.type = type
        }

        const res = await api.get('/dashboard/feed', { params })
        return res.data
    },

    // Script Generation (Real Backend AI)
    async generateScript(topicId, templateId, personaId, extraPrompt = '') {
        const res = await api.post('/scripts/generate', {
            topic_id: topicId,
            template_id: templateId,
            persona_id: personaId,
            extra_prompt: extraPrompt
        })
        return res.data
    },

    // Script Recovery
    async getScriptForTopic(topicId) {
        try {
            const res = await api.get(`/scripts/topic/${topicId}`)
            return res.data
        } catch (e) {
            return null // Not found is fine
        }
    },

    // Metadata Generation (AI Title, Info, Tags)
    async generateMetadata(topicId, personaId, scriptContent = null) {
        const params = personaId ? { persona_id: personaId } : {}
        const payload = scriptContent ? { script_content: scriptContent } : {}
        const res = await api.post(`/topics/${topicId}/generate-metadata`, payload, { params })
        const topic = res.data
        return {
            ...topic, // Return full topic to keep data synced
            titles: topic.analysis_result?.ai_titles || [topic.ai_title],
            intros: topic.analysis_result?.script_intro ? [topic.analysis_result.script_intro] : [topic.ai_summary],
            tags: topic.analysis_result?.keywords || []
        }
    }
}

// Map exports to expected mockData style exports if needed by Views
// Note: DashboardView calls dataService.getDiscoveryFeed
