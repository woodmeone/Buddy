import api from './api'

export const personaService = {
    async getPersonas() {
        // Backend returns list of PersonaRead (with source_configs)
        const res = await api.get('/personas')
        return res.data.map(transformFromBackend)
    },

    async getPersona(id) {
        const res = await api.get(`/personas/${id}`)
        return transformFromBackend(res.data)
    },

    async createPersona(data) {
        const payload = transformToBackend(data)
        const res = await api.post('/personas', payload)
        // Note: Creating persona usually doesn't create sources immediately in this simplified API,
        // or if it did, we'd need to handle that. 
        // Our current backend create_persona takes PersonaCreate which doesn't have source_configs.
        // So we might need to save persona first, then save sources?
        return transformFromBackend(res.data)
    },

    async updatePersona(id, data) {
        // 1. Update Persona Basic Info
        const payload = transformToBackend(data)
        const res = await api.put(`/personas/${id}`, payload)

        // 2. Sync Sources
        // Combine all lists into one flat list of SourceConfigs
        const allSources = [
            ...(data.bilibiliList || []).map(item => transformSourceToBackend(item, 'bilibili_user')),
            ...(data.rssList || []).map(item => transformSourceToBackend(item, 'rss_feed')),
            ...(data.hotSources || []).map(item => transformSourceToBackend(item, 'hot_list'))
        ]

        // Call the new endpoint
        await api.put(`/personas/${id}/sources`, allSources)

        // Re-fetch fresh data to ensure UI is in sync
        const fresh = await this.getPersona(id)
        return fresh
    },

    async deletePersona(id) {
        return api.delete(`/personas/${id}`)
    }
}

function transformSourceToBackend(item, type) {
    // Frontend item: {name, uid/url, enabled} + maybe id
    const config_data = {}
    if (type === 'bilibili_user') config_data.uid = item.uid
    if (type === 'rss_feed') config_data.url = item.url

    return {
        // id: item.id, // Omit ID to treat as new insert (Replace All strategy)
        type: type,
        name: item.name,
        enabled: item.enabled,
        views_threshold: parseInt(item.viewsThreshold || 0),
        config_data: config_data
    }
}

// Helpers
function transformFromBackend(p) {
    if (!p) return null
    // Flatten source_configs back to lists
    const bilibiliList = []
    const rssList = []
    const hotSources = []

    if (p.source_configs) {
        p.source_configs.forEach(sc => {
            if (sc.type === 'bilibili_user') bilibiliList.push(fromSourceConfig(sc))
            if (sc.type === 'rss_feed') rssList.push(fromSourceConfig(sc))
            if (sc.type === 'hot_list') hotSources.push(fromSourceConfig(sc))
        })
    }

    return {
        ...p,
        bilibiliList,
        rssList,
        hotSources
    }
}

function fromSourceConfig(sc) {
    // Backend: {id, type, config_data: {uid}, name, enabled}
    // Frontend Bilibili: {name, uid, enabled}
    const common = { id: sc.id, name: sc.name, enabled: sc.enabled, viewsThreshold: sc.views_threshold || 0 }
    if (sc.type === 'bilibili_user') return { ...common, uid: sc.config_data?.uid }
    if (sc.type === 'rss_feed') return { ...common, url: sc.config_data?.url }
    if (sc.type === 'hot_list') return { ...common } // Hot list usually just name + enabled
    return common
}

function transformToBackend(p) {
    // Only transforms basic fields for PersonaCreate/Update
    return {
        name: p.name,
        description: p.description,
        depth: p.depth,
        custom_prompt: p.customPrompt, // Note: backend snake_case 'custom_prompt' vs frontend camel 'customPrompt' ?
        // Check models.py: custom_prompt. 
        // Frontend useSettings mockData: customPrompt.
        // Need to ensure mapping.
        interests: p.interests
    }
}
