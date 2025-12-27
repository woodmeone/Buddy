import api from './api'

export const dataService = {
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

    // Script Generation (Mock -> Backend)
    async generateScript(topicId, templateId) {
        const res = await api.post('/scripts/generate', {
            topic_id: topicId,
            template_id: templateId
        })
        return res.data
    },

    // Script Templates
    async getScriptTemplates() {
        const res = await api.get('/script-templates')
        return res.data
    }
}

// Map exports to expected mockData style exports if needed by Views
// Note: DashboardView calls dataService.getDiscoveryFeed
