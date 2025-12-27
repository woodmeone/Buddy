import api from './api'

export const topicService = {
    // 获取选题列表 (Mock -> Backend)
    async getTopics(status = 'all') {
        const res = await api.get('/topics')
        // ... (rest is same)
        let topics = res.data
        if (status !== 'all') {
            topics = topics.filter(t => t.status === status)
        }
        return topics
    },

    // 获取单个选题
    async getTopic(id) {
        // Backend API implements GET /topics/{id}
        const res = await api.get(`/topics/${id}`)
        return res.data
    },

    // 删除选题
    async deleteTopic(id) {
        return api.delete(`/topics/${id}`)
    },

    // 批量删除
    async batchDelete(ids) {
        return api.post('/topics/batch-delete', ids)
    },

    // 保存选题 (从发现页添加到选题库)
    // Frontend checks duplications usually? Or backend?
    // Backend API create_topic just adds.
    async createTopic(topicData) {
        return api.post('/topics', topicData)
    },

    async updateTopicStatus(id, status) {
        return api.put(`/topics/${id}`, { status })
    }
}
