export const mockPersonas = [
    {
        id: 1,
        name: 'Default (通用)',
        description: '系统默认人设',
        customPrompt: '你是一个充满热情的技术博主，擅长用通俗易懂的语言解释复杂的技术概念。',
        depth: 7,
        interests: ['Python', 'AI', 'Vue3', 'ProJuss'],
        hotSources: [
            { id: 'zhihu', name: '知乎热榜', enabled: true },
            { id: 'weibo', name: '微博热搜', enabled: true }
        ],
        bilibiliList: [{ name: '竞品A', uid: '12345678', enabled: true }],
        rssList: [{ name: '阮一峰', url: 'http://www.ruanyifeng.com/blog/atom.xml', enabled: true }]
    },
    {
        id: 2,
        name: '犀利点评',
        description: '专门用于竞品分析和吐槽',
        customPrompt: '你是一个犀利的互联网评论员，目光如炬，善于发现产品的痛点和逻辑漏洞。说话风格一针见血，不留情面。',
        depth: 9,
        interests: ['产品分析', '商业模式', '吐槽'],
        bilibiliList: [],
        rssList: []
    }
]

export const mockScripts = [
    {
        id: 1,
        name: '⚡ 快节奏口播',
        template: `# 脚本: {{topic.title}}\n\n## 00:00 - 00:05 开场 (Hook)\n画面：快节奏剪辑\n台词：你也听说 {{topic.title}} 了吗？这可能是今年最炸裂的更新！\n\n## 00:05 - 00:30 核心观点\n画面：演示核心功能\n台词：...`
    },
    {
        id: 2,
        name: '📖 深度故事向',
        template: `# 脚本: {{topic.title}}\n\n## 起因\n很多年前，我们就在想...\n\n## 经过\n直到今天，{{topic.title}} 的出现改变了一切。\n\n## 结果\n...`
    }
]

export const mockSavedTopics = [
    {
        id: 901,
        title: 'Cursor vs Copilot: 终极对决',
        source: 'Twitter',
        savedAt: '2023-12-25T10:00:00Z',
        summary: '对比了两个 AI 编程助手的优缺点，Cursor 在上下文理解上更胜一筹。'
    },
    {
        id: 902,
        title: '如何评价 Apple Vision Pro 的销量？',
        source: 'Zhihu',
        savedAt: '2023-12-26T09:30:00Z',
        summary: '销量惨淡，但生态正在慢慢构建...'
    }
]
