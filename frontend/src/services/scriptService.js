import api from './api'

export const scriptService = {
    // Templates
    async getTemplates() {
        const res = await api.get('/script-templates')
        // Map content_template -> template for UI
        return res.data.map(t => ({
            ...t,
            template: t.content_template
        }))
    },

    async createTemplate(templateData) {
        // Map template -> content_template for Backend
        const payload = {
            name: templateData.name,
            content_template: templateData.template,
            type: templateData.type || 'fast_paced'
        }
        const res = await api.post('/script-templates', payload)
        return { ...res.data, template: res.data.content_template }
    },

    async updateTemplate(id, templateData) {
        const payload = {
            name: templateData.name,
            content_template: templateData.template,
            type: templateData.type
        }
        const res = await api.put(`/script-templates/${id}`, payload)
        return { ...res.data, template: res.data.content_template }
    },

    async deleteTemplate(id) {
        return api.delete(`/script-templates/${id}`)
    }
}
