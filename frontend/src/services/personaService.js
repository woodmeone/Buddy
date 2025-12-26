import api from './api'

export const personaService = {
    async getPersonas() {
        const res = await api.get('/personas')
        return res.data
    },

    async createPersona(data) {
        const res = await api.post('/personas', data)
        return res.data
    },

    async updatePersona(id, data) {
        const res = await api.put(`/personas/${id}`, data)
        return res.data
    },

    async deletePersona(id) {
        return api.delete(`/personas/${id}`)
    }
}
