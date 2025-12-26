import api from './api'

export const topicService = {
    // Get all saved topics
    async getTopics() {
        const res = await api.get('/topics')
        return res.data
    },

    // Save a topic to the library
    async saveTopic(topicData) {
        // Prepare data structure
        const payload = {
            title: topicData.title,
            source: topicData.source || 'Unknown',
            summary: topicData.aiSummary || topicData.description || '',
            url: topicData.url || '',
            originalId: topicData.id,
            savedAt: new Date().toISOString()
        }
        const res = await api.post('/topics', payload)
        return res.data
    },

    // Delete a topic
    async deleteTopic(id) {
        return api.delete(`/topics/${id}`)
    },

    // Batch delete
    async deleteTopics(ids) {
        return api.post('/topics/batch-delete', { ids })
    }
}
