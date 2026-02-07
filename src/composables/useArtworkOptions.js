import { ref } from 'vue'
import axios from '@/axios'

export function useArtworkOptions() {
    const artists = ref([])
    const commissions = ref([])
    const loadingOptions = ref(false)

    const fetchArtists = async () => {
        try {
            const { data } = await axios.get('/artworks/artists/')
            artists.value = data
        } catch (e) {
            console.error(e)
        }
    }

    const fetchCommissions = async () => {
        try {
            const { data } = await axios.get('/artworks/commissions/')
            commissions.value = data
        } catch (e) {
            console.error(e)
        }
    }

    const fetchAll = async () => {
        loadingOptions.value = true
        try {
            await Promise.all([fetchArtists(), fetchCommissions()])
        } finally {
            loadingOptions.value = false
        }
    }

    return {
        artists,
        commissions,
        loadingOptions,
        fetchArtists,
        fetchCommissions,
        fetchAll
    }
}
