import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
})

// 요청마다 토큰 자동 첨부
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 401 시 로그인으로 리다이렉트
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──
export const login = (email, password) =>
  client.post('/auth/token', new URLSearchParams({ username: email, password }), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })

export const register = (data) =>
  client.post('/users/', data)

// ── Chatbot ──
export const sendMessage = (message) =>
  client.post('/chatbot/', { message })

// ── Bookmarks ──
export const getBookmarks = () =>
  client.get('/bookmarks/')

export const addBookmark = (restaurantId) =>
  client.post(`/bookmarks/restaurants/${restaurantId}`)

export const removeBookmark = (restaurantId) =>
  client.delete(`/bookmarks/restaurants/${restaurantId}`)

// ── Restaurants ──
export const getRestaurant = (id) =>
  client.get(`/restaurants/${id}`)

export default client
