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
    },

    // Metadata Generation (Mock)
    async generateMetadata(scriptContent) {
        // 模拟延迟
        await new Promise(resolve => setTimeout(resolve, 1000));

        return {
            titles: [
                "爆款标题：揭秘行业内幕，这三点你必须知道",
                "新手必看！十分钟掌握核心技巧",
                "为什么99%的人都做错了？真相在这里"
            ],
            intros: [
                "大家好，我是WoodMe。今天我们来聊聊一个大家都很关心的话题...",
                "你是不是也经常遇到这个问题？别担心，今天这条视频就帮你彻底解决...",
                "这可能是今年最重要的一条视频，建议先收藏再看..."
            ],
            tags: [
                ["行业干货", "新手教程", "避坑指南"],
                ["实操演示", "经验分享", "职场进阶"],
                ["深度解析", "思维认知", "效率提升"]
            ]
        }
    }
}

// Map exports to expected mockData style exports if needed by Views
// Note: DashboardView calls dataService.getDiscoveryFeed
