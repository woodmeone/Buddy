import api from './api'

export const scriptService = {
    // Templates
    async getTemplates() {
        const res = await api.get('/script-templates')
        return res.data
    },

    async createTemplate(templateData) {
        const res = await api.post('/script-templates', templateData)
        return res.data
    },

    async updateTemplate(id, templateData) {
        const res = await api.put(`/script-templates/${id}`, templateData)
        return res.data
    },

    async deleteTemplate(id) {
        return api.delete(`/script-templates/${id}`)
    }
}
