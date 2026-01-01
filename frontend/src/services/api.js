import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import { mockPersonas, mockScripts, mockSavedTopics } from './mockData'

// Create Axios Instance
const api = axios.create({
    baseURL: '/api/v1',
    timeout: 120000
})

// --- MOCK SERVER SETUP (Toggle this based on env if needed) ---
// const isDev = import.meta.env.DEV
const isDev = false

if (isDev) {
    const mock = new MockAdapter(api, { delayResponse: 500 })

    // --- Personas ---
    mock.onGet('/personas').reply(200, mockPersonas)

    mock.onPost('/personas').reply(config => {
        const data = JSON.parse(config.data)
        const newPersona = { ...data, id: Date.now() } // Simple ID generation
        mockPersonas.push(newPersona)
        return [200, newPersona]
    })

    mock.onPut(/\/personas\/\d+/).reply(config => {
        const id = parseInt(config.url.split('/').pop())
        const data = JSON.parse(config.data)
        const index = mockPersonas.findIndex(p => p.id === id)
        if (index > -1) {
            mockPersonas[index] = { ...mockPersonas[index], ...data }
            return [200, mockPersonas[index]]
        }
        return [404]
    })

    mock.onDelete(/\/personas\/\d+/).reply(config => {
        const id = parseInt(config.url.split('/').pop())
        const index = mockPersonas.findIndex(p => p.id === id)
        if (index > -1) {
            mockPersonas.splice(index, 1)
            return [200]
        }
        return [404]
    })

    // --- Scripts ---
    mock.onGet('/script-templates').reply(200, mockScripts)

    mock.onPost('/script-templates').reply(config => {
        const data = JSON.parse(config.data)
        const newItem = { ...data, id: Date.now() }
        mockScripts.push(newItem)
        return [200, newItem]
    })

    mock.onPut(/\/script-templates\/\d+/).reply(config => {
        const id = parseInt(config.url.split('/').pop())
        const data = JSON.parse(config.data)
        const index = mockScripts.findIndex(p => p.id === id)
        if (index > -1) {
            mockScripts[index] = { ...mockScripts[index], ...data }
            return [200, mockScripts[index]]
        }
        return [404]
    })

    mock.onDelete(/\/script-templates\/\d+/).reply(config => {
        console.log('[Mock] DELETE request:', config.url)
        const id = parseInt(config.url.split('/').pop())
        console.log('[Mock] Parsing ID:', id)
        const index = mockScripts.findIndex(p => p.id === id)
        console.log('[Mock] Found index:', index)
        if (index > -1) {
            mockScripts.splice(index, 1)
            return [200]
        }
        return [404]
    })

    // --- Topics Library ---
    mock.onGet('/topics').reply(200, mockSavedTopics)

    mock.onPost('/topics').reply(config => {
        const data = JSON.parse(config.data)
        // Check for duplicate (Simulated)
        if (mockSavedTopics.some(t => t.title === data.title)) {
            return [409, { message: 'Topic already exists' }]
        }
        const newItem = { ...data, id: Date.now() }
        mockSavedTopics.unshift(newItem)
        return [200, newItem]
    })

    mock.onDelete(/\/topics\/\d+/).reply(config => {
        const id = parseInt(config.url.split('/').pop())
        const index = mockSavedTopics.findIndex(t => t.id === id)
        if (index > -1) {
            mockSavedTopics.splice(index, 1)
            return [200]
        }
        return [404]
    })

    mock.onPost('/topics/batch-delete').reply(config => {
        const { ids } = JSON.parse(config.data)
        const initialLength = mockSavedTopics.length
        // Filter out deleted items (modify array in place or reassign)
        // JS modules exported consts are read-only-ish for reassignment if imported this way, 
        // but array mutation works.
        const remaining = mockSavedTopics.filter(t => !ids.includes(t.id))
        mockSavedTopics.length = 0
        mockSavedTopics.push(...remaining)
        return [200, { deleted: initialLength - remaining.length }]
    })

    console.log('[Mock] API Mock Server initialized')
}

export default api
