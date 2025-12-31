import axios from 'axios'

const API_PREFIX = '/api/v1'

export const aiService = {
    /**
     * 获取 AI 智能挑选的选题
     * @param {number} personaId 人设ID
     * @returns {Promise<{items: Array<{topic: Object, reason: string}>, count: number}>}
     */
    async getAIPicks(personaId) {
        const params = {}
        if (personaId) params.persona_id = personaId

        const response = await axios.post(`${API_PREFIX}/ai/picks`, null, { params })
        return response.data
    }
}
