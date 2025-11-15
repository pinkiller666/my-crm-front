import { reactive, watchEffect } from 'vue'

const STORAGE_KEY = 'dev_flags_v1'

const state = reactive({
    useNewCards: false, // флажок "новый визуал карточек"
})

function loadFromStorage() {
    if (typeof window === 'undefined') {
        return
    }

    try {
        const raw = window.localStorage.getItem(STORAGE_KEY)

        if (!raw) {
            return
        }

        const parsed = JSON.parse(raw)

        if (parsed && typeof parsed.useNewCards === 'boolean') {
            state.useNewCards = parsed.useNewCards
        }
    } catch (error) {
        // тихо игнорируем
    }
}

function saveToStorage() {
    if (typeof window === 'undefined') {
        return
    }

    const payload = {
        useNewCards: state.useNewCards,
    }

    try {
        const json = JSON.stringify(payload)
        window.localStorage.setItem(STORAGE_KEY, json)
    } catch (error) {
        // тоже игнорируем
    }
}

loadFromStorage()

watchEffect(() => {
    saveToStorage()
})

export function useDevFlags() {
    function setUseNewCards(value) {
        state.useNewCards = Boolean(value)
    }

    return {
        devFlags: state,
        setUseNewCards,
    }
}
