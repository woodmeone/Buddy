import { ref, computed, watch } from 'vue'
import { personaService } from '../services/personaService'

// Global State (Singleton pattern for composable)
const personas = ref([])
const currentPersonaId = ref(null)
const isLoading = ref(false)

const init = async () => {
    if (personas.value.length > 0) return // Already initialized

    isLoading.value = true
    try {
        const list = await personaService.getPersonas()
        personas.value = list
        if (list.length > 0) {
            // Restore last used persona or default to first
            const lastId = localStorage.getItem('buddy_last_persona_id')
            if (lastId && list.find(p => p.id === parseInt(lastId))) {
                currentPersonaId.value = parseInt(lastId)
            } else {
                currentPersonaId.value = list[0].id
            }
        }
    } catch (e) {
        console.error('Failed to load personas', e)
    } finally {
        isLoading.value = false
    }
}

// Auto-save watcher (Debounding recommended in real app, simplistic for now)
const saveCurrentPersona = async () => {
    if (!currentPersonaId.value) return
    const persona = personas.value.find(p => p.id === currentPersonaId.value)
    if (persona) {
        try {
            await personaService.updatePersona(persona.id, persona)
            console.log('Auto-saved persona:', persona.id)
        } catch (e) {
            console.error('Failed to save persona', e)
        }
    }
}

export function useSettings() {
    // Computed for the current persona object
    const currentPersona = computed(() => {
        return personas.value.find(p => p.id === currentPersonaId.value) || {}
    })

    const switchPersona = (id) => {
        currentPersonaId.value = id
        localStorage.setItem('buddy_last_persona_id', id)
    }

    const reloadPersonas = async () => {
        const list = await personaService.getPersonas()
        personas.value = list
        // Ensure current ID is still valid
        if (!list.find(p => p.id === currentPersonaId.value)) {
            currentPersonaId.value = list.length > 0 ? list[0].id : null
        }
    }

    // Initialize on first use
    init()

    return {
        isLoading,
        personas,
        currentPersonaId,
        currentPersona,
        switchPersona,
        reloadPersonas,
        saveCurrentPersona
    }
}
